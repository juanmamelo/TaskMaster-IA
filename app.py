import streamlit as st
import requests
import json
import re
from datetime import datetime

st.set_page_config(page_title="TaskMaster IA", page_icon="🧠")

# --- Función para consultar a Gemini ---
def consultar_gemini(prompt_usuario):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": st.secrets["GEMINI_API_KEY"]}
    data = {
        "contents": [{
            "parts": [{"text": prompt_usuario}]
        }]
    }
    response = requests.post(url, headers=headers, params=params, json=data)

    if response.status_code == 200:
        respuesta = response.json()
        return respuesta["candidates"][0]["content"]["parts"][0]["text"]
    else:
        return f"❌ Error {response.status_code}: {response.text}"

# --- Inicializar sesión ---
if "tareas" not in st.session_state:
    st.session_state.tareas = []

# --- Agregar nueva tarea ---
st.title("🧠 TaskMaster IA")
st.write("Organizá tu día con inteligencia artificial. Podés ingresar tareas con o sin horario, y la IA completará lo que falta.")

if st.button("➕ Agregar nueva tarea"):
    st.session_state.tareas.append({"descripcion": "", "inicio": "", "fin": ""})

# --- Mostrar tareas cargadas dinámicamente ---
st.subheader("📋 Lista de tareas")

for i, tarea in enumerate(st.session_state.tareas):
    col1, col2, col3 = st.columns([3, 1.5, 1.5])
    tarea["descripcion"] = col1.text_input(f"Tarea #{i+1}", tarea["descripcion"], key=f"desc_{i}")
    tarea["inicio"] = col2.text_input(f"Inicio", tarea["inicio"], key=f"ini_{i}", placeholder="hh:mm")
    tarea["fin"] = col3.text_input(f"Fin", tarea["fin"], key=f"fin_{i}", placeholder="hh:mm")

# --- Botón de análisis ---
if st.button("🧠 Organizar cronograma"):
    tareas_con_horario = []
    tareas_sin_horario = []

    for t in st.session_state.tareas:
        if t["descripcion"].strip() == "":
            continue
        if t["inicio"].strip() and t["fin"].strip():
            tareas_con_horario.append(t)
        else:
            tareas_sin_horario.append(t)

    prompt_horarios = "Tengo las siguientes tareas con horario definido:\n"
    for t in tareas_con_horario:
        prompt_horarios += f"- {t['descripcion']} de {t['inicio']} a {t['fin']}\n"

    if tareas_sin_horario:
        prompt_horarios += "\nY estas tareas sin horario:\n"
        for t in tareas_sin_horario:
            prompt_horarios += f"- {t['descripcion']}\n"
        prompt_horarios += "\nPor favor, asignales un horario a las tareas sin superponerlas con las ya definidas. Mantené bloques razonables y ordenados."

        resultado_cronograma = consultar_gemini(prompt_horarios)
    else:
        resultado_cronograma = "Todas las tareas tienen horario asignado."

    # --- Mostrar cronograma final ---
    st.subheader("🗓️ Cronograma sugerido")
    st.markdown(resultado_cronograma)

    # --- También pedir análisis y prioridad ---
    todas_las_tareas = "\n".join([f"- {t['descripcion']}" for t in st.session_state.tareas])
    prompt_prioridad = f"""
Actuá como un asistente de productividad. Analizá estas tareas y asignales una prioridad (Alta, Media, Baja) con una breve justificación.
Tareas:
{todas_las_tareas}
"""
    resultado_prioridad = consultar_gemini(prompt_prioridad)

st.subheader("📌 Análisis y prioridades con colores")

# Buscar líneas con patrón tipo: "- Tarea: Prioridad (explicación)"
lineas = resultado_prioridad.splitlines()

for linea in lineas:
    if "Alta" in linea:
        color = "#FFCCCC"  # rojo claro
    elif "Media" in linea:
        color = "#FFF2CC"  # amarillo claro
    elif "Baja" in linea:
        color = "#CCFFCC"  # verde claro
    else:
        color = "#F0F0F0"  # gris claro por defecto

    st.markdown(f"<div style='background-color: {color}; padding: 10px; border-radius: 8px; margin-bottom: 5px;'>{linea}</div>", unsafe_allow_html=True)

