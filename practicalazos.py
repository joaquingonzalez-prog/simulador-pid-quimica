import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.integrate import odeint
import datetime

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA Y METADATOS
# ==========================================
st.set_page_config(page_title="Lab Virtual - Práctica 2", layout="wide")

st.markdown("""
    <div style='background-color: #0e4b75; padding: 15px; border-radius: 10px; color: white;'>
        <h2 style='color: white; margin-bottom: 0px;'>Práctica 2: El cuello de botella físico - Instrumentación, Dinámica y Válvulas</h2>
        <p style='margin-bottom: 0px;'><b>Asignatura:</b> Control e Instrumentación de Procesos Químicos</p>
        <p style='margin-bottom: 0px;'><b>Autor:</b> Jose Joaquin Gonzalez Cortes</p>
        <p style='font-size: 12px; margin-top: 5px;'><i>Este material se distribuye bajo licencia CC BY-NC-SA 4.0</i></p>
    </div>
    <br>
""", unsafe_allow_html=True)

# ==========================================
# INICIALIZACIÓN DE ESTADOS (SESSION STATE)
# ==========================================
if 'tau_sensor' not in st.session_state:
    st.session_state['tau_sensor'] = 5.0
if 'tipo_valvula' not in st.session_state:
    st.session_state['tipo_valvula'] = "Isoporcentual (Igual Porcentaje)"
if 'q1_respuesta' not in st.session_state:
    st.session_state['q1_respuesta'] = ""
if 'q2_respuesta' not in st.session_state:
    st.session_state['q2_respuesta'] = ""

# ==========================================
# SIDEBAR: DATOS DEL ALUMNO Y NAVEGACIÓN
# ==========================================
st.sidebar.header("📋 Datos del Alumno")
alumno_nombre = st.sidebar.text_input("Nombre y Apellidos:")
alumno_id = st.sidebar.text_input("DNI / Matrícula:")

st.sidebar.markdown("---")
st.sidebar.header("🧭 Navegación")
fase = st.sidebar.radio("Selecciona la Fase de la Práctica:",["1. Dinámica del Sensor", 
                         "2. Curva de la Válvula", 
                         "3. Impacto en el Lazo (PID)", 
                         "4. Evaluación e Informe"])

