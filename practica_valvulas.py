import streamlit as st
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="Práctica 2: Válvulas de Control", layout="wide")

# ==========================================
# FUNCIONES MATEMÁTICAS (MODELO)
# ==========================================
def caracteristica_inherente(x, tipo_valvula, R=50):
    """Calcula el caudal relativo ideal f(x) según el tipo de obturador."""
    if tipo_valvula == "Lineal":
        return x
    elif tipo_valvula == "Igual Porcentaje (Equal %)":
        # Evitamos x=0 exacto para la fórmula exponencial matemática
        x_safe = np.where(x == 0, 0.001, x)
        return R**(x_safe - 1)
    elif tipo_valvula == "Apertura Rápida":
        return np.sqrt(x)

def caracteristica_instalada(f_x, autoridad):
    """Calcula el caudal relativo real considerando la pérdida de carga del sistema."""
    # Evitamos división por cero si la autoridad es 0
    a = max(autoridad, 0.01) 
    # Fórmula clásica de la característica instalada
    return f_x / np.sqrt(a + (1 - a) * f_x**2)

# ==========================================
# INTERFAZ DE USUARIO (UI)
# ==========================================
st.title("🎛️ Laboratorio Virtual OCW - Práctica 2")
st.subheader("Dimensionamiento y Caracterización de Válvulas de Control")

st.markdown("""
**Estudio de Caso:** Eres el ingeniero de instrumentación de una planta química. Debes seleccionar una válvula 
para controlar el caudal de un intercambiador de calor. Debido a las tuberías de la instalación, la válvula 
no absorberá toda la caída de presión del sistema (esto se mide con la **Autoridad, $a$**). 
**Tu objetivo:** Seleccionar el *Tipo de Obturador* adecuado para que, al estar instalada, la respuesta del 
caudal frente al movimiento del vástago sea **lo más lineal posible**.
""")

st.divider()

# -- Paneles de Control --
col1, col2 = st.columns([1, 3])

with col1:
    st.header("⚙️ Parámetros")
    
    tipo_valvula = st.selectbox(
        "1. Tipo de Obturador",
        ["Lineal", "Igual Porcentaje (Equal %)", "Apertura Rápida"]
    )
    
    autoridad = st.slider(
        "2. Autoridad de la válvula (a)", 
        min_value=0.1, max_value=1.0, value=0.5, step=0.05,
        help="a = ΔP_válvula / ΔP_total. Un valor de 1.0 significa que no hay tuberías que roben presión (ideal). Un valor bajo (0.1) simula una tubería muy larga."
    )
    
    apertura_actual = st.slider(
        "3. Posición del Vástago (%)", 
        min_value=0, max_value=100, value=50, step=1
    ) / 100.0  # Lo pasamos a tanto por uno

# -- Cálculos y Gráficas --
with col2:
    # Vector de aperturas (0 a 1)
    x_array = np.linspace(0, 1, 100)
    
    # Cálculos vectorizados para las curvas
    f_x_array = caracteristica_inherente(x_array, tipo_valvula)
    y_inst_array = caracteristica_instalada(f_x_array, autoridad)
    
    # Cálculos puntuales (para el valor actual del slider)
    f_x_actual = caracteristica_inherente(apertura_actual, tipo_valvula)
    y_inst_actual = caracteristica_instalada(f_x_actual, autoridad)
    
    # GRÁFICA PRINCIPAL (Plotly)
    fig = go.Figure()

    # Curva Inherente (Catálogo)
    fig.add_trace(go.Scatter(
        x=x_array*100, y=f_x_array*100, 
        mode='lines', name='C. Inherente (Teórica)',
        line=dict(color='blue', dash='dash')
    ))
    
    # Curva Instalada (Real)
    fig.add_trace(go.Scatter(
        x=x_array*100, y=y_inst_array*100, 
        mode='lines', name='C. Instalada (Real en planta)',
        line=dict(color='red', width=3)
    ))
    
    # Punto actual de operación
    fig.add_trace(go.Scatter(
        x=[apertura_actual*100], y=[y_inst_actual*100],
        mode='markers', name='Punto de Operación',
        marker=dict(color='black', size=12, symbol='x')
    ))

    # Referencia Lineal Ideal
    fig.add_trace(go.Scatter(
        x=[0, 100], y=[0, 100], 
        mode='lines', name='Comportamiento Lineal Ideal',
        line=dict(color='green', width=1, dash='dot')
    ))

    fig.update_layout(
        title="Curvas de la Válvula: Inherente vs Instalada",
        xaxis_title="Apertura del Vástago (%)",
        yaxis_title="Caudal Relativo (%)",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# MÉTRICAS Y EVALUACIÓN (INFORME)
# ==========================================
st.divider()
st.header("📊 Resultados del Estudio de Caso")

col_res1, col_res2, col_res3 = st.columns(3)
col_res1.metric(label="Caudal Teórico (Inherente)", value=f"{f_x_actual*100:.1f} %")
col_res2.metric(label="Caudal Real (Instalado)", value=f"{y_inst_actual*100:.1f} %", delta=f"{(y_inst_actual - f_x_actual)*100:.1f} % de desvío")

# Lógica de evaluación simple
error_linealidad = np.mean(np.abs(y_inst_array - x_array))
es_optimo = error_linealidad < 0.15 # Umbral de tolerancia

if es_optimo:
    st.success("✅ ¡Buen trabajo! Con esta configuración (Válvula + Autoridad), la curva instalada se aproxima bastante a un comportamiento lineal. Esto facilitará la sintonía del PID.")
else:
    st.warning("⚠️ La curva instalada está muy deformada respecto a la linealidad. En la vida real, el controlador PID (Práctica 1) se volvería inestable a bajos o altos caudales. ¡Prueba otra combinación!")

# -- Generación del Informe TXT --
informe_texto = f"""
LABORATORIO VIRTUAL OCW - CONTROL E INSTRUMENTACIÓN
---------------------------------------------------
PRACTICA 2: DIMENSIONAMIENTO DE VÁLVULAS DE CONTROL
Fecha y Hora de la simulación: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

--- PARÁMETROS CONFIGURADOS POR EL ALUMNO ---
Tipo de Válvula Seleccionada : {tipo_valvula}
Autoridad de la Válvula (a)  : {autoridad:.2f}
Apertura Final del Vástago   : {apertura_actual*100:.1f} %

--- RESULTADOS ---
Caudal Relativo Inherente    : {f_x_actual*100:.1f} %
Caudal Relativo Instalado    : {y_inst_actual*100:.1f} %
Desviación de linealidad     : {error_linealidad*100:.1f} %

--- CONCLUSIÓN TÉCNICA ---
{"El alumno logró una configuración con un comportamiento cuasi-lineal óptimo para el lazo de control." if es_optimo else "La configuración elegida presenta una alta no linealidad, dificultando el control regulatorio."}

---------------------------------------------------
Firma Digital del Simulador
"""

st.download_button(
    label="📄 Descargar Informe en .txt para subir al Campus",
    data=informe_texto,
    file_name="informe_practica2_valvulas.txt",
    mime="text/plain",
    type="primary"
)
