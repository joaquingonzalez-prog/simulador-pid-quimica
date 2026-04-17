import streamlit as st
import numpy as np
import plotly.graph_objects as go
import datetime

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA Y METADATOS
# ==========================================
st.set_page_config(page_title="Lab Virtual - Práctica 1", layout="wide")

# Cabecera con los requisitos obligatorios
st.markdown("""
    <div style='background-color: #2c3e50; padding: 20px; border-radius: 10px; color: white;'>
        <h2 style='color: white; margin-bottom: 0px;'>Práctica 1: Metrología y Transmisión de Señales</h2>
        <p style='margin-bottom: 0px; font-size: 16px;'><b>Asignatura:</b> Control e Instrumentación de Procesos Químicos</p>
        <p style='margin-bottom: 0px; font-size: 16px;'><b>Autor:</b> Jose Joaquin Gonzalez Cortes</p>
        <hr style='margin: 10px 0px; border-color: #7f8c8d;'>
        <p style='font-size: 13px; margin-top: 5px; margin-bottom: 0px;'><i>Este material se distribuye bajo licencia CC BY-NC-SA 4.0</i></p>
    </div>
    <br>
""", unsafe_allow_html=True)

# ==========================================
# INICIALIZACIÓN DE ESTADOS (SESSION STATE)
# ==========================================
# Para guardar las respuestas y que no se borren al cambiar de pestaña
if 'q1_p1' not in st.session_state: st.session_state['q1_p1'] = ""
if 'q2_p1' not in st.session_state: st.session_state['q2_p1'] = ""

# ==========================================
# SIDEBAR: DATOS DEL ALUMNO Y NAVEGACIÓN
# ==========================================
st.sidebar.header("📋 Datos del Alumno")
alumno_nombre = st.sidebar.text_input("Nombre y Apellidos:")
alumno_id = st.sidebar.text_input("DNI / Matrícula:")

st.sidebar.markdown("---")
st.sidebar.header("🧭 Navegación")
fase = st.sidebar.radio("Selecciona la Fase de la práctica:",[
    "1. El Sensor (Termopar)", 
    "2. El Transmisor (4-20 mA)", 
    "3. Errores Estáticos (Histéresis)", 
    "4. Evaluación e Informe"
])

# ==========================================
# FASE 1: EL SENSOR (TERMOPAR Y UNIÓN FRÍA)
# ==========================================
if fase == "1. El Sensor (Termopar)":
    st.header("Fase 1: Principio Termoeléctrico y Unión Fría")
    st.markdown("""
    *Referencia: Tema 2 - Medidores de Temperatura.*
    
    El **termopar** mide la diferencia de temperatura entre la *unión caliente* (proceso) y la *unión fría* (referencia en los bornes del instrumento). 
    Si no compensamos la temperatura ambiente de la unión fría, nuestro sistema de control recibirá una medida errónea.
    """)
    
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.subheader("Simulación del Proceso")
        t_caliente = st.slider("Temperatura del Proceso (Unión Caliente) [ºC]", min_value=0.0, max_value=1000.0, value=350.0, step=10.0)
        t_ambiente = st.slider("Temperatura Ambiente (Unión Fría) [ºC]", min_value=-10.0, max_value=50.0, value=25.0, step=1.0)
        
        compensacion = st.toggle("Activar Compensación de Unión Fría (Hardware/Software)")
        
        # Sensibilidad típica de un Termopar Tipo K (~41 uV/ºC) para simplificar
        k_sens = 0.041 
        
        # Matemáticas de la FEM (Fuerza electromotriz)
        fem_generada = k_sens * (t_caliente - t_ambiente)
        
        if compensacion:
            fem_compensacion = k_sens * t_ambiente
            fem_total = fem_generada + fem_compensacion
            t_medida = fem_total / k_sens
            estado = "✅ Medida correcta y compensada"
            color_delta = "green"
        else:
            t_medida = fem_generada / k_sens
            estado = "⚠️ ¡Error! El sistema lee una temperatura menor a la real."
            color_delta = "red"
            
        error_absoluto = t_caliente - t_medida
        
        st.markdown("### Resultados del Instrumento")
        st.write(f"**F.E.M Generada por el cable:** {fem_generada:.3f} mV")
        if compensacion:
            st.write(f"**F.E.M de Compensación añadida:** + {fem_compensacion:.3f} mV")
        st.info(estado)

    with col2:
        # Gráfico tipo Velocímetro para ver la diferencia
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = t_medida,
            title = {'text': "Temperatura Interpretada por el PLC (ºC)", 'font': {'size': 20}},
            delta = {'reference': t_caliente, 'increasing': {'color': color_delta}, 'decreasing': {'color': color_delta}},
            gauge = {
                'axis': {'range': [0, 1000], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "darkblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': t_caliente}
            }
        ))
        st.plotly_chart(fig, use_container_width=True)
        st.caption("La línea roja indica la temperatura real del proceso. El indicador azul es la temperatura que 'cree' que hay el sistema.")

