import streamlit as st
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# CONFIGURACIÓN Y ESTILOS
# ==========================================
st.set_page_config(page_title="Práctica 2 - Válvulas de Control", layout="wide")

# Estilo para los encabezados de sección
def local_css(file_name):
    st.markdown(f'<style>{file_name}</style>', unsafe_allow_html=True)

# ==========================================
# CONSTANTES Y METADATOS
# ==========================================
ASIGNATURA = "Control e Instrumentación de Procesos Químicos"
AUTOR = "José Joaquín González Cortés"
LICENCIA = "CC BY-NC-SA 4.0"

# ==========================================
# LÓGICA MATEMÁTICA
# ==========================================
def calc_curvas(tipo, autoridad, R=50):
    x = np.linspace(0, 1, 100)
    # Característica Inherente
    if tipo == "Lineal":
        f_x = x
    elif tipo == "Igual Porcentaje (EP)":
        f_x = R**(x - 1)
    else: # Apertura Rápida
        f_x = np.sqrt(x)
    
    # Característica Instalada
    a = max(autoridad, 0.01)
    y_inst = f_x / np.sqrt(a + (1 - a) * f_x**2)
    return x, f_x, y_inst

# ==========================================
# INTERFAZ DE USUARIO (TABS)
# ==========================================
st.title("🧪 Laboratorio Virtual: Caracterización de Válvulas")
st.caption(f"**Asignatura:** {ASIGNATURA} | **Autor:** {AUTOR}")

tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Objetivos y Fundamento", 
    "🕹️ Simulador Interactivo", 
    "📝 Cuestionario", 
    "📥 Generar Informe"
])

# --- TAB 1: OBJETIVOS ---
with tab1:
    st.header("1. Objetivos de la Práctica")
    st.markdown(f"""
    En esta sesión de laboratorio virtual, el alumno deberá:
    * **Comprender** la diferencia entre la característica *inherente* (catálogo) y la *instalada* (real).
    * **Analizar** el concepto de **Autoridad de la Válvula ($a$)** y cómo la pérdida de carga en la tubería deforma la respuesta del proceso.
    * **Seleccionar** el obturador óptimo para diferentes escenarios industriales buscando la **linealidad** del lazo de control.
    
    **Instrucciones:** 1. Ve a la pestaña 'Simulador' y prueba los 3 escenarios propuestos.
    2. Analiza las gráficas y observa el error de linealidad.
    3. Responde a las preguntas de la pestaña 'Cuestionario' basándote en tus observaciones.
    """)
    st.info(f"Este material se distribuye bajo licencia {LICENCIA}")

# --- TAB 2: SIMULADOR ---
with tab2:
    st.header("2. Experimentación y Análisis")
    
    col_input, col_plot = st.columns([1, 2])
    
    with col_input:
        st.subheader("Configuración de Planta")
        nombre_alumno = st.text_input("Nombre del Alumno", placeholder="Introduce tu nombre completo")
        
        escenario = st.radio(
            "Selecciona un Escenario Industrial:",
            ["A: Línea corta (Alta Autoridad a=0.9)", 
             "B: Línea estándar (Autoridad media a=0.5)", 
             "C: Línea muy larga (Baja Autoridad a=0.15)"]
        )
        
        # Seteo automático de autoridad según escenario pero permitiendo ajuste fino
        val_aut = 0.9 if "A:" in escenario else (0.5 if "B:" in escenario else 0.15)
        a_user = st.slider("Ajuste fino de Autoridad (a)", 0.05, 1.0, val_aut)
        
        tipo_v = st.selectbox("Tipo de Obturador de la Válvula:", 
                             ["Lineal", "Igual Porcentaje (EP)", "Apertura Rápida"])
        
        st.divider()
        st.write("**Datos en Tiempo Real:**")
        x, f_x, y_inst = calc_curvas(tipo_v, a_user)
        # Error de linealidad: desviación media respecto a la recta y=x
        error = np.mean(np.abs(y_inst - x)) * 100
        st.metric("Desviación de Linealidad", f"{error:.2f} %")

    with col_plot:
        fig = go.Figure()
        # Curva instalada
        fig.add_trace(go.Scatter(x=x*100, y=y_inst*100, name="C. Instalada (Real)", 
                                line=dict(color='red', width=4)))
        # Curva inherente
        fig.add_trace(go.Scatter(x=x*100, y=f_x*100, name="C. Inherente (Catálogo)", 
                                line=dict(color='blue', dash='dash')))
        # Referencia ideal
        fig.add_trace(go.Scatter(x=[0, 100], y=[0, 100], name="Ideal Lineal", 
                                line=dict(color='gray', dash='dot')))
        
        fig.update_layout(title=f"Respuesta de la Válvula (Autoridad = {a_user})",
                        xaxis_title="Apertura del vástago (%)",
                        yaxis_title="Caudal relativo (%)",
                        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 3: CUESTIONARIO ---
with tab3:
    st.header("3. Evaluación del Estudio de Caso")
    st.write("Responde a las siguientes preguntas basándote en tus experimentos en el simulador:")
    
    q1 = st.text_area("1. ¿Qué sucede con la curva 'Lineal' cuando la autoridad (a) cae por debajo de 0.2? Justifica si es fácil o difícil de controlar.")
    
    q2 = st.text_area("2. En el Escenario C (Baja autoridad), ¿qué tipo de válvula compensa mejor la pérdida de carga del sistema para mantener una respuesta casi lineal?")
    
    q3 = st.text_area("3. Explica brevemente por qué es deseable que la característica INSTALADA sea lineal en un lazo de control con PID.")

# --- TAB 4: REPORTE ---
with tab4:
    st.header("4. Finalizar y Exportar")
    
    if not nombre_alumno:
        st.error("⚠️ Debes introducir tu nombre en la pestaña 'Simulador' para generar el informe.")
    else:
        # Construcción del contenido del TXT
        reporte = f"""=======================================================
INFORME DE LABORATORIO VIRTUAL - OCW
Asignatura: {ASIGNATURA}
Autor del Software: {AUTOR}
Licencia: {LICENCIA}
=======================================================

DATOS DEL ALUMNO:
Nombre: {nombre_alumno}
Fecha de realización: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

RESULTADOS DE LA EXPERIMENTACIÓN:
- Último escenario probado: {escenario}
- Autoridad final utilizada: {a_user}
- Obturador seleccionado: {tipo_v}
- Error de linealidad final: {error:.2f}%

RESPUESTAS AL CUESTIONARIO:
Pregunta 1: {q1}

Pregunta 2: {q2}

Pregunta 3: {q3}

-------------------------------------------------------
Validación: Este documento sirve como comprobante de
realización de la Práctica 2 en el entorno virtual.
-------------------------------------------------------
"""
        st.text_area("Previsualización del informe:", reporte, height=300)
        
        st.download_button(
            label="💾 Descargar Informe .txt",
            data=reporte,
            file_name=f"Practica2_{nombre_alumno.replace(' ','_')}.txt",
            mime="text/plain",
            type="primary"
        )
