import streamlit as st
import numpy as np
import plotly.graph_objects as go
import graphviz
from datetime import datetime

# ==========================================
# CONFIGURACIÓN
# ==========================================
st.set_page_config(page_title="P&ID Interactivo - Fermentador", layout="wide")

ASIGNATURA = "Control e Instrumentación de Procesos Químicos"
AUTOR = "José Joaquín González Cortés"
LICENCIA = "CC BY-NC-SA 4.0"

# ==========================================
# FUNCIONES DE GENERACIÓN P&ID (GRAPHVIZ)
# ==========================================
def dibujar_pid_temperatura(estrategia):
    """Genera el diagrama P&ID en tiempo real basado en la selección del alumno."""
    dot = graphviz.Digraph(engine='dot')
    dot.attr(rankdir='LR', nodesep='0.8', ranksep='1.0')
    
    # Nodos de Proceso (Equipos)
    dot.node('F', 'Fermentador\n(Proceso)', shape='box', style='filled', fillcolor='#f0f2f6')
    dot.node('C', 'Camisa de\nRefrigeración', shape='box', style='filled', fillcolor='#dbe4f0')
    
    # Instrumento primario (Transmisor de Temperatura)
    dot.node('TT1', 'TT\n101', shape='circle', style='filled', fillcolor='white')
    dot.edge('F', 'TT1', style='solid', label='Medida Tº') # Línea de proceso
    
    # Controlador Maestro
    dot.node('TC1', 'TC\n101', shape='circle', style='filled', fillcolor='white')
    dot.edge('TT1', 'TC1', style='dashed', label='Señal Eléctrica (4-20mA)')

    if estrategia == "Lazo Simple (Feedback)":
        # Actuador directo
        dot.node('TV', 'TV\n101', shape='circle', style='filled', fillcolor='#ffcccc')
        dot.edge('TC1', 'TV', style='dashed', label='Señal de Control')
        dot.edge('TV', 'C', style='solid', label='Agua Fría')
        
    elif estrategia == "Control en Cascada":
        # Esclavo de Cascada
        dot.node('TC2', 'TC\n102', shape='circle', style='filled', fillcolor='#ccffcc', 
                 tooltip='Controlador Esclavo de la Camisa')
        dot.node('TT2', 'TT\n102', shape='circle', style='filled', fillcolor='white')
        
        # Conexión Cascada (El TC1 manda el SetPoint al TC2)
        dot.edge('TC1', 'TC2', style='dashed', label='SetPoint (SP)', color='blue', penwidth='2')
        
        # Medida de la camisa al esclavo
        dot.edge('C', 'TT2', style='solid')
        dot.edge('TT2', 'TC2', style='dashed')
        
        # Actuador comandado por el esclavo
        dot.node('TV', 'TV\n102', shape='circle', style='filled', fillcolor='#ffcccc')
        dot.edge('TC2', 'TV', style='dashed')
        dot.edge('TV', 'C', style='solid', label='Agua Fría')

    return dot

def simular_dinamica(estrategia):
    """Simulación diferencial de la respuesta térmica (simplificada)."""
    t = np.linspace(0, 100, 200)
    T_ferm = np.ones_like(t) * 37.0
    T_cam = np.ones_like(t) * 20.0
    
    for i in range(10, len(t)-1):
        dt = t[i] - t[i-1]
        perturbacion = 8.0 if t[i] > 20 else 0.0 # Pico exotérmico
        
        error = 37.0 - (T_ferm[i-4] if i > 4 else T_ferm[i]) # Retardo
        
        if estrategia == "Lazo Simple (Feedback)":
            u = 20.0 - (2.0 * error)
        else:
            sp_cam = 20.0 - (3.5 * error)
            u = 20.0 - (5.0 * (sp_cam - T_cam[i]))
            
        u = np.clip(u, 5, 40)
        T_cam[i+1] = T_cam[i] + ((u - T_cam[i])/5.0) * dt
        T_ferm[i+1] = T_ferm[i] + ((T_cam[i] + perturbacion - T_ferm[i])/15.0) * dt
        
    return t, T_ferm, T_cam

# ==========================================
# INTERFAZ DE LA APLICACIÓN
# ==========================================
st.title("🧩 Constructor de Lazos P&ID: El Fermentador")
st.caption(f"**Asignatura:** {ASIGNATURA} | **Autor:** {AUTOR} | **Norma:** ISA-5.1")

# Introducción al Reto
with st.expander("📖 Leer el Caso de Estudio (Click para expandir)", expanded=True):
    st.markdown("""
    **Problema Térmico:** El crecimiento microbiano genera un aumento rápido de temperatura en el fermentador que debe ser controlada a través del paso de agua de refrigeración en el encamisado. Como la sonda de temperatura del fermentador tiene **tiempo muerto** (es lenta), se recomienda usar una arquitectura avanzada para reaccionar antes de que el fermentador se sobrecaliente.
    """)