# ==========================================
# FASE 2: EL TRANSMISOR (4-20 mA)
# ==========================================
elif fase == "2. El Transmisor (4-20 mA)":
    st.header("Fase 2: Calibración del Transmisor y 'Cero Vivo'")
    st.markdown("""
    *Referencia: Tema 1 - Transmisión de la medida.*
    
    La temperatura medida por el sensor debe enviarse al controlador a través de un cable eléctrico. En la industria química, el estándar absoluto es el lazo de corriente de **4 a 20 mA**. 
    Vamos a configurar el *Alcance* (Span) definiendo el Valor Inferior (LRV) y Superior (URV).
    """)
    
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.subheader("Configuración de Rango")
        lrv = st.number_input("Valor Inferior del Rango (LRV) [ºC]", value=0.0, step=10.0)
        urv = st.number_input("Valor Superior del Rango (URV) [ºC]", value=500.0, step=10.0)
        
        if lrv >= urv:
            st.error("El URV debe ser mayor que el LRV.")
            span = 0
        else:
            span = urv - lrv
            st.success(f"**Alcance (Span):** {span} ºC")
            
        st.markdown("---")
        t_actual = st.slider("Simular Temperatura Actual [ºC]", min_value=lrv-50.0, max_value=urv+50.0, value=(lrv+urv)/2)
        
        # Ecuación de la recta del transmisor
        if span != 0:
            mA_teorico = 4.0 + 16.0 * ((t_actual - lrv) / span)
            # Saturación física del transmisor (no puede bajar de 3.8 ni subir de 20.5 aprox)
            mA_real = np.clip(mA_teorico, 3.8, 20.5)
        else:
            mA_teorico = mA_real = 0
            
        st.metric(label="Señal de Corriente Transmitida", value=f"{mA_real:.2f} mA")
        if mA_teorico < 3.8 or mA_teorico > 20.5:
            st.warning("⚠️ El transmisor está SATURADO (fuera de rango).")
            
    with col2:
        if span != 0:
            x_vals = np.linspace(lrv-50, urv+50, 200)
            y_teorico = 4.0 + 16.0 * ((x_vals - lrv) / span)
            y_real = np.clip(y_teorico, 3.8, 20.5)
            
            fig2 = go.Figure()
            # Curva real con saturación
            fig2.add_trace(go.Scatter(x=x_vals, y=y_real, mode='lines', name='Respuesta Real Transmisor', line=dict(color='#e67e22', width=4)))
            # Curva teórica infinita
            fig2.add_trace(go.Scatter(x=x_vals, y=y_teorico, mode='lines', name='Extrapolación Teórica', line=dict(color='gray', width=2, dash='dot')))
            
            # Punto de operación
            fig2.add_trace(go.Scatter(x=[t_actual], y=[mA_real], mode='markers', name='Operación Actual', marker=dict(color='red', size=14, symbol='x')))
            
            # Líneas límite
            fig2.add_hline(y=4, line_dash="dash", line_color="#2980b9", annotation_text="Cero Vivo (4 mA)")
            fig2.add_hline(y=20, line_dash="dash", line_color="#2980b9", annotation_text="Fondo de Escala (20 mA)")
            
            fig2.update_layout(title="Curva de Calibración del Transmisor", xaxis_title="Temperatura Variable de Proceso (ºC)", yaxis_title="Señal Eléctrica (mA)", template="plotly_white")
            st.plotly_chart(fig2, use_container_width=True)

