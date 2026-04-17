import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA Y METADATOS
# ==========================================
st.set_page_config(page_title="Lab Virtual - Práctica 3", layout="wide")

st.markdown("""
    <div style='background-color: #005b96; padding: 15px; border-radius: 10px; color: white;'>
        <h2 style='color: white; margin-bottom: 0px;'>Práctica 3: Control Avanzado - Domando Perturbaciones con Control en Cascada</h2>
        <p style='margin-bottom: 0px;'><b>Asignatura:</b> Control e Instrumentación de Procesos Químicos</p>
        <p style='margin-bottom: 0px;'><b>Autor:</b> Jose Joaquin Gonzalez Cortes</p>
        <p style='font-size: 12px; margin-top: 5px;'><i>Este material se distribuye bajo licencia CC BY-NC-SA 4.0</i></p>
    </div>
    <br>
""", unsafe_allow_html=True)

# ==========================================
# INICIALIZACIÓN DE ESTADOS (SESSION STATE)
# ==========================================
if 'caida_presion' not in st.session_state:
    st.session_state['caida_presion'] = 30.0
if 'kc_m' not in st.session_state: st.session_state['kc_m'] = 2.0
if 'ti_m' not in st.session_state: st.session_state['ti_m'] = 40.0
if 'kc_s' not in st.session_state: st.session_state['kc_s'] = 3.0
if 'ti_s' not in st.session_state: st.session_state['ti_s'] = 5.0
if 'q1_resp' not in st.session_state: st.session_state['q1_resp'] = ""
if 'q2_resp' not in st.session_state: st.session_state['q2_resp'] = ""

# ==========================================
# SIDEBAR: DATOS DEL ALUMNO Y NAVEGACIÓN
# ==========================================
st.sidebar.header("📋 Datos del Alumno")
alumno_nombre = st.sidebar.text_input("Nombre y Apellidos:")
alumno_id = st.sidebar.text_input("DNI / Matrícula:")

st.sidebar.markdown("---")
st.sidebar.header("🧭 Navegación")
fase = st.sidebar.radio("Selecciona la Fase de la Práctica:",[
    "1. El Fracaso del Lazo Simple", 
    "2. Diseño del Control en Cascada", 
    "3. Simulación y Comparativa", 
    "4. Evaluación e Informe"
])

# ==========================================
# FASE 1: EL FRACASO DEL LAZO SIMPLE
# ==========================================
if fase == "1. El Fracaso del Lazo Simple":
    st.header("Fase 1: El Problema de las Perturbaciones en el Servicio")
    st.markdown("""
    *Basado en el Tema 6 (Control Básico y Avanzado).*
    Tenemos un **Reactor Exotérmico** que debe operar a 80ºC. Usamos un Lazo de Control Simple (Feedback) donde un controlador de temperatura (TC) manipula directamente la válvula de agua de refrigeración.
    
    **El Problema:** El agua proviene de una red general de la fábrica. Si otros equipos demandan agua, la presión de nuestra línea cae bruscamente.
    ¿Qué pasará con la temperatura de nuestro reactor si la presión del agua cae y usamos un control simple?
    """)
    
    caida = st.slider("Caída de presión en la red de agua (%)", min_value=0, max_value=60, value=30, step=5)
    st.session_state['caida_presion'] = caida
    
    st.warning(f"Has configurado una caída de presión del **{caida}%**. Esto significa que, sin mover la válvula, entrará menos agua fría al reactor. Pasa a la Fase 2 para diseñar una solución.")
    
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Feedback_loop_with_disturbance.svg/800px-Feedback_loop_with_disturbance.svg.png", width=400, caption="Lazo de Control Simple (Feedback) sometido a perturbación.")

