import streamlit as st
import numpy as np
import plotly.graph_objects as go
import graphviz
from datetime import datetime
import re

# ==========================================
# CONFIGURACIÓN
# ==========================================
st.set_page_config(page_title="Diseño P&ID: El Fermentador", layout="wide")

ASIGNATURA = "Control e Instrumentación de Procesos Químicos"
AUTOR = "José Joaquín González Cortés"
LICENCIA = "CC BY-NC-SA 4.0"

# ==========================================
# FUNCIONES LÓGICAS Y MATEMÁTICAS
# ==========================================
def validar_isa(tag, esperado):
    """Valida si el alumno ha introducido la etiqueta ISA correcta."""
    tag = tag.strip().upper()
    if not tag: return False, "Vacío"
    if tag.startswith(esperado): return True, tag
    return False, tag

def simular_dinamica(conexion):
    """Simula el proceso. Falla si la conexión es directa (Lazo Simple)."""
    t = np.linspace(0, 100, 200)
    T_ferm = np.ones_like(t) * 37.0
    T_cam = np.ones_like(t) * 20.0
    
    for i in range(10, len(t)-1):
        dt = t[i] - t[i-1]
        perturbacion = 8.0 if t[i] > 20 else 0.0 # Crecimiento bacteriano brusco
        
        # Tiempo muerto severo en el fermentador
        error = 37.0 - (T_ferm[i-8] if i > 8 else T_ferm[i]) 
        
        if conexion == "Directo a la Válvula de Refrigeración (Lazo Simple)":
            u = 20.0 - (1.5 * error) # Sintonía agresiva que causará inestabilidad
        else: # Cascada
            sp_cam = 20.0 - (3.5 * error)
            u = 20.0 - (5.0 * (sp_cam - T_cam[i]))
            
        u = np.clip(u, 5, 40)
        T_cam[i+1] = T_cam[i] + ((u - T_cam[i])/5.0) * dt
        T_ferm[i+1] = T_ferm[i] + ((T_cam[i] + perturbacion - T_ferm[i])/15.0) * dt
        
    return t, T_ferm, T_cam

# ==========================================
# INTERFAZ DE USUARIO
# ==========================================
st.title("🧩 Reto de Ingeniería: Cableado P&ID")
st.caption(f"**Asignatura:** {ASIGNATURA} | **Autor:** {AUTOR} | **Norma:** ISA-5.1")

with st.expander("📖 Especificaciones del Proyecto (Leer antes de diseñar)", expanded=True):
    st.markdown("""
    **Misión:** Diseñar el lazo de control térmico de un fermentador continuo.
    * **Restricción Técnica:** La sonda de temperatura del fermentador está encapsulada y presenta un **gran tiempo muerto**.
    * **Acción Requerida:** Etiquetar los instrumentos según la norma ISA-5.1 y decidir el enrutamiento de las señales eléctricas (4-20mA). Un mal diseño provocará la pérdida del cultivo bacteriano.
    """)

tab_diseno, tab_simulacion, tab_informe = st.tabs(["🛠️ 1. Mesa de Diseño", "📈 2. Prueba de Estrés", "📥 3. Informe"])

