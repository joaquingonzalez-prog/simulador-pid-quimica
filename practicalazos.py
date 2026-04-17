import streamlit as st
import numpy as np
import plotly.graph_objects as go

# ==========================================
# CONFIGURACIÓN OCW
# ==========================================
st.set_page_config(page_title="Laboratorio OCW: Control Avanzado", layout="wide")

st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/OpenCourseWare_logo.svg/512px-OpenCourseWare_logo.svg.png", width=150)
st.sidebar.title("Práctica 3")
st.sidebar.markdown("**Asignatura:** Control e Instrumentación de Procesos Químicos")
st.sidebar.markdown("**Tema 6:** Control Básico en la Industria")
st.sidebar.divider()

# Navegación lateral paso a paso
modulo = st.sidebar.radio(
    "Progreso del Laboratorio:",
    ["1. Introducción al Caso", 
     "2. Lazo 1: Control de Razón (Nutrientes)", 
     "3. Lazo 2: Cascada (Temperatura)", 
     "4. Evaluación y Cierre"]
)

# ==========================================
# MÓDULO 1: INTRODUCCIÓN
# ==========================================
if modulo == "1. Introducción al Caso":
    st.title("🏭 Planta de Fermentación Continua")
    st.markdown("""
    ### Objetivos de Aprendizaje
    Al finalizar este módulo virtual, el alumno será capaz de:
    1. Identificar las limitaciones del control *Feedback* simple frente a perturbaciones específicas.
    2. Aplicar la estrategia de **Control de Razón (Ratio)** para mantener proporciones de mezcla.
    3. Aplicar el **Control en Cascada** para mitigar los efectos del tiempo muerto en sistemas térmicos.
    
    ### Descripción del Proceso
    En este laboratorio analizaremos un fermentador continuo. Para que los microorganismos sobrevivan y produzcan de forma óptima, debemos resolver dos grandes retos de instrumentación:
    * **Reto A (Mezcla):** El medio de cultivo se forma diluyendo un nutriente concentrado con agua. Si el caudal de agua fluctúa, la concentración del alimento cambiará, matando de hambre o sobrealimentando a las bacterias.
    * **Reto B (Refrigeración):** La reacción es exotérmica. Necesitamos enfriar el reactor con una camisa de agua fría, pero el sensor de temperatura del reactor es muy grueso y tarda en detectar los cambios (tiene un alto tiempo muerto).
    
    👈 **Utiliza el menú lateral para avanzar al primer reto.**
    """)
    st.info("💡 **Nota metodológica:** Asegúrate de haber repasado los apuntes del Tema 6 (Estrategias de Control) antes de continuar.")

# ==========================================
# MÓDULO 2: CONTROL DE RAZÓN
# ==========================================
elif modulo == "2. Lazo 1: Control de Razón (Nutrientes)":
    st.title("🧪 Reto A: Dosificación de Nutrientes")
    st.markdown("""
    El cultivo requiere que por cada **10 L/min de agua de dilución**, entren exactamente **2 L/min de nutriente concentrado** (Razón Óptima $R = 0.2$). 
    
    Experimenta con los deslizadores. Observa qué ocurre con un lazo simple (que intenta mantener el nutriente fijo a 2 L/min sin importar el agua) frente a un control de razón que "sigue" al caudal de agua.
    """)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Panel de Operación")
        caudal_agua = st.slider("Caudal de Agua de Dilución (Perturbación) [L/min]:", min_value=5.0, max_value=20.0, value=10.0, step=1.0)
        estrategia_mezcla = st.radio("Estrategia de Control del Nutriente:", ["Control Fijo (Lazo Simple)", "Control de Razón (Ratio)"])
        
    with col2:
        # Lógica de la mezcla
        caudal_nutriente_fijo = 2.0
        
        if estrategia_mezcla == "Control Fijo (Lazo Simple)":
            nutriente_real = caudal_nutriente_fijo
        else:
            nutriente_real = caudal_agua * 0.2
            
        concentracion = nutriente_real / (caudal_agua + nutriente_real)
        concentracion_ideal = 2.0 / (10.0 + 2.0)
        
        # Gráfica de barras comparativa
        fig = go.Figure()
        fig.add_trace(go.Bar(x=['Concentración Actual'], y=[concentracion], marker_color='blue' if abs(concentracion - concentracion_ideal) < 0.01 else 'red'))
        fig.add_hline(y=concentracion_ideal, line_dash="dash", line_color="green", annotation_text="Concentración Óptima")
        fig.update_layout(yaxis_title="Fracción de Nutriente", yaxis_range=[0, 0.4], title="Calidad del Medio de Cultivo")
        
        st.plotly_chart(fig, use_container_width=True)
        
        if abs(concentracion - concentracion_ideal) > 0.01:
            st.error("⚠️ La concentración se ha desviado peligrosamente de la óptima.")
        else:
            st.success("✅ Medio de cultivo en condiciones perfectas.")

