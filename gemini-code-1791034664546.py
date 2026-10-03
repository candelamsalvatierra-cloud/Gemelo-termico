import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Gemelo Digital - Témp. Aula", page_icon="🏫", layout="wide"
)

st.title("🏫 Gemelo Digital: Control Térmico de un Aula")
st.markdown(
    "Este prototipo simula la evolución de la temperatura en un aula considerando la presencia de alumnos y el uso del aire acondicionado."
)

# --- PANEL DE CONTROL (BARRA LATERAL) ---
st.sidebar.header("⚙️ Parámetros del Aula")

# Parámetros ambientales y físicos
temp_exterior = st.sidebar.slider(
    "Temperatura Exterior (°C)", 10.0, 40.0, 28.0, 0.5
)
num_alumnos = st.sidebar.slider("Número de Alumnos", 0, 50, 25, 1)

st.sidebar.header("❄️ Configuración del Aire Acondicionado")
estado_ac = st.sidebar.checkbox("Encender Aire Acondicionado", value=True)
temp_setpoint = st.sidebar.slider(
    "Temperatura Objetivo AC (°C)", 18.0, 26.0, 22.0, 0.5
)

st.sidebar.header("⏱️ Simulación")
tiempo_total_min = st.sidebar.slider(
    "Duración de la simulación (minutos)", 30, 240, 120, 10
)

# --- MODELO FÍSICO (SIMULACIÓN DINÁMICA) ---
# Constantes del modelo
capacidad_termica = (
    50000.0  # Inercia térmica del aula (kJ/°C aprox o equivalente en escala)
)
resistencia_paredes = (
    0.02  # Coeficiente de transferencia con el exterior
)
calor_por_alumno = (
    100.0  # Watts generados por persona (W)
)


def simular_temperatura(
    t_ext, n_alu, ac_on, t_target, minutos, t_inicial=24.0
):
    dt = 1.0  # paso de 1 minuto en segundos (60s)
    tiempos = np.arange(0, minutos + 1, 1)
    temperaturas = [t_inicial]

    t_actual = t_inicial

    for _ in range(minutos):
        # 1. Calor ganado por los alumnos (W convertidos a efecto térmico)
        q_alumnos = n_alu * calor_por_alumno

        # 2. Transferencia de calor con el exterior por las paredes
        q_paredes = resistencia_paredes * (t_ext - t_actual) * 500

        # 3. Efecto del aire acondicionado
        q_ac = 0.0
        if ac_on:
            # Si el aire está encendido, ejerce una potencia proporcional a la diferencia con el setpoint
            # Si hace más calor que el setpoint, enfría; si hace menos, calefacciona suavemente.
            diferencia = t_actual - t_target
            q_ac = (
                -4000.0 * np.sign(diferencia) * min(abs(diferencia) / 2.0, 1.5)
            )
            # Simplificación de control proporcional simple
            t_actual += (
                -0.05 * (t_actual - t_target) if abs(t_actual - t_target) > 0.1 else 0
            )

        # Variación neta de temperatura (Ley de enfriamiento/calentamiento simplificada)
        # dT = (Calor neto / Capacidad térmica) * factor de escala temporal
        delta_t = (
            (q_alumnos + q_paredes + q_ac) / capacidad_termica
        ) * 15  # Factor de escala para visualización dinámica
        t_actual += delta_t

        # Acotar temperaturas realistas
        t_actual = max(10.0, min(45.0, t_actual))
        temperaturas.append(t_actual)

    df = pd.DataFrame(
        {"Minuto": tiempos, "Temperatura Aula (°C)": temperaturas}
    )
    return df


# Ejecutar simulación
df_simulacion = simular_temperatura(
    temp_exterior, num_alumnos, estado_ac, temp_setpoint, tiempo_total_min
)

# --- VISUALIZACIÓN EN PANTALLA PRINCIPAL ---
col1, col2, col3 = st.columns(3)

temp_final = df_simulacion["Temperatura Aula (°C)"].iloc[-1]
col1.metric(
    label="Temperatura Inicial",
    value=f"{df_simulacion['Temperatura Aula (°C)'].iloc[0]:.1f} °C",
)
col2.metric(
    label="Temperatura Final (Simulada)",
    value=f"{temp_final:.1f} °C",
    delta=f"{temp_final - df_simulacion['Temperatura Aula (°C)'].iloc[0]:.1f} °C",
)
col3.metric(
    label="Estado del Sistema",
    value="❄️ Enfriando/Climatizando" if estado_ac else "⚠️ Sin Climatización",
)

st.subheader("📈 Evolución de la Temperatura en el Tiempo")
st.line_chart(df_simulacion.set_index("Minuto"))

st.info(
    "💡 **Cómo usar este prototipo:** Modifica el número de alumnos o enciende/apaga el aire acondicionado en la barra lateral para ver en tiempo real cómo responde la curva térmica del aula."
)