# --- TAB 1: MESA DE DISEÑO ---
with tab_diseno:
    st.header("Especificación de Instrumentos y Enrutamiento")
    
    # Usamos un formulario para que el alumno piense todo antes de ver el resultado
    with st.form("form_diseno"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Lazo Principal (Fermentador)")
            tag_sensor1 = st.text_input("1. Etiqueta del Sensor/Transmisor de Temperatura:", placeholder="Ej: TT-101")
            tag_controlador1 = st.text_input("2. Etiqueta del Controlador Maestro:", placeholder="Ej: TC-101")
            
            st.subheader("Decisión de Enrutamiento")
            conexion = st.radio(
                "3. ¿A dónde enviamos la salida (Output) del Controlador Maestro?",
                ["Directo a la Válvula de Refrigeración (Lazo Simple)", 
                 "Al SetPoint de un Controlador Esclavo (Control en Cascada)"]
            )
            
        with col2:
            st.subheader("Lazo Secundario (Solo si aplica)")
            tag_sensor2 = st.text_input("4. Sensor de Tº en la Camisa (Si aplica):", placeholder="Ej: TT-102")
            tag_controlador2 = st.text_input("5. Controlador Esclavo (Si aplica):", placeholder="Ej: TC-102")
            
        submit_button = st.form_submit_button(label="Construir Arquitectura P&ID")

    # Si el alumno ha pulsado el botón, evaluamos y dibujamos
    if submit_button:
        st.divider()
        st.subheader("Análisis de tu Diseño")
        
        # Validaciones
        v_s1, t_s1 = validar_isa(tag_sensor1, "TT")
        v_c1, t_c1 = validar_isa(tag_controlador1, "TC")
        
        errores_isa = 0
        if not v_s1: st.error(f"❌ Error ISA: Un sensor de temperatura no se llama '{t_s1}'. Debería empezar por 'TT'."); errores_isa += 1
        if not v_c1: st.error(f"❌ Error ISA: El controlador maestro no se llama '{t_c1}'. Debería empezar por 'TC'."); errores_isa += 1
        
        if conexion == "Al SetPoint de un Controlador Esclavo (Control en Cascada)":
            v_s2, t_s2 = validar_isa(tag_sensor2, "TT")
            v_c2, t_c2 = validar_isa(tag_controlador2, "TC")
            if not v_s2: st.error(f"❌ Error ISA en lazo esclavo: Sonda incorrecta '{t_s2}'."); errores_isa += 1
            if not v_c2: st.error(f"❌ Error ISA en lazo esclavo: Controlador incorrecto '{t_c2}'."); errores_isa += 1
        
        if errores_isa == 0:
            st.success("✅ Nomenclatura ISA-5.1 Correcta. Generando diagrama...")
            
        # DIBUJO DEL GRAFO CON GRAPHVIZ (Incluso si hay errores, dibujamos lo que ha puesto para que vea su fallo)
        dot = graphviz.Digraph(engine='dot')
        dot.attr(rankdir='LR', nodesep='0.8', ranksep='1.0')
        
        dot.node('F', 'Fermentador', shape='box', style='filled', fillcolor='#f0f2f6')
        dot.node('C', 'Camisa', shape='box', style='filled', fillcolor='#dbe4f0')
        dot.node('S1', t_s1 if tag_sensor1 else '???', shape='circle')
        dot.node('C1', t_c1 if tag_controlador1 else '???', shape='circle')
        
        dot.edge('F', 'S1', style='solid')
        dot.edge('S1', 'C1', style='dashed')
        
        if conexion == "Directo a la Válvula de Refrigeración (Lazo Simple)":
            dot.node('V', 'TV', shape='circle', style='filled', fillcolor='#ffcccc')
            dot.edge('C1', 'V', style='dashed', label='Control Directo', color='red')
            dot.edge('V', 'C', style='solid')
        else:
            dot.node('S2', t_s2 if tag_sensor2 else '???', shape='circle')
            dot.node('C2', t_c2 if tag_controlador2 else '???', shape='circle')
            dot.node('V', 'TV', shape='circle', style='filled', fillcolor='#ffcccc')
            
            dot.edge('C1', 'C2', style='dashed', label='SetPoint', color='blue', penwidth='2')
            dot.edge('C', 'S2', style='solid')
            dot.edge('S2', 'C2', style='dashed')
            dot.edge('C2', 'V', style='dashed')
            dot.edge('V', 'C', style='solid')
            
        st.graphviz_chart(dot, use_container_width=True)
        st.session_state['conexion'] = conexion # Guardamos la decisión para la pestaña 2

# --- TAB 2: SIMULACIÓN ---
with tab_simulacion:
    st.header("Prueba de Estrés del Sistema")
    if 'conexion' not in st.session_state:
        st.info("⚠️ Primero debes construir tu arquitectura en la Pestaña 1 y pulsar el botón.")
    else:
        st.write("Simulando una perturbación exotérmica (multiplicación bacteriana rápida)...")
        
        t, T_ferm, T_cam = simular_dinamica(st.session_state['conexion'])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t, y=T_ferm, name="Tº Fermentador", line=dict(color='#d62728', width=3)))
        fig.add_trace(go.Scatter(x=t, y=T_cam, name="Tº Camisa", line=dict(color='#1f77b4', dash='dash')))
        fig.add_hline(y=37.0, line_dash="dot", line_color="green", annotation_text="Punto de Operación (37ºC)")
        
        # Evaluar si ha explotado (T > 42ºC mata el cultivo)
        max_temp = np.max(T_ferm)
        if max_temp > 42.0:
            fig.add_hrect(y0=42, y1=50, fillcolor="red", opacity=0.3, layer="below", annotation_text="ZONA LETAL (>42ºC)")
            st.error(f"🚨 **¡CATASTROFE!** La temperatura alcanzó los {max_temp:.1f}ºC. El cultivo bacteriano ha muerto. Tu diseño no ha podido compensar el tiempo muerto del sensor. Vuelve a la mesa de diseño e implementa una estrategia avanzada.")
        else:
            st.success(f"✅ **¡PROCESO ESTABLE!** La temperatura máxima fue de {max_temp:.1f}ºC. El lazo esclavo absorbió la perturbación a tiempo.")

        fig.update_layout(xaxis_title="Tiempo (min)", yaxis_title="Temperatura (ºC)", yaxis_range=[15, 50])
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 3: INFORME ---
with tab_informe:
    st.header("Auditoría del Diseño")
    nombre = st.text_input("Firma del Ingeniero/a:")
    
    if nombre and 'conexion' in st.session_state:
        exito = "SATISFACTORIO" if np.max(T_ferm) <= 42.0 else "FALLIDO (Cultivo destruido)"
        
        informe = f"""=======================================================
REPORTE DE AUDITORÍA P&ID
Asignatura: {ASIGNATURA}
Profesor: {AUTOR}
=======================================================
INGENIERO DISEÑADOR: {nombre}
FECHA: {datetime.now().strftime("%d/%m/%Y %H:%M")}

ARQUITECTURA DISEÑADA:
- Enrutamiento: {st.session_state['conexion']}

RESULTADO DE LA PRUEBA DE ESTRÉS:
- Estado del Sistema: {exito}
- Temperatura Máxima Alcanzada: {np.max(T_ferm):.1f} ºC

OBSERVACIONES:
El diseño de lazos en procesos con alto tiempo muerto 
requiere obligatoriamente estrategias de control avanzado 
(Cascada) para mantener la integridad operativa.
======================================================="""
        st.text_area("Borrador del Informe:", informe, height=300)
        st.download_button("💾 Exportar Certificado (.txt)", data=informe, file_name=f"Auditoria_{nombre.replace(' ', '_')}.txt")
