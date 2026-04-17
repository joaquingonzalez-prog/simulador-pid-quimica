import streamlit as st
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# CONFIGURACIÓN Y METADATOS
# ==========================================
st.set_page_config(page_title="Diseño de Lazos de Control", layout="wide")

ASIGNATURA = "Control e Instrumentación de Procesos Químicos"
AUTOR = "José Joaquín González Cortés"
LICENCIA = "CC BY-NC-SA 4.0"

# ==========================================
# LÓGICA DE SIMULACIÓN (CASCADA VS SIMPLE)
# ==========================================
def simular_temperatura(estrategia):
    """
    Simula la respuesta térmica del fermentador ante una perturbación exotérmica.
    Usa un modelo simplificado de diferencias finitas (Euler).
    """
    t = np.linspace(0, 100, 200)
    T_fermentador = np.zeros_like(t)
    T_camisa = np.zeros_like(t)
    
    # Parámetros del proceso
    tau_camisa = 5.0
    tau_fermentador = 15.0
    retardo = 5  # Índices de retardo en la medida
    
    # Setpoint y Perturbación
    SP = 37.0
    T_fermentador[0:10] = SP
    T_camisa[0:10] = 20.0
    
    # PID Variables
    error_integral_master = 0
    error_integral_slave = 0
    
    for i in range(10, len(t)-1):
        dt = t[i] - t[i-1]
        
        # Perturbación exotérmica en t=20
        perturbacion = 5.0 if t[i] > 20 else 0.0
        
        # Medida con tiempo muerto
        T_medida = T_fermentador[i-retardo] if i > retardo else T_fermentador[i]
        
        error_master = SP - T_medida
        error_integral_master += error_master * dt
        
        if estrategia == "Lazo Simple (Feedback)":
            # El controlador maestro mueve directamente la válvula de agua fría
            u_valvula = 20.0 - (2.0 * error_master + 0.5 * error_integral_master)
        else: # Cascada
            # El maestro pide una temperatura de camisa (Setpoint esclavo)
            SP_camisa = 20.0 - (3.0 * error_master + 0.8 * error_integral_master)
            
            # El esclavo controla la camisa (sin retardo)
            error_slave = SP_camisa - T_camisa[i]
            error_integral_slave += error_slave * dt
            u_valvula = 20.0 - (5.0 * error_slave + 1.0 * error_integral_slave)
            
        # Saturación de la válvula (0 a 100% de enfriamiento)
        u_valvula = np.clip(u_valvula, 5.0, 40.0)
        
        # Dinámica de la camisa y el fermentador
        dT_camisa = (u_valvula - T_camisa[i]) / tau_camisa
        T_camisa[i+1] = T_camisa[i] + dT_camisa * dt
        
        dT_fermentador = ((T_camisa[i] + perturbacion) - T_fermentador[i]) / tau_fermentador
        T_fermentador[i+1] = T_fermentador[i] + dT_fermentador * dt
        
    return t, T_fermentador, T_camisa

# ==========================================
# INTERFAZ DE USUARIO
# ==========================================
st.title("🏭 Diseño de Estrategias de Control Avanzado")
st.caption(f"**Asignatura:** {ASIGNATURA} | **Autor:** {AUTOR} | **Licencia:** {LICENCIA}")

tab1, tab2, tab3, tab4 = st.tabs([
    "📖 Caso de Estudio", 
    "🛠️ Diseño de Lazos", 
    "📈 Simulación Dinámica", 
    "📥 Informe Final"
])