# ==========================================
# FASE 2: DISEÑO DEL CONTROL EN CASCADA
# ==========================================
elif fase == "2. Diseño del Control en Cascada":
    st.header("Fase 2: Arquitectura Maestro-Esclavo")
    st.markdown("""
    Para evitar que la caída de presión afecte al reactor, implementaremos un **Control en Cascada**:
    1.  **Lazo Maestro (TC):** Mide la Temperatura del reactor. Es un proceso de dinámica lenta. Su salida calcula el *SetPoint* de caudal de agua que necesitamos.
    2.  **Lazo Esclavo (FC):** Mide el Caudal de agua. Es muy rápido. Recibe la orden del Maestro y mueve la válvula.
    
    **Regla de Oro (Tema 6):** El lazo esclavo (interno) debe ser entre 5 y 10 veces más rápido que el lazo maestro (externo). Configura los parámetros PID (P - Proporcional, I - Tiempo Integral).
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Controlador Maestro (TC - Lento)")
        kc_m = st.number_input("Ganancia Proporcional (Kc Maestro)", value=2.0, min_value=0.1, step=0.1)
        ti_m = st.number_input("Tiempo Integral (Ti Maestro - seg)", value=40.0, min_value=1.0, step=1.0)
        st.session_state['kc_m'] = kc_m
        st.session_state['ti_m'] = ti_m
        st.info("💡 Un tiempo integral (Ti) alto significa que la acción integral es más lenta y suave.")
        
    with col2:
        st.subheader("Controlador Esclavo (FC - Rápido)")
        kc_s = st.number_input("Ganancia Proporcional (Kc Esclavo)", value=3.0, min_value=0.1, step=0.1)
        ti_s = st.number_input("Tiempo Integral (Ti Esclavo - seg)", value=5.0, min_value=0.1, step=0.5)
        st.session_state['kc_s'] = kc_s
        st.session_state['ti_s'] = ti_s
        st.success("💡 Un tiempo integral (Ti) bajo hace que el controlador esclavo reaccione casi inmediatamente.")

# ==========================================
# FASE 3: SIMULACIÓN Y COMPARATIVA
# ==========================================
elif fase == "3. Simulación y Comparativa":
    st.header("Fase 3: Simulación Dinámica")
    st.markdown("Comparativa matemática del Lazo Simple vs. Control en Cascada ante la caída de presión configurada en la Fase 1.")
    
    if st.button("▶️ Iniciar Simulación", type="primary"):
        # Parámetros de simulación
        t = np.linspace(0, 300, 600)
        dt = t[1] - t[0]
        drop_p = st.session_state['caida_presion'] / 100.0
        
        # Perturbación: Cae la presión en t=50s
        P_agua = np.ones(len(t))
        P_agua[t >= 50] = 1.0 - drop_p
        
        # Constantes del proceso
        tau_jacket = 10.0
        tau_reactor = 40.0
        SP_T = 80.0
        
        # --- Arrays para Lazo Simple ---
        T_r_sing = np.ones(len(t)) * 80.0
        x1_sing = 0.0
        V_sing = np.ones(len(t)) * 50.0
        F_sing = np.ones(len(t)) * 50.0
        int_sing = 0.0
        Kc_sing = -st.session_state['kc_m'] # Acción Inversa (refrigeración)
        Ti_sing = st.session_state['ti_m']
        
        # --- Arrays para Lazo Cascada ---
        T_r_casc = np.ones(len(t)) * 80.0
        x1_casc = 0.0
        V_casc = np.ones(len(t)) * 50.0
        F_casc = np.ones(len(t)) * 50.0
        SP_F = np.ones(len(t)) * 50.0
        int_m = 0.0
        int_s = 0.0
        Kc_m = -st.session_state['kc_m'] # Acción inversa
        Ti_m = st.session_state['ti_m']
        Kc_s = st.session_state['kc_s']  # Acción directa (Caudal-Válvula)
        Ti_s = st.session_state['ti_s']
        
        # BUCLE DE SIMULACIÓN (Integración de Euler)
        for i in range(1, len(t)):
            # ==============================
            # 1. LAZO SIMPLE (Feedback solo)
            # ==============================
            e_sing = SP_T - T_r_sing[i-1]
            if 0 < V_sing[i-1] < 100: int_sing += e_sing * dt # Anti-windup
            
            V_sing[i] = np.clip(50.0 + Kc_sing * (e_sing + int_sing/Ti_sing), 0, 100)
            F_sing[i] = V_sing[i] * np.sqrt(P_agua[i])
            
            # Dinámica Planta Simple
            dx1_sing = (- (F_sing[i] - 50.0) - x1_sing) / tau_jacket
            x1_sing += dx1_sing * dt
            dT_sing = (x1_sing - (T_r_sing[i-1] - 80.0)) / tau_reactor
            T_r_sing[i] = T_r_sing[i-1] + dT_sing * dt

            # ==============================
            # 2. CONTROL EN CASCADA
            # ==============================
            # Maestro (TC)
            e_m = SP_T - T_r_casc[i-1]
            if 0 < SP_F[i-1] < 100: int_m += e_m * dt
            SP_F[i] = np.clip(50.0 + Kc_m * (e_m + int_m/Ti_m), 0, 100)
            
            # Esclavo (FC)
            e_s = SP_F[i] - F_casc[i-1]
            if 0 < V_casc[i-1] < 100: int_s += e_s * dt
            V_casc[i] = np.clip(50.0 + Kc_s * (e_s + int_s/Ti_s), 0, 100)
            
            F_casc[i] = V_casc[i] * np.sqrt(P_agua[i])
            
            # Dinámica Planta Cascada
            dx1_casc = (- (F_casc[i] - 50.0) - x1_casc) / tau_jacket
            x1_casc += dx1_casc * dt
            dT_casc = (x1_casc - (T_r_casc[i-1] - 80.0)) / tau_reactor
            T_r_casc[i] = T_r_casc[i-1] + dT_casc * dt

        # CREACIÓN DE GRÁFICOS (Plotly)
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                            subplot_titles=("Temperatura del Reactor (ºC)", "Caudal de Agua Fría (F)", "Apertura de Válvula (%)"),
                            vertical_spacing=0.08)
        
        # Temp
        fig.add_trace(go.Scatter(x=t, y=T_r_sing, name="Temp - Lazo Simple", line=dict(color="red")), row=1, col=1)
        fig.add_trace(go.Scatter(x=t, y=T_r_casc, name="Temp - Cascada", line=dict(color="green")), row=1, col=1)
        fig.add_trace(go.Scatter(x=t, y=np.ones(len(t))*80, name="SetPoint", line=dict(dash="dot", color="black")), row=1, col=1)
        
        # Flujo
        fig.add_trace(go.Scatter(x=t, y=F_sing, name="Flujo - Simple", line=dict(color="lightcoral")), row=2, col=1)
        fig.add_trace(go.Scatter(x=t, y=F_casc, name="Flujo - Cascada", line=dict(color="lightgreen")), row=2, col=1)
        
        # Válvula
        fig.add_trace(go.Scatter(x=t, y=V_sing, name="Válvula - Simple", line=dict(color="darkred")), row=3, col=1)
        fig.add_trace(go.Scatter(x=t, y=V_casc, name="Válvula - Cascada", line=dict(color="darkgreen")), row=3, col=1)
        
        fig.update_layout(height=700, title_text="Resultados de la Simulación frente a Perturbación en t=50s")
        st.plotly_chart(fig, use_container_width=True)
        
        st.success("👉 **Observa las gráficas:** Fíjate cómo en el Lazo Simple, la válvula no se abre hasta que la Temperatura del reactor ya ha subido (¡Demasiado tarde!). En el Control en Cascada, el Lazo Esclavo detecta la caída de caudal al instante (gráfico 2) y abre la válvula rápidamente (gráfico 3) *antes* de que la Temperatura del reactor sufra (gráfico 1). ¡Ese es el poder de la Cascada!")

# ==========================================
# FASE 4: EVALUACIÓN E INFORME
# ==========================================
elif fase == "4. Evaluación e Informe":
    st.header("Fase 4: Estudio de Caso y Generación de Informe")
    st.markdown("Responde a las siguientes preguntas para consolidar tu aprendizaje. Una vez respondidas, genera tu archivo TXT para subirlo al campus.")
    
    q1 = st.text_area("1. ¿Por qué el Lazo Simple de Temperatura es ineficiente para corregir perturbaciones que ocurren en la línea de servicio (como la presión de agua)?", value=st.session_state['q1_resp'])
    st.session_state['q1_resp'] = q1
    
    q2 = st.text_area("2. Según la Regla de Oro del diseño (Tema 6), ¿Por qué el tiempo integral (Ti) del Controlador Esclavo de caudal debe ser mucho menor que el del Controlador Maestro de Temperatura?", value=st.session_state['q2_resp'])
    st.session_state['q2_resp'] = q2
    
    st.markdown("---")
    
    if st.button("Generar Informe TXT"):
        if not alumno_nombre or not alumno_id:
            st.error("⚠️ Por favor, introduce tu Nombre y Matrícula en el menú lateral izquierdo.")
        elif not q1 or not q2:
            st.error("⚠️ Por favor, responde a todas las preguntas de reflexión.")
        else:
            fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            informe_texto = f"""====================================================
LABORATORIO VIRTUAL - PRÁCTICA 3 (CONTROL AVANZADO)
====================================================
Asignatura: Control e Instrumentación de Procesos Químicos
Autor Simulador: Jose Joaquin Gonzalez Cortes
Licencia: CC BY-NC-SA 4.0
Fecha de generación: {fecha}

DATOS DEL ALUMNO
----------------------------------------------------
Nombre: {alumno_nombre}
Matrícula/DNI: {alumno_id}

PARÁMETROS DE SIMULACIÓN (CASCADA)
----------------------------------------------------
- Perturbación (Caída de Presión): {st.session_state['caida_presion']} %
- Sintonía Maestro (TC): Kc = {st.session_state['kc_m']}, Ti = {st.session_state['ti_m']} s
- Sintonía Esclavo (FC): Kc = {st.session_state['kc_s']}, Ti = {st.session_state['ti_s']} s

RESPUESTAS AL ESTUDIO DE CASO
----------------------------------------------------
Pregunta 1: Ineficiencia del Lazo Simple ante perturbaciones de servicio.
Respuesta: {st.session_state['q1_resp']}

Pregunta 2: Justificación de la velocidad del lazo esclavo (Regla de Oro).
Respuesta: {st.session_state['q2_resp']}

====================================================
Documento generado automáticamente por el simulador OCW.
"""
            st.download_button(
                label="📥 Descargar Informe Completo (.txt)",
                data=informe_texto,
                file_name=f"Practica3_Cascada_{alumno_id}.txt",
                mime="text/plain"
            )
            st.success("✅ ¡Informe generado! Haz clic en el botón de arriba para descargarlo.")