# ==========================================
# FASE 1: DINÁMICA DEL SENSOR
# ==========================================
if fase == "1. Dinámica del Sensor":
    st.header("Fase 1: El Sensor y su Constante de Tiempo ($\\tau$)")
    st.markdown("""
    *Basado en el Tema 2 (Medidores de Temperatura).* 
    Para medir la temperatura de un fluido agresivo a 150ºC partiendo de 20ºC (ambiente), usamos un **Termopar Tipo K**. 
    Para protegerlo, debemos usar una vaina (termopozo). Calcula cómo afecta la física del sistema a la constante de tiempo $\\tau$.
    
    Ecuación de conservación de energía: $\\tau = \\frac{m \cdot C_p}{h \cdot A}$
    """)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Parámetros Físicos")
        grosor_vaina = st.slider("Grosor de la vaina protectora (mm)", min_value=1.0, max_value=20.0, value=5.0, step=1.0, help="Aumenta la masa (m) del sensor.")
        vel_fluido = st.slider("Velocidad del fluido (m/s)", min_value=0.1, max_value=5.0, value=1.0, step=0.1, help="Aumenta el coeficiente convectivo (h).")
        
        # Modelo simplificado de tau
        # A mayor grosor, mayor masa -> mayor tau
        # A mayor velocidad, mayor h -> menor tau
        tau = (grosor_vaina * 3.0) / (vel_fluido * 0.8)
        st.session_state['tau_sensor'] = tau
        
        st.success(f"**Constante de tiempo calculada ($\\tau$): {tau:.2f} segundos**")
        
    with col2:
        t = np.linspace(0, 100, 500)
        T_env = 20
        T_fluid = 150
        T_medida = T_env + (T_fluid - T_env) * (1 - np.exp(-t/tau))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t, y=np.full_like(t, T_fluid), mode='lines', name='T Real del Fluido (150ºC)', line=dict(dash='dash', color='red')))
        fig.add_trace(go.Scatter(x=t, y=T_medida, mode='lines', name='T Medida por el Termopar', line=dict(color='blue', width=3)))
        
        # Marcar el 63.2% (1 Tau)
        t_tau = tau
        T_tau = T_env + (T_fluid - T_env) * 0.632
        fig.add_trace(go.Scatter(x=[t_tau], y=[T_tau], mode='markers+text', name='1 Tau (63.2%)', text=[f"  {T_tau:.1f}ºC"], textposition="bottom right", marker=dict(color='green', size=10)))
        
        fig.update_layout(title="Respuesta del Termopar a un Cambio Brusco (Escalón)", xaxis_title="Tiempo (s)", yaxis_title="Temperatura (ºC)")
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# FASE 2: CURVA DE LA VÁLVULA
# ==========================================
elif fase == "2. Curva de la Válvula":
    st.header("Fase 2: Selección del Elemento Final de Control")
    st.markdown("""
    *Basado en el Tema de Elementos Finales de Control.*
    La señal del controlador debe transformarse en caudal. Aquí analizaremos la diferencia entre la curva **Inherente** (de fábrica) 
    y la **Instalada** (cuando la válvula sufre caídas de presión en la tubería real).
    """)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Configuración de Válvula")
        tipo_valv = st.radio("Característica Inherente de la Válvula:",["Lineal", "Isoporcentual (Igual Porcentaje)", "Apertura Rápida"])
        st.session_state['tipo_valvula'] = tipo_valv
        
        caida_presion = st.slider("Relación de caída de presión (r = ΔP_válvula / ΔP_total)", 
                                  min_value=0.1, max_value=1.0, value=0.5, step=0.1,
                                  help="Si r=1, toda la caída de presión ocurre en la válvula. Si r es bajo, la tubería roba presión.")
        
    with col2:
        x = np.linspace(0, 1, 100) # Apertura de la válvula (0 a 1)
        
        # Curvas Inherentes f(x)
        if tipo_valv == "Lineal":
            fx = x
        elif tipo_valv == "Isoporcentual (Igual Porcentaje)":
            alpha = 50 # Rangeabilidad típica
            fx = alpha**(x - 1)
            fx = (fx - 1/alpha) / (1 - 1/alpha) # Normalizar para que empiece en 0
        else: # Apertura rápida
            fx = np.sqrt(x)
            
        # Curva Instalada
        r = caida_presion
        fx_inst = fx / np.sqrt(1 + r * (fx**2 - 1))
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=x*100, y=fx*100, mode='lines', name='Inherente (Fábrica)', line=dict(dash='dash', color='gray')))
        fig2.add_trace(go.Scatter(x=x*100, y=fx_inst*100, mode='lines', name='Instalada (Real en Planta)', line=dict(color='orange', width=3)))
        
        fig2.update_layout(title=f"Curva de Válvula: {tipo_valv}", xaxis_title="% de Apertura del Vástago", yaxis_title="% de Caudal (Cv)")
        st.plotly_chart(fig2, use_container_width=True)

