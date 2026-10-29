import streamlit as st
import json
import os
from datetime import date

DATA_FILE = "/app-data/todos.json"
os.makedirs("/app-data", exist_ok=True)

def cargar():
    """Carga los TODOs y convierte el formato antiguo (texto) al nuevo (diccionario)."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        datos = json.load(f)
    return [
        t if isinstance(t, dict)
        else {"texto": t, "creado": str(date.today()), "vence": None}
        for t in datos
    ]

def guardar(todos):
    with open(DATA_FILE, "w") as f:
        json.dump(todos, f)

todos = cargar()

st.title("Simple TODO App")

# Formulario para añadir un TODO
with st.form("nuevo", clear_on_submit=True):
    texto = st.text_input("Nuevo TODO")
    vence = st.date_input("Fecha límite", value=date.today())
    if st.form_submit_button("Añadir") and texto:
        todos.append({"texto": texto, "creado": str(date.today()), "vence": str(vence)})
        guardar(todos)
        st.rerun()

# Listado con botón de borrado
st.subheader("Tus TODOs")
for i, t in enumerate(todos):
    col1, col2 = st.columns([5, 1])
    col1.write(f"**{t['texto']}**  \nCreado: {t['creado']} · Vence: {t['vence']}")
    if col2.button("Eliminar", key=f"del_{i}"):
        todos.pop(i)
        guardar(todos)
        st.rerun()
