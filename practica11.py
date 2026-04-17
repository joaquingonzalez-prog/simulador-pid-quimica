import streamlit as st
import numpy as np
import plotly.graph_objects as go
import datetime

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA Y METADATOS
# ==========================================
st.set_page_config(page_title="Lab Virtual - Práctica 2", layout="wide")

# Cabecera con los requisitos obligatorios
st.markdown("""
    <div style='background-color: #27ae60; padding: 20px; border-radius: 10px; color: white;'>
        <h2 style='color: white; margin-bottom: 0px;'>Práctica 2: Mecánica de Fluidos - Caudalímetros y Válvulas</h2>
        <p style='margin-bottom: 0px; font-size: 16px;'><b>Asignatura:</b> Control e Instrumentación de Procesos Químicos</p>
        <p style='margin-bottom: 0px; font-size: 16px;'><b>Autor:</b> Jose Joaquin Gonzalez Cortes</p>
        <hr style='margin: 10px 0px; border-color: #2ecc71;'>
        <p style='font-size: 13px; margin-top: 5px; margin-bottom: 0px;'><i>Este material se distribuye bajo licencia CC BY-NC-SA 4.0</i></p>
    </div>
    <br>
""", unsafe_allow_html=True)

# ==========================================
# INICIALIZACIÓN DE ESTADOS (SESSION STATE)
# ==========================================
if 'q1_p2' not in st.session_state: st.session_state['q1_p2'] = ""
if 'q2_p2' not in st.session_state: st.session_state['q2_p2'] = ""
if 'beta_val' not in st.session_state: st.session_state['beta_val'] = 0.5
if 'auth_val' not in st.session_state: st.session_state['auth_val'] = 0.3

# ==========================================
# SIDEBAR: DATOS DEL ALUMNO Y NAVEGACIÓN
# ==========================================
st.sidebar.header("📋 Datos del Alumno")
alumno_nombre = st.sidebar.text_input("Nombre y Apellidos:")
alumno_id = st.sidebar.text_input("DNI / Matrícula:")

st.sidebar.markdown("---")
st.sidebar.header("🧭 Navegación")
fase = st.sidebar.radio("Selecciona la Fase de la práctica:",[
    "1. Medición de Caudal (ΔP)", 
    "2. Pérdida de Carga Permanente", 
    "3. La Válvula de Control", 
    "4. Evaluación e Informe"
])

