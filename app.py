"""
===============================================================
 Simulador Didáctico de Controlador PID — Reactor Químico
 Para estudiantes de Ingeniería Química / Control de Procesos
===============================================================
Ejecutar con:  streamlit run pid_reactor_simulator.py
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.integrate import odeint

# ──────────────────────────────────────────────────
# Configuración de la página
# ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Simulador PID – Reactor Químico",
    page_icon="⚗️",
    layout="wide",
)

# ──────────────────────────────────────────────────
# CSS personalizado
# ──────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title   {font-size:2.2rem; font-weight:700; color:#1a3a5c; text-align:center;}
    .subtitle     {font-size:1.1rem; color:#4a6fa5; text-align:center; margin-bottom:1rem;}
    .section-hdr  {font-size:1.2rem; font-weight:600; color:#1a3a5c;
                   border-left:4px solid #4a6fa5; padding-left:0.5rem; margin-top:1rem;}
    .info-box     {background:#eaf1fb; border-radius:8px; padding:1rem; margin:0.5rem 0;
                   border:1px solid #b3cde8;}
    .warn-box     {background:#fff8e1; border-radius:8px; padding:1rem; margin:0.5rem 0;
                   border:1px solid #ffe082;}
    .good-box     {background:#e8f5e9; border-radius:8px; padding:1rem; margin:0.5rem 0;
                   border:1px solid #a5d6a7;}
    .formula      {background:#f5f5f5; border-radius:6px; padding:0.6rem 1rem;
                   font-family:monospace; font-size:1rem; margin:0.4rem 0;}
    .metric-label {font-size:0.85rem; color:#555;}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────
# Encabezado
# ──────────────────────────────────────────────────
st.markdown('<div class="main-title">⚗️ Simulador Didáctico de Controlador PID</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Aplicado al control de temperatura en un reactor de tanque agitado (CSTR)</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Autor:José Joaquín González Cortés</div>', unsafe_allow_html=True)
st.divider()

# ──────────────────────────────────────────────────
# Sidebar — Parámetros del controlador y proceso
# ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Panel de Control")
    st.markdown("---")

    st.markdown("### Parámetros PID")
    Kp = st.slider("**Kp** — Ganancia Proporcional", 0.1, 20.0, 2.0, 0.1,
                   help="Amplifica el error actual. Valores altos → respuesta más rápida pero posible inestabilidad.")
    Ki = st.slider("**Ki** — Ganancia Integral", 0.0, 5.0, 0.5, 0.05,
                   help="Elimina el error en estado estacionario. Valores altos → oscilaciones y sobre-amortiguamiento.")
    Kd = st.slider("**Kd** — Ganancia Derivativa", 0.0, 5.0, 0.3, 0.05,
                   help="Amortigua oscilaciones prediciendo el comportamiento futuro del error.")

    st.markdown("---")
    st.markdown("### ⚙️ Parámetros del Proceso")
    T_setpoint = st.slider("**Temperatura deseada (SP)** [°C]", 50, 150, 100, 5)
    T_initial  = st.slider("**Temperatura inicial** [°C]", 20, 100, 25, 5)
    tau_p      = st.slider("**Constante de tiempo del proceso** τ [min]", 1.0, 20.0, 5.0, 0.5,
                           help="Qué tan lento responde térmicamente el reactor.")
    K_process  = st.slider("**Ganancia del proceso** Kₚ", 0.5, 5.0, 1.5, 0.1,
                           help="Sensibilidad del reactor a la acción de control.")
    dead_time  = st.slider("**Tiempo muerto** θ [min]", 0.0, 3.0, 0.5, 0.1,
                           help="Retardo puro antes de que el proceso reaccione al control.")

    st.markdown("---")
    st.markdown("### 📐 Simulación")
    t_end   = st.slider("Tiempo total [min]", 10, 120, 40, 5)
    dt      = st.select_slider("Paso de tiempo Δt [min]", options=[0.01, 0.02, 0.05, 0.1], value=0.05)
    disturbance_on = st.checkbox("Agregar perturbación al proceso", value=False)
    if disturbance_on:
        t_dist = st.slider("Tiempo de perturbación [min]", 5, t_end-5, 20, 1)
        mag_dist = st.slider("Magnitud perturbación [°C]", -30, 30, -10, 1)

# ──────────────────────────────────────────────────
# Motor de simulación PID
# ──────────────────────────────────────────────────
def simulate_pid(Kp, Ki, Kd, setpoint, T0, tau_p, K_proc, dead_time, dt, t_end,
                 disturbance_on=False, t_dist=20, mag_dist=-10):
    """
    Simula un controlador PID sobre un proceso de primer orden con tiempo muerto.
    Modelo del proceso (discreto):
        T[k+1] = T[k] + dt/tau_p * ( -T[k] + T0 + K_proc * u[k_dead] )
    """
    N = int(t_end / dt)
    t = np.linspace(0, t_end, N)

    T        = np.zeros(N)
    u        = np.zeros(N)   # señal de control (potencia al calentador)
    error    = np.zeros(N)
    integral = 0.0
    prev_err = 0.0

    T[0] = T0
    dead_steps = max(1, int(dead_time / dt))

    # Buffer de tiempo muerto
    u_buffer = [0.0] * dead_steps

    u_min, u_max = 0.0, 100.0  # límites anti-windup

    for k in range(N - 1):
        # Perturbación escalón
        if disturbance_on and t[k] >= t_dist:
            sp_eff = setpoint
            T[k] += mag_dist * dt / tau_p if k == int(t_dist / dt) else 0
        sp_eff = setpoint

        # Error
        e = sp_eff - T[k]
        error[k] = e

        # Término integral con anti-windup
        integral += e * dt
        integral = np.clip(integral, -500, 500)

        # Término derivativo
        derivative = (e - prev_err) / dt
        prev_err = e

        # Ley de control PID
        u_raw = Kp * e + Ki * integral + Kd * derivative
        u[k]  = np.clip(u_raw, u_min, u_max)

        # Tiempo muerto: usar la señal de control retrasada
        u_buffer.append(u[k])
        u_delayed = u_buffer.pop(0)

        # Modelo del proceso: reactor de primer orden
        dT = (dt / tau_p) * (-T[k] + T0 + K_proc * u_delayed)
        # Perturbación como escalón en temperatura
        if disturbance_on and abs(t[k] - t_dist) < dt:
            dT += mag_dist
        T[k + 1] = T[k] + dT

    error[N-1] = setpoint - T[N-1]
    return t, T, u, error


# ──────────────────────────────────────────────────
# Ejecutar simulación
# ──────────────────────────────────────────────────
dist_kwargs = dict(disturbance_on=disturbance_on,
                   t_dist=t_dist if disturbance_on else 20,
                   mag_dist=mag_dist if disturbance_on else 0)

t, T, u, error = simulate_pid(
    Kp, Ki, Kd,
    T_setpoint, T_initial,
    tau_p, K_process,
    dead_time, dt, t_end,
    **dist_kwargs
)

# ──────────────────────────────────────────────────
# Métricas de desempeño
# ──────────────────────────────────────────────────
sp = T_setpoint
T_ss = T[-1]
overshoot = max(0, (T.max() - sp) / (sp - T_initial) * 100) if sp != T_initial else 0

# Tiempo de subida (10% → 90%)
band_lo = T_initial + 0.10 * (sp - T_initial)
band_hi = T_initial + 0.90 * (sp - T_initial)
idx_lo  = np.argmax(T >= band_lo)
idx_hi  = np.argmax(T >= band_hi) if np.any(T >= band_hi) else -1
rise_time = (t[idx_hi] - t[idx_lo]) if idx_hi > 0 else np.nan

# Tiempo de asentamiento (±2%)
tol = 0.02 * abs(sp - T_initial)
settled = np.where(np.abs(T - sp) <= tol)[0]
settle_time = t[settled[0]] if len(settled) > 0 else np.nan

sse = np.mean(error[-50:]**2)   # Error cuadrático medio en estado final

# ──────────────────────────────────────────────────
# Layout principal — columnas
# ──────────────────────────────────────────────────
col_graph, col_info = st.columns([3, 1])

with col_graph:
    # ── Gráfica principal ──
    fig = plt.figure(figsize=(10, 8), facecolor="#f8fafc")
    gs  = gridspec.GridSpec(3, 1, hspace=0.45)

    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])
    ax3 = fig.add_subplot(gs[2])

    # Paleta
    c_sp    = "#e74c3c"
    c_T     = "#2980b9"
    c_u     = "#27ae60"
    c_err   = "#8e44ad"

    # — Panel 1: Temperatura —
    ax1.plot(t, T, color=c_T, lw=2, label="Temperatura del reactor T(t)")
    ax1.axhline(sp, color=c_sp, ls="--", lw=1.5, label=f"Set-point = {sp} °C")
    ax1.fill_between(t, sp - abs(sp-T_initial)*0.02, sp + abs(sp-T_initial)*0.02,
                     color=c_sp, alpha=0.08, label="Banda ±2%")
    if disturbance_on:
        ax1.axvline(t_dist, color="orange", ls=":", lw=1.5, label="Perturbación")
    ax1.set_ylabel("Temperatura [°C]", fontsize=10)
    ax1.set_title("Respuesta del Sistema — Temperatura", fontsize=11, fontweight="bold")
    ax1.legend(fontsize=8, loc="upper right")
    ax1.grid(True, alpha=0.3)
    ax1.set_facecolor("#f0f4f8")

    # — Panel 2: Señal de control —
    ax2.plot(t, u, color=c_u, lw=2, label="Señal de control u(t) [%]")
    ax2.axhline(0,   color="gray", ls="-",  lw=0.5)
    ax2.axhline(100, color="gray", ls="--", lw=0.8, alpha=0.5, label="Límite saturación")
    ax2.set_ylabel("Control u(t) [%]", fontsize=10)
    ax2.set_title("Acción de Control (Potencia al Calentador)", fontsize=11, fontweight="bold")
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)
    ax2.set_facecolor("#f0f4f8")
    ax2.set_ylim(-5, 110)

    # — Panel 3: Error —
    ax3.plot(t, error, color=c_err, lw=2, label="Error e(t) = SP − T(t)")
    ax3.axhline(0, color="gray", ls="--", lw=1)
    ax3.fill_between(t, error, 0, alpha=0.15, color=c_err)
    ax3.set_ylabel("Error [°C]", fontsize=10)
    ax3.set_xlabel("Tiempo [min]", fontsize=10)
    ax3.set_title("Error del Sistema", fontsize=11, fontweight="bold")
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)
    ax3.set_facecolor("#f0f4f8")

    fig.suptitle(f"PID: Kp={Kp}  Ki={Ki}  Kd={Kd}",
                 fontsize=12, fontweight="bold", color="#1a3a5c", y=0.98)

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

with col_info:
    st.markdown('<div class="section-hdr">📊 Indicadores de Desempeño</div>', unsafe_allow_html=True)

    st.metric("Temperatura final", f"{T_ss:.1f} °C", f"{T_ss - sp:.1f} °C vs SP")
    st.metric("Sobre-amortiguamiento", f"{overshoot:.1f} %")
    st.metric("Tiempo de subida",  f"{rise_time:.2f} min"   if not np.isnan(rise_time)   else "N/A")
    st.metric("Tiempo asentamiento", f"{settle_time:.2f} min" if not np.isnan(settle_time) else "N/A")
    st.metric("Error cuadrático (estado final)", f"{sse:.3f} °C²")

    st.markdown("---")
    # Diagnóstico automático
    if overshoot > 20:
        st.markdown('<div class="warn-box">⚠️ <b>Sobre-amortiguamiento alto</b><br>Reduce Kp o aumenta Kd para suavizar la respuesta.</div>', unsafe_allow_html=True)
    elif not np.isnan(settle_time) and settle_time < 5:
        st.markdown('<div class="good-box">✅ <b>Respuesta rápida y estable</b><br>Buen balance entre velocidad y amortiguamiento.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">ℹ️ Ajusta los parámetros para mejorar la respuesta del sistema.</div>', unsafe_allow_html=True)

    if sse > 5:
        st.markdown('<div class="warn-box">⚠️ <b>Error en estado estacionario</b><br>Incrementa Ki para eliminar el error residual.</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────────
# Sección didáctica
# ──────────────────────────────────────────────────
st.divider()
st.markdown("## 📚 Guía Didáctica para Estudiantes de Ingeniería")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔵 ¿Qué es un PID?",
    "⚗️ El Reactor (CSTR)",
    "📐 Matemáticas del PID",
    "🎯 Sintonización",
    "🧪 Experimentos"
])

with tab1:
    st.markdown("""
    ### ¿Qué es un controlador PID?
    Un controlador **PID** (Proporcional–Integral–Derivativo) es el algoritmo de control
    más utilizado en la industria. Se estima que más del **90%** de los lazos de control
    industriales usan alguna variante PID.

    Su objetivo es **mover automáticamente una variable del proceso** (ej. temperatura)
    hasta el valor deseado llamado **Set-Point (SP)**, actuando sobre una variable
    manipulable (ej. potencia del calentador).
    """)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("""
        <div class="info-box">
        <b>🔵 P — Proporcional</b><br><br>
        Actúa en proporción al <b>error actual</b>.<br>
        • Respuesta inmediata<br>
        • Puede dejar error residual<br>
        • Kp alto → oscilaciones
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown("""
        <div class="good-box">
        <b>🟢 I — Integral</b><br><br>
        Acumula el error en el <b>tiempo</b>.<br>
        • Elimina error permanente<br>
        • Puede causar sobre-impulso<br>
        • Ki alto → Wind-up
        </div>
        """, unsafe_allow_html=True)
    with col_c:
        st.markdown("""
        <div class="warn-box">
        <b>🟡 D — Derivativo</b><br><br>
        Reacciona a la <b>velocidad de cambio</b>.<br>
        • Anticipa el comportamiento<br>
        • Reduce oscilaciones<br>
        • Sensible al ruido
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("""
    ### El Reactor de Tanque Agitado Continuo (CSTR)

    En este simulador modelamos un **reactor exotérmico de primer orden** donde se controla
    la **temperatura** mediante un calentador/enfriador eléctrico.

    **Variables del sistema:**
    - **Variable controlada (CV):** Temperatura del reactor T(t) [°C]
    - **Variable manipulada (MV):** Potencia del calentador u(t) [0–100%]
    - **Set-Point (SP):** Temperatura deseada de reacción
    - **Perturbaciones:** Cambios en temperatura de alimentación, concentración, etc.

    **Modelo matemático simplificado:**
    """)
    st.markdown('<div class="formula">τ · dT/dt = −T(t) + T₀ + Kₚ · u(t − θ)</div>', unsafe_allow_html=True)
    st.markdown("""
    Donde:
    - **τ** = constante de tiempo del proceso (inercia térmica)
    - **T₀** = temperatura base sin control
    - **Kₚ** = ganancia del proceso
    - **θ** = tiempo muerto (retardo de transporte o análisis)

    > 💡 **El tiempo muerto es el enemigo del control.** A mayor tiempo muerto θ,
    > más difícil es estabilizar el sistema sin oscilaciones.
    """)

with tab3:
    st.markdown("""
    ### La Ecuación del Controlador PID

    La ley de control PID en **tiempo continuo** es:
    """)
    st.markdown("""
    <div class="formula">
    u(t) = Kp · e(t)  +  Ki · ∫₀ᵗ e(τ)dτ  +  Kd · de(t)/dt
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    Donde **e(t) = SP − T(t)** es el error entre el set-point y la variable controlada.

    En **tiempo discreto** (como en este simulador con paso Δt):
    """)
    st.markdown("""
    <div class="formula">
    u[k] = Kp·e[k]  +  Ki·Δt·Σe[i]  +  Kd·(e[k] − e[k−1])/Δt
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    #### Función de Transferencia (dominio s de Laplace)

    En el dominio de Laplace, el PID ideal tiene la forma:
    """)
    st.markdown('<div class="formula">C(s) = Kp + Ki/s + Kd·s</div>', unsafe_allow_html=True)

    st.markdown("""
    #### ⚠️ Fenómeno de Wind-Up Integral
    Cuando la señal de control alcanza su límite (saturación), el término integral
    puede seguir creciendo indefinidamente. Esto se llama **Wind-Up** y puede causar
    oscilaciones severas. La solución es limitar el acumulador integral (*Anti-Wind-Up*).
    """)

with tab4:
    st.markdown("""
    ### Métodos de Sintonización de PID

    #### 1. Método de Ziegler-Nichols (lazo cerrado)
    1. Establece Ki = 0 y Kd = 0
    2. Aumenta Kp hasta que el sistema oscile de forma **sostenida** → llámalo **Kp_crítico (Ku)**
    3. Mide el **período de oscilación Pu** [min]
    4. Aplica las reglas:
    """)

    import pandas as pd
    df_zn = pd.DataFrame({
        "Tipo": ["Solo P", "PI", "PID"],
        "Kp": ["0.5·Ku", "0.45·Ku", "0.6·Ku"],
        "Ki": ["—", "1.2·Kp/Pu", "2·Kp/Pu"],
        "Kd": ["—", "—", "Kp·Pu/8"],
    })
    st.dataframe(df_zn, use_container_width=True, hide_index=True)

    st.markdown("""
    #### 2. Sintonización por tanteo (heurística)

    | Parámetro | Aumentar | Reducir |
    |-----------|----------|---------|
    | Kp ↑ | Respuesta más rápida, más oscilaciones | — |
    | Ki ↑ | Elimina error residual más rápido | Más sobre-impulso |
    | Kd ↑ | Menos oscilaciones, más amortiguamiento | Sensible a ruido |

    #### 3. Criterios de desempeño
    - **ISE** (Integral Squared Error): minimiza errores grandes
    - **IAE** (Integral Absolute Error): más equilibrado
    - **ITAE** (Integral Time·Absolute Error): penaliza errores tardíos
    """)

with tab5:
    st.markdown("""
    ### 🧪 Experimentos Sugeridos

    Realiza estos experimentos moviendo los sliders del **Panel de Control** (izquierda):

    ---
    #### Experimento 1: Solo control proporcional
    - Ki = 0, Kd = 0
    - Observa cómo **Kp** afecta la velocidad y el **error en estado estacionario**
    - ❓ ¿Puedes eliminar el error solo con P? ¿Por qué?

    ---
    #### Experimento 2: Efecto del término integral
    - Kp = 2, Kd = 0
    - Aumenta Ki de 0 hasta 2
    - ❓ ¿Cómo cambia el error residual? ¿Qué pasa con el sobre-impulso?

    ---
    #### Experimento 3: Amortiguamiento derivativo
    - Kp = 5, Ki = 0.5, Kd = 0
    - Aumenta Kd de 0 hasta 2
    - ❓ ¿Cómo afecta Kd a las oscilaciones?

    ---
    #### Experimento 4: Tiempo muerto
    - Fija Kp=3, Ki=0.5, Kd=0.5
    - Aumenta el tiempo muerto θ de 0 a 2 min
    - ❓ ¿Qué le pasa a la estabilidad del sistema?

    ---
    #### Experimento 5: Perturbación externa
    - Activa la **perturbación** en el panel
    - Ajusta los parámetros PID para que el sistema rechace la perturbación rápidamente
    - ❓ ¿Qué acción de control es más efectiva para el rechazo de perturbaciones?

    ---
    > 💡 **Consejo:** Un buen PID industrial suele tener Kp moderado, Ki suficiente para
    > eliminar el offset, y Kd entre 0.1–0.5 veces Kp para amortiguar sin amplificar ruido.
    """)

# ──────────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style="text-align:center; color:#888; font-size:0.85rem;">
Simulador Didáctico PID — Reactor Químico CSTR  |  
Desarrollado para el curso de Control e Instrumentación de Procesos Químicos (UCA/ETSIA)  |  
Modelo de primer orden con tiempo muerto + Anti-Wind-Up
</div>
""", unsafe_allow_html=True)