# ==========================================
# MÓDULO 3: CONTROL EN CASCADA
# ==========================================
elif modulo == "3. Lazo 2: Cascada (Temperatura)":
    st.title("🌡️ Reto B: Refrigeración con Tiempo Muerto")
    st.markdown("""
    El crecimiento celular genera un aumento brusco de temperatura. La sonda (TT-101) tarda **5 minutos** en reaccionar. 
    Selecciona la estrategia y observa la dinámica del sistema frente a un "pico" exotérmico en el minuto 20.
    """)
    
    estrategia_temp = st.selectbox("Estrategia del Lazo Térmico:", ["Selecciona...", "Control Feedback Simple", "Control en Cascada"])
    
    if estrategia_temp != "Selecciona...":
        # Simulación matemática
        t = np.linspace(0, 80, 200)
        T_ferm = np.ones_like(t) * 37.0
        T_cam = np.ones_like(t) * 20.0
        
        for i in range(10, len(t)-1):
            dt = t[i] - t[i-1]
            perturbacion = 10.0 if 20 < t[i] < 40 else 0.0 # Perturbación tipo pulso
            
            error_m = 37.0 - (T_ferm[i-12] if i > 12 else T_ferm[i]) # Fuerte retardo
            
            if estrategia_temp == "Control Feedback Simple":
                u = 20.0 - (2.5 * error_m)
            else: # Cascada
                sp_c = 20.0 - (4.0 * error_m)
                u = 20.0 - (6.0 * (sp_c - T_cam[i])) # El esclavo corrige rápido
                
            u = np.clip(u, 5, 40)
            T_cam[i+1] = T_cam[i] + ((u - T_cam[i])/3.0) * dt
            T_ferm[i+1] = T_ferm[i] + ((T_cam[i] + perturbacion - T_ferm[i])/10.0) * dt
            
        # Graficar
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=t, y=T_ferm, name="T. Fermentador", line=dict(color='red', width=3)))
        fig2.add_trace(go.Scatter(x=t, y=T_cam, name="T. Camisa", line=dict(color='blue', dash='dash')))
        fig2.add_hline(y=37.0, line_dash="dot", line_color="green", annotation_text="Setpoint 37ºC")
        fig2.add_hrect(y0=40, y1=45, fillcolor="red", opacity=0.2, annotation_text="ZONA CRÍTICA")
        fig2.update_layout(xaxis_title="Tiempo (min)", yaxis_title="Temperatura (ºC)", yaxis_range=[15, 45])
        
        st.plotly_chart(fig2, use_container_width=True)
        
        if estrategia_temp == "Control Feedback Simple":
            st.warning("Fíjate cómo el lazo simple reacciona tarde. La temperatura sube a la zona crítica porque el controlador no 've' el aumento de temperatura hasta que es demasiado tarde.")
        else:
            st.success("¡Excelente! Al usar un controlador esclavo (Cascada) midiendo la camisa, reaccionamos al cambio de energía antes de que la temperatura del fermentador se descontrole.")

# ==========================================
# MÓDULO 4: EVALUACIÓN
# ==========================================
elif modulo == "4. Evaluación y Cierre":
    st.title("📝 Autoevaluación del Laboratorio")
    st.markdown("Comprueba si has asimilado los conceptos del Tema 6 y de esta práctica.")
    
    with st.form("quiz"):
        q1 = st.radio("1. Según el Tema 6, ¿cuál es el objetivo primordial e innegociable de un sistema de control?", 
                      ["Optimizar el beneficio económico.", "Proteger el medio ambiente.", "Garantizar la seguridad (Personal y Planta).", "Mejorar la calidad del producto."])
        
        q2 = st.radio("2. ¿Por qué el control de Razón (Ratio) era necesario en la dosificación de nutrientes?", 
                      ["Porque la reacción es exotérmica.", "Porque hay un flujo salvaje (agua) que no podemos controlar directamente, y el nutriente debe mantener proporción con él.", "Para evitar la cavitación en la bomba.", "Para corregir el tiempo muerto del sensor de nivel."])
        
        q3 = st.radio("3. ¿Cuál es el propósito principal del bucle esclavo (secundario) en un control en cascada?", 
                      ["Absorber perturbaciones locales antes de que afecten a la variable principal.", "Reducir el coste de la instrumentación.", "Controlar dos válvulas al mismo tiempo.", "Sustituir al Sistema Instrumentado de Seguridad (SIS)."])
        
        submit = st.form_submit_button("Evaluar Respuestas")
        
    if submit:
        score = 0
        if "seguridad" in q1.lower(): score += 1
        if "salvaje" in q2.lower(): score += 1
        if "absorber perturbaciones" in q3.lower(): score += 1
        
        st.divider()
        if score == 3:
            st.success(f"**¡Puntuación Perfecta ({score}/3)!** Has superado con éxito el Laboratorio Virtual de Estrategias de Control.")
            st.balloons()
        else:
            st.warning(f"**Puntuación: {score}/3.** Revisa la teoría en los módulos anteriores o en los apuntes del profesor.")