# ==========================================
# FASE 1: CAUDALÍMETROS DE PRESIÓN DIFERENCIAL
# ==========================================
if fase == "1. Medición de Caudal (ΔP)":
    st.header("Fase 1: Principio de Bernoulli y Restricciones")
    st.markdown("""
    *Referencia: Tema 3 - Medición de Caudal Volumétrico.*
    
    Los caudalímetros de presión diferencial (Placa de Orificio, Venturi, Tobera) se basan en una restricción que reduce el área de flujo. 
    Al aumentar la velocidad en la "vena contracta", disminuye la presión. **El caudal es proporcional a la raíz cuadrada de esta caída de presión (ΔP).**
    """)
    
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.subheader("Parámetros Físicos")
        D_tuberia = st.number_input("Diámetro interno de la tubería D (mm)", value=100.0, step=10.0)
        beta = st.slider("Relación de diámetros (β = d/D)", min_value=0.2, max_value=0.8, value=st.session_state['beta_val'], step=0.05)
        st.session_state['beta_val'] = beta
        
        d_orificio = D_tuberia * beta
        st.info(f"**Diámetro de la restricción (d):** {d_orificio:.1f} mm")
        
        st.latex(r"W = C \cdot d^2 \frac{\sqrt{\rho \cdot \Delta P}}{\sqrt{1-\beta^4}}")
        st.markdown("Al reducir $\\beta$, el orificio es más pequeño, por lo que para pasar el mismo caudal se generará una $\\Delta P$ mucho mayor.")
        
    with col2:
        # dp en kPa (hasta 25 kPa típico como dice el Tema 3 pg 19)
        dp = np.linspace(0, 25, 100) 
        
        # Constante arbitraria para simulación visual proporcional
        C = 0.61 
        K = C * ((d_orificio/100)**2) / np.sqrt(1 - beta**4)
        flujo = K * np.sqrt(dp) * 50 # Escalado visual
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dp, y=flujo, mode='lines', name='Relación Caudal/ΔP', line=dict(color='#2980b9', width=4)))
        
        fig.update_layout(title=f"Curva de Caudal vs ΔP (para β = {beta:.2f})", 
                          xaxis_title="Presión Diferencial Medida ΔP (kPa)", 
                          yaxis_title="Caudal Volumétrico W (L/s)",
                          template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# FASE 2: PÉRDIDA DE CARGA PERMANENTE
# ==========================================
elif fase == "2. Pérdida de Carga Permanente":
    st.header("Fase 2: Comparativa de Tecnologías (OPEX vs CAPEX)")
    st.markdown("""
    *Referencia: Tema 3 - Pérdida de Carga Permanente.*
    
    Toda la presión que cae en el estrechamiento **no se recupera totalmente**. Hay una pérdida permanente por turbulencia y fricción. 
    Esta pérdida significa que la bomba deberá trabajar más (mayor OPEX o coste eléctrico).
    """)
    
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.subheader("Selección del Elemento")
        st.markdown("Arrastra para cambiar el valor de **β (d/D)** y observa cómo cambia la pérdida de energía en las dos tecnologías más usadas.")
        beta_loss = st.slider("Relación de diámetros (β = d/D)", 0.2, 0.8, st.session_state['beta_val'], step=0.05)
        st.session_state['beta_val'] = beta_loss
        
        # Modelos empíricos aproximados visuales
        # Placa Orificio pierde aprox (1 - B^2)*100 %
        perdida_orificio = (1 - beta_loss**2.5) * 100 
        # Venturi recupera muy bien, pierde entre 10 y 15%
        perdida_venturi = 10.0 + (1 - beta_loss) * 5
        
        st.warning(f"**Placa de Orificio:** Pierde un {perdida_orificio:.1f}% de la ΔP generada.\n\n *(Es barata de comprar, pero cara de mantener operando)*.")
        st.success(f"**Tubo Venturi:** Solo pierde un {perdida_venturi:.1f}% de la ΔP generada.\n\n *(Es muy caro de comprar, pero ahora mucha energía de bombeo)*.")
        
    with col2:
        fig2 = go.Figure(data=[
            go.Bar(name='Placa de Orificio (Barata, Turbulenta)', x=['Pérdida Irrecuperable'], y=[perdida_orificio], marker_color='#e74c3c'),
            go.Bar(name='Tubo Venturi (Caro, Aerodinámico)', x=['Pérdida Irrecuperable'], y=[perdida_venturi], marker_color='#27ae60')
        ])
        fig2.update_layout(title=f"Energía Perdida Permanentemente (β = {beta_loss:.2f})", 
                           yaxis_title="% de ΔP perdida para siempre", 
                           barmode='group',
                           yaxis=dict(range=[0, 100]),
                           template="plotly_white")
        st.plotly_chart(fig2, use_container_width=True)

# ==========================================
# FASE 3: LA VÁLVULA DE CONTROL
# ==========================================
elif fase == "3. La Válvula de Control":
    st.header("Fase 3: Curvas Inherentes vs. Instaladas")
    st.markdown("""
    *Referencia: Elementos Finales de Control.*
    
    El fabricante te vende una válvula con una característica ideal (**Inherente**). Pero al instalarla en tu planta, la tubería, los codos y el equipo ofrecen resistencia. 
    Esto hace que la válvula pierda **"Autoridad"**, deformando su curva (Curva **Instalada**).
    """)
    
    col1, col2 = st.columns([1, 1.5])
    with col1:
        tipo_valv = st.radio("Característica Inherente de la Válvula:",["Lineal", "Isoporcentual (Igual Porcentaje)", "Apertura Rápida"])
        
        r = st.slider("Autoridad de la Válvula (a)", min_value=0.05, max_value=1.0, value=st.session_state['auth_val'], step=0.05,
                      help="Relación entre la caída de presión en la válvula y la caída en todo el sistema (a = ΔPv / ΔPsist). a=1 es una válvula ideal sin tuberías.")
        st.session_state['auth_val'] = r
        
        st.info("Si la autoridad **a** es baja (ej. 0.1), significa que la válvula domina poco el sistema y su curva se deformará drásticamente.")
        
    with col2:
        x = np.linspace(0, 1, 100) # % de apertura (0 a 1)
        
        # Curva Inherente f(x)
        if tipo_valv == "Lineal": 
            fx = x
        elif tipo_valv == "Isoporcentual (Igual Porcentaje)": 
            R = 50 # Rangeabilidad
            fx = R**(x - 1)
            fx = (fx - 1/R) / (1 - 1/R) # Forzar que pase por 0,0
        else: 
            fx = np.sqrt(x)
            
        # Ecuación de la curva instalada
        # Q_inst = f(x) / sqrt( a + (1-a)*f(x)^2 )
        fx_inst = fx / np.sqrt(r + (1 - r) * (fx**2))
        
        fig3 = go.Figure()
        # Ideal lineal de referencia
        fig3.add_trace(go.Scatter(x=x*100, y=x*100, mode='lines', name='Lineal Pura (Objetivo PID)', line=dict(dash='dot', color='black', width=1)))
        
        # Curva de fábrica
        fig3.add_trace(go.Scatter(x=x*100, y=fx*100, mode='lines', name='Inherente (En Taller)', line=dict(dash='dash', color='gray', width=3)))
        
        # Curva instalada en planta
        fig3.add_trace(go.Scatter(x=x*100, y=fx_inst*100, mode='lines', name=f'Instalada en Planta (a={r:.2f})', line=dict(color='#8e44ad', width=4)))
        
        fig3.update_layout(title=f"Deformación de la Válvula {tipo_valv}", 
                           xaxis_title="% Apertura del Vástago", 
                           yaxis_title="% Caudal de Fluido",
                           template="plotly_white")
        st.plotly_chart(fig3, use_container_width=True)
        
        if tipo_valv == "Isoporcentual (Igual Porcentaje)" and r < 0.3:
            st.success("💡 **Dato Clave:** Fíjate cómo al bajar la autoridad (tuberías muy largas), la curva Isoporcentual se infla y se acerca peligrosamente a la línea de 'Lineal Pura'. Por eso es la válvula más usada en la industria.")

# ==========================================
# FASE 4: INFORME
# ==========================================
elif fase == "4. Evaluación e Informe":
    st.header("Fase 4: Estudio de Caso e Informe")
    st.markdown("Por favor, reflexiona sobre lo simulado y responde a las siguientes preguntas basadas en la teoría de la asignatura. Cuando termines, descarga el informe para entregarlo.")
    
    q1 = st.text_area("1. Según lo visto en la Fase 2 y en tus apuntes (Tema 3), si debes diseñar un medidor de caudal para una tubería principal con bombas de alta potencia que funcionan 24/7, ¿Elegirías Placa de Orificio o Tubo Venturi? Justifica tu respuesta considerando CAPEX (Coste inicial) y OPEX (Coste de operación/energía).", value=st.session_state['q1_p2'], height=150)
    st.session_state['q1_p2'] = q1
    
    q2 = st.text_area("2. Basado en la Fase 3, ¿Por qué los ingenieros químicos seleccionan mayoritariamente válvulas con característica 'Isoporcentual' en lugar de 'Lineales' si el objetivo del Controlador PID es tener siempre un comportamiento lineal?", value=st.session_state['q2_p2'], height=150)
    st.session_state['q2_p2'] = q2
    
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
LABORATORIO VIRTUAL - PRÁCTICA 2
====================================================
PRÁCTICA: Mecánica de Fluidos en Instrumentación
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
PREGUNTA 1: Selección entre Placa de Orificio y Tubo Venturi (CAPEX vs OPEX).
Respuesta: 
{st.session_state['q1_p2']}

PREGUNTA 2: Selección de Válvulas Isoporcentuales frente a la pérdida de autoridad.
Respuesta: 
{st.session_state['q2_p2']}

====================================================
Documento generado automáticamente por el simulador OCW.
"""
                st.download_button(
                    label="📥 Descargar Informe Completo (.txt)",
                    data=informe_texto,
                    file_name=f"Practica2_{alumno_id}.txt",
                    mime="text/plain"
                )
                st.success("✅ ¡Informe generado con éxito! Pulsa el botón de arriba para descargar.")