# ==========================================
# FASE 3: ERRORES ESTÁTICOS (HISTÉRESIS)
# ==========================================
elif fase == "3. Errores Estáticos (Histéresis)":
    st.header("Fase 3: Características Estáticas de los Instrumentos")
    st.markdown("""
    *Referencia: Tema 1 - Definiciones.*
    
    Los instrumentos mecánicos (como manómetros o válvulas) rara vez son ideales. Uno de los mayores problemas es la **Histéresis**: la diferencia en la medida dependiendo de si la variable está aumentando o disminuyendo (por culpa de rozamientos o deformaciones elásticas).
    """)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Configurar Instrumento")
        hist_percent = st.slider("Porcentaje de Histéresis (% del Rango)", 0.0, 20.0, 8.0, step=1.0)
        
        st.markdown(f"""
        **¿Qué significa esto?**
        Significa que si la temperatura real es del 50%, tu instrumento leerá un valor diferente si el sistema se está calentando que si se está enfriando.
        El error máximo absoluto será de **{hist_percent} %** entre ambas trayectorias.
        """)
        
    with col2:
        # Generar ciclo de histéresis visual
        x_ideal = np.linspace(0, 100, 100)
        
        # Simulación de la desviación
        offset = hist_percent / 2.0
        y_subida = np.clip(x_ideal - offset, 0, 100)
        y_bajada = np.clip(x_ideal + offset, 0, 100)
        
        fig3 = go.Figure()
        # Línea Ideal
        fig3.add_trace(go.Scatter(x=x_ideal, y=x_ideal, mode='lines', name='Comportamiento Ideal', line=dict(dash='dot', color='black', width=2)))
        # Subida
        fig3.add_trace(go.Scatter(x=x_ideal, y=y_subida, mode='lines', name='Curva de Subida (Calentamiento)', line=dict(color='#e74c3c', width=3)))
        # Bajada
        fig3.add_trace(go.Scatter(x=x_ideal, y=y_bajada, mode='lines', name='Curva de Bajada (Enfriamiento)', line=dict(color='#3498db', width=3)))
        
        # Cerrar el ciclo (Líneas verticales en los extremos para estética de histéresis)
        fig3.add_trace(go.Scatter(x=[100, 100], y=[y_subida[-1], y_bajada[-1]], mode='lines', showlegend=False, line=dict(color='gray', width=1)))
        fig3.add_trace(go.Scatter(x=[0, 0], y=[y_subida[0], y_bajada[0]], mode='lines', showlegend=False, line=dict(color='gray', width=1)))
        
        fig3.update_layout(title=f"Lazo de Histéresis ({hist_percent}%)", 
                           xaxis_title="Valor Real de la Variable (%)", 
                           yaxis_title="Lectura del Instrumento (%)",
                           template="plotly_white")
        st.plotly_chart(fig3, use_container_width=True)

# ==========================================
# FASE 4: INFORME
# ==========================================
elif fase == "4. Evaluación e Informe":
    st.header("Fase 4: Estudio de Caso y Generación de Informe")
    st.markdown("Por favor, reflexiona sobre lo simulado y responde a las siguientes preguntas basadas en la teoría de la asignatura. Cuando termines, descarga el informe para entregarlo.")
    
    q1 = st.text_area("1. Según lo visto en la Fase 1 y en tus apuntes (Tema 2), ¿Por qué el termopar marca una temperatura inferior a la real cuando no hay compensación de unión fría? Explícalo usando la Ley de Temperaturas Intermedias.", value=st.session_state['q1_p1'], height=150)
    st.session_state['q1_p1'] = q1
    
    q2 = st.text_area("2. En la Fase 2, hemos usado el estándar eléctrico 4-20 mA. ¿Cuál es el motivo principal de seguridad industrial por el que se utiliza un 'cero vivo' (4 mA) en lugar de transmitir de 0 a 20 mA? (Pista: Piensa en qué pasa si se rompe el cable).", value=st.session_state['q2_p1'], height=150)
    st.session_state['q2_p1'] = q2
    
    st.markdown("---")
    
    col_btn, _ = st.columns([1, 2])
    with col_btn:
        if st.button("📄 Previsualizar y Generar Informe TXT", type="primary"):
            if not alumno_nombre or not alumno_id:
                st.error("⚠️ Falta información: Introduce tu Nombre y Matrícula en el panel lateral.")
            elif not q1 or not q2:
                st.error("⚠️ Responde a todas las preguntas antes de generar el informe.")
            else:
                fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                informe_texto = f"""====================================================
LABORATORIO VIRTUAL - PRÁCTICA 1
====================================================
PRÁCTICA: Metrología y Transmisión de Señales
ASIGNATURA: Control e Instrumentación de Procesos Químicos
AUTOR: Jose Joaquin Gonzalez Cortes
LICENCIA: CC BY-NC-SA 4.0
FECHA DE GENERACIÓN: {fecha}

DATOS DEL ALUMNO
----------------------------------------------------
Nombre: {alumno_nombre}
Matrícula/DNI: {alumno_id}

RESPUESTAS AL ESTUDIO DE CASO
----------------------------------------------------
PREGUNTA 1: Compensación de la Unión Fría en Termopares.
Respuesta: 
{st.session_state['q1_p1']}

PREGUNTA 2: Justificación del "Cero Vivo" en el estándar 4-20 mA.
Respuesta: 
{st.session_state['q2_p1']}

====================================================
Documento generado automáticamente por el simulador OCW.
"""
                st.download_button(
                    label="📥 Descargar Informe Completo (.txt)",
                    data=informe_texto,
                    file_name=f"Practica1_{alumno_id}.txt",
                    mime="text/plain"
                )
                st.success("✅ ¡Informe generado con éxito! Pulsa el botón de arriba para descargar.")