# --- TAB 1: CASO DE ESTUDIO ---
with tab1:
    st.header("1. Descripción del Proceso: Fermentador Continuo")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        **Analiza el siguiente diagrama y el texto descriptivo:**
        
        El medio de cultivo se obtiene a partir de la dilución de nutrientes concentrados, existe, por tanto, una relación entre los caudales de agua de dilución y de nutrientes concentrados. 
        
        El crecimiento microbiano genera un aumento rápido de temperatura en el fermentador que debe ser controlada a través del paso de agua de refrigeración en el encamisado, como la medida de la temperatura en el fermentador tiene cierto tiempo muerto se recomienda el uso de un lazo específico. 
        
        La dosificación del medio de cultivo debe controlarse a partir de la medida de la concentración de sustrato en el fermentador. La concentración de oxígeno disuelto (OD) en el fermentador es un parámetro clave que debe mantenerse en un valor estable mediante la regulación del caudal de aire. Adicionalmente deben controlarse los niveles de ambos recipientes.
        """)
    with col2:
        # Aquí puedes cargar la imagen que el alumno debe analizar
        st.info("📌 **Nota para el profesor:** Sube la imagen del diagrama a la misma carpeta y usa `st.image('fermentador.png')` aquí.")
        # st.image("fermentador.png", caption="Diagrama mudo del proceso")

# --- TAB 2: DISEÑO DE LAZOS ---
with tab2:
    st.header("2. Asignación de Estrategias de Control")
    st.write("Selecciona la estrategia de control óptima para cada subsistema descrito en el caso de estudio.")
    
    nombre_alumno = st.text_input("Nombre del Alumno / Grupo:", placeholder="Ej. Equipo 1")
    
    st.divider()
    
    colA, colB = st.columns(2)
    
    with colA:
        lazo_dilucion = st.selectbox(
            "A. Dilución de nutrientes concentrados con agua",
            ["Seleccionar...", "Control Feedback Simple", "Control en Cascada", "Control de Razón (Ratio)", "Control Split Range", "Control Feedforward"]
        )
        
        lazo_temperatura = st.selectbox(
            "B. Control de Temperatura del Fermentador (con tiempo muerto)",
            ["Seleccionar...", "Control Feedback Simple", "Control en Cascada", "Control de Razón (Ratio)", "Control Split Range", "Control Feedforward"]
        )
        
    with colB:
        lazo_od = st.selectbox(
            "C. Control de Oxígeno Disuelto (OD) regulando aire",
            ["Seleccionar...", "Control Feedback Simple", "Control en Cascada", "Control de Razón (Ratio)", "Control Split Range", "Control Feedforward"]
        )
        
        lazo_nivel = st.selectbox(
            "D. Control de Nivel de los recipientes",
            ["Seleccionar...", "Control Feedback Simple", "Control en Cascada", "Control de Razón (Ratio)", "Control Split Range", "Control Feedforward"]
        )

# --- TAB 3: SIMULACIÓN ---
with tab3:
    st.header("3. Justificación de la Estrategia Térmica")
    st.markdown("Has leído que la temperatura del fermentador sufre un **tiempo muerto**. Comprueba matemáticamente por qué la estrategia avanzada es necesaria frente a un crecimiento microbiano brusco (perturbación exotérmica).")
    
    estrategia_sim = st.radio("Selecciona la arquitectura a simular:", 
                              ["Lazo Simple (Feedback)", "Control en Cascada"], horizontal=True)
    
    t, T_ferm, T_cam = simular_temperatura(estrategia_sim)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=T_ferm, name="T. Fermentador (Variable Controlada)", line=dict(color='red', width=3)))
    fig.add_trace(go.Scatter(x=t, y=T_cam, name="T. Camisa (Variable Esclava/Manipulada)", line=dict(color='blue', dash='dash')))
    fig.add_trace(go.Scatter(x=[0, 100], y=[37, 37], name="Setpoint (37ºC)", line=dict(color='green', dash='dot')))
    
    # Resaltar zona de perturbación
    fig.add_vrect(x0=20, x1=100, fillcolor="red", opacity=0.1, layer="below", line_width=0, annotation_text="Pico Exotérmico")
    
    fig.update_layout(title=f"Respuesta del Sistema Térmico usando {estrategia_sim}",
                      xaxis_title="Tiempo (min)", yaxis_title="Temperatura (ºC)",
                      hovermode="x unified")
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("💡 **Observación:** El lazo simple tarda mucho en reaccionar debido al tiempo muerto de la sonda. El control en cascada detecta el cambio de energía en la camisa antes de que afecte gravemente al fermentador.")

# --- TAB 4: INFORME FINAL ---
with tab4:
    st.header("4. Evaluación y Descarga")
    
    if not nombre_alumno or lazo_dilucion == "Seleccionar...":
        st.warning("Completa tu nombre y al menos una estrategia en la Pestaña 2 para generar el informe.")
    else:
        # Corrección automática básica
        aciertos = 0
        if lazo_dilucion == "Control de Razón (Ratio)": aciertos += 1
        if lazo_temperatura == "Control en Cascada": aciertos += 1
        if lazo_od == "Control Feedback Simple": aciertos += 1
        if lazo_nivel == "Control Feedback Simple": aciertos += 1
        
        nota = (aciertos / 4) * 10
        
        informe = f"""=======================================================
INFORME DE DISEÑO DE ESTRATEGIAS DE CONTROL
Asignatura: {ASIGNATURA}
Profesor: {AUTOR}
Licencia: {LICENCIA}
=======================================================

DATOS DEL ALUMNO:
Nombre: {nombre_alumno}
Fecha de realización: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

ESTRATEGIAS SELECCIONADAS (CASO FERMENTADOR):
1. Dilución de nutrientes: {lazo_dilucion}
2. Temperatura (con retardo): {lazo_temperatura}
3. Oxígeno Disuelto: {lazo_od}
4. Nivel de tanques: {lazo_nivel}

RESULTADO DE LA EVALUACIÓN LÓGICA:
Aciertos: {aciertos} de 4
Calificación del diseño: {nota:.1f} / 10.0

FIRMA DEL SIMULADOR:
El alumno ha interactuado con la simulación dinámica
de control en cascada frente a lazo simple.
=======================================================
"""
        st.text_area("Revisión del Informe:", informe, height=350)
        
        st.download_button(
            label="💾 Descargar P&ID y Estrategias (.txt)",
            data=informe,
            file_name=f"Estrategias_{nombre_alumno.replace(' ','_')}.txt",
            mime="text/plain",
            type="primary"
        )
