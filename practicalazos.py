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
    **Problema Térmico:** El crecimiento microbiano genera un aumento rápido de temperatura en el fermentador que debe ser controlada a través del paso de agua de refrigeración en el encamis