tab_construccion, tab_simulacion, tab_informe = st.tabs([
    "🛠️ 1. Construir P&ID", 
    "📈 2. Simular Respuesta", 
    "📥 3. Informe Técnico"
])

# --- TAB 1: CONSTRUCTOR VISUAL P&ID ---
with tab_construccion:
    st.header("Construcción del Lazo Térmico (Simbología ISA)")
    
    col_controles, col_lienzo = st.columns([1, 2])
    
    with col_controles:
        st.write("**Paso 1: Elección de la Arquitectura**")
        st.info("Selecciona cómo quieres conectar los instrumentos. El diagrama de la derecha se actualizará con tu decisión.")
        
        estrategia_termica = st.radio(
            "Estrategia para el Control de Temperatura:",
            ["Lazo Simple (Feedback)", "Control en Cascada"]
        )
        
        st.write("**Análisis de la decisión:**")
        if estrategia_termica == "Lazo Simple (Feedback)":
            st.error("❌ **Alerta de Ingeniería:** Con esta estrategia, el controlador TC-101 ataca directamente a la válvula. Dado que la sonda TT-101 tiene retardo, cuando detecte el cambio de temperatura, ya será demasiado tarde.")
        else:
            st.success("✅ **Diseño Óptimo:** Has introducido un lazo interno (esclavo). Ahora, si el agua de refrigeración cambia, el TC-102 lo detecta y corrige inmediatamente, antes de que afecte al fermentador.")

    with col_lienzo:
        st.write("**Diagrama P&ID Generado:**")
        # Generamos y renderizamos el grafo de Graphviz en tiempo real
        diagrama_pid = dibujar_pid_temperatura(estrategia_termica)
        st.graphviz_chart(diagrama_pid, use_container_width=True)

# --- TAB 2: SIMULACIÓN ---
with tab_simulacion:
    st.header("Comprobación Dinámica del Lazo Construido")
    st.write(f"Has diseñado un diagrama basado en **{estrategia_termica}**. Veamos cómo se comporta físicamente frente a una perturbación exotérmica (crecimiento brusco de bacterias).")
    
    t, T_ferm, T_cam = simular_dinamica(estrategia_termica)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=T_ferm, name="T. Fermentador (TT-101)", line=dict(color='#d62728', width=3)))
    fig.add_trace(go.Scatter(x=t, y=T_cam, name="T. Camisa (TT-102)", line=dict(color='#1f77b4', dash='dash')))
    fig.add_hline(y=37.0, line_dash="dot", line_color="green", annotation_text="SetPoint (37ºC)")
    fig.add_vrect(x0=20, x1=100, fillcolor="red", opacity=0.05, layer="below", annotation_text="Perturbación Exotérmica")
    
    fig.update_layout(title="Dinámica de Temperaturas del Reactor", xaxis_title="Tiempo (min)", yaxis_title="Temperatura (ºC)")
    st.plotly_chart(fig, use_container_width=True)

# --- TAB 3: INFORME ---
with tab_informe:
    st.header("Generar Especificación Funcional")
    nombre = st.text_input("Ingeniero/a a cargo del diseño:")
    
    if nombre:
        justificacion = "El alumno optó por un control en cascada, protegiendo al sistema del tiempo muerto." if estrategia_termica == "Control en Cascada" else "El alumno optó por un lazo simple, resultando en oscilaciones excesivas debido al retardo de medición."
        
        informe = f"""=======================================================
ESPECIFICACIÓN FUNCIONAL DE INSTRUMENTACIÓN (P&ID)
Asignatura: {ASIGNATURA}
Tutor: {AUTOR} | Licencia: {LICENCIA}
=======================================================
INGENIERO DISEÑADOR: {nombre}
FECHA: {datetime.now().strftime("%d/%m/%Y %H:%M")}

1. SUBSISTEMA TÉRMICO (Fermentador - Camisa)
Estrategia seleccionada : {estrategia_termica}
Instrumentos generados  : TT-101, TC-101 {', TT-102, TC-102' if estrategia_termica == 'Control en Cascada' else ''}, TV

2. RESULTADOS DE LA SIMULACIÓN
{justificacion}

3. VALIDACIÓN
Documento válido como Práctica 3 para el campus virtual.
======================================================="""
        
        st.text_area("Previsualización:", informe, height=300)
        st.download_button("💾 Descargar Informe de Ingeniería (.txt)", data=informe, file_name=f"PID_{nombre}.txt")