# ==========================================
# FASE 3: IMPACTO EN EL LAZO (PID)
# ==========================================
elif fase == "3. Impacto en el Lazo (PID)":
    st.header("Fase 3: El Lazo Completo con tu Instrumentación")
    st.markdown(f"""
    Unimos lo aprendido. Tienes un controlador PID estándar (sintonizado idealmente). 
    Vamos a ver cómo responde el proceso real usando la instrumentación que dejaste configurada en las fases anteriores:
    *   **$\\tau$ del sensor:** {st.session_state['tau_sensor']:.2f} s.
    *   **Válvula:** {st.session_state['tipo_valvula']}.
    """)
    
    if st.button("Simular Lazo Cerrado"):
        # Simulación discreta de un Lazo de Control
        # Simplificación educativa para mostrar el efecto del retardo (tau)
        t_sim = np.linspace(0, 150, 300)
        dt = t_sim[1] - t_sim[0]
        
        SP = np.ones_like(t_sim) * 100 # Setpoint = 100ºC
        PV_real = np.zeros_like(t_sim)
        PV_medido = np.zeros_like(t_sim)
        OP = np.zeros_like(t_sim)
        
        # Parámetros PID fijos (Sintonía estándar agresiva)
        Kc = 2.5
        Ti = 10.0
        integral = 0.0
        
        tau = st.session_state['tau_sensor']
        
        for k in range(1, len(t_sim)):
            # Error calculado con la temperatura MEDIDA (no la real)
            error = SP[k] - PV_medido[k-1]
            integral += error * dt
            
            # Salida del controlador PID (0 a 100%)
            op_calc = Kc * error + (Kc / Ti) * integral
            OP[k] = np.clip(op_calc, 0, 100)
            
            # Proceso real (Afectado por la válvula)
            apertura = OP[k] / 100.0
            if st.session_state['tipo_valvula'] == "Isoporcentual (Igual Porcentaje)":
                caudal = 50**(apertura - 1) # Simplificado
            elif st.session_state['tipo_valvula'] == "Lineal":
                caudal = apertura
            else:
                caudal = np.sqrt(apertura)
            
            # Dinámica del proceso (1er orden rápido)
            tau_proceso = 10.0 
            PV_real[k] = PV_real[k-1] + (dt / tau_proceso) * (caudal * 150 - PV_real[k-1])
            
            # Dinámica del SENSOR (Aplica el tau calculado por el alumno)
            PV_medido[k] = PV_medido[k-1] + (dt / tau) * (PV_real[k] - PV_medido[k-1])

        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=t_sim, y=SP, mode='lines', name='SetPoint (SP)', line=dict(dash='dot', color='black')))
        fig3.add_trace(go.Scatter(x=t_sim, y=PV_real, mode='lines', name='Temperatura REAL', line=dict(color='green', width=2)))
        fig3.add_trace(go.Scatter(x=t_sim, y=PV_medido, mode='lines', name='Temperatura MEDIDA (Sensor)', line=dict(color='red', width=2)))
        
        fig3.update_layout(title=f"Respuesta del PID ante un sensor con τ={tau:.1f}s", xaxis_title="Tiempo (s)", yaxis_title="Temperatura (ºC)")
        st.plotly_chart(fig3, use_container_width=True)
        
        if tau > 15:
            st.error("⚠️ ¡Inestabilidad! El sensor es tan lento (vaina muy gruesa o bajo flujo) que el controlador actúa a ciegas, causando grandes oscilaciones.")
        elif st.session_state['tipo_valvula'] == "Apertura Rápida":
            st.warning("⚠️ Cuidado: La válvula de apertura rápida inyecta demasiado flujo al principio, causando sobrepasos (Overshoot).")
        else:
            st.success("✅ Control aceptable. El equilibrio entre el sensor y la válvula permite al PID estabilizar el proceso.")

# ==========================================
# FASE 4: EVALUACIÓN E INFORME
# ==========================================
elif fase == "4. Evaluación e Informe":
    st.header("Fase 4: Estudio de Caso y Generación de Informe")
    st.markdown("Responde a las siguientes preguntas basándote en tu experiencia con el simulador. Al finalizar, descarga tu informe para subirlo al Campus Virtual.")
    
    q1 = st.text_area("1. ¿Qué impacto observaste en la Fase 3 al aumentar drásticamente el grosor de la vaina del termopar en la Fase 1? Relaciónalo con la constante de tiempo.", value=st.session_state['q1_respuesta'])
    st.session_state['q1_respuesta'] = q1
    
    q2 = st.text_area("2. Basado en la Fase 2, ¿Por qué en la industria química se suele preferir una válvula 'Isoporcentual' frente a una 'Lineal' cuando hay grandes caídas de presión en la tubería?", value=st.session_state['q2_respuesta'])
    st.session_state['q2_respuesta'] = q2
    
    st.markdown("---")
    
    if st.button("Preparar Informe TXT"):
        if not alumno_nombre or not alumno_id:
            st.error("Por favor, introduce tu Nombre y Matrícula en el menú lateral antes de generar el informe.")
        elif not q1 or not q2:
            st.error("Por favor, responde a todas las preguntas de reflexión.")
        else:
            fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            informe_texto = f"""====================================================
LABORATORIO VIRTUAL - PRÁCTICA 2
====================================================
Asignatura: Control e Instrumentación de Procesos Químicos
Autor Simulador: Jose Joaquin Gonzalez Cortes
Licencia: CC BY-NC-SA 4.0
Fecha de generación: {fecha}

DATOS DEL ALUMNO
----------------------------------------------------
Nombre: {alumno_nombre}
Matrícula/DNI: {alumno_id}

PARÁMETROS SELECCIONADOS EN LA SIMULACIÓN
----------------------------------------------------
- Constante de tiempo del sensor (Tau): {st.session_state['tau_sensor']:.2f} segundos
- Tipo de Válvula seleccionada: {st.session_state['tipo_valvula']}

RESPUESTAS AL ESTUDIO DE CASO
----------------------------------------------------
Pregunta 1: Impacto del grosor de la vaina en el Lazo PID.
Respuesta: {st.session_state['q1_respuesta']}

Pregunta 2: Uso de válvulas isoporcentuales.
Respuesta: {st.session_state['q2_respuesta']}

==================================
