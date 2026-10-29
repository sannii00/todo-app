import json
import os
import uuid
from datetime import date

import streamlit as st

DATA_FILE = "/app-data/todos.json"
os.makedirs("/app-data", exist_ok=True)

st.set_page_config(page_title="TODO App", page_icon="✅")


def guardar(todos):
    """Guarda los TODOs de forma segura (archivo temporal + reemplazo)."""
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_FILE)


def cargar():
    """Carga los TODOs y migra el formato antiguo (texto) al nuevo (diccionario con id)."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except (json.JSONDecodeError, OSError):
        # Se detiene para no sobrescribir un archivo que podría recuperarse
        st.error("No se pudo leer el archivo de TODOs.")
        st.stop()

    migrado = False
    todos = []
    for t in datos:
        if not isinstance(t, dict):
            t = {"texto": str(t), "creado": str(date.today()), "vence": None}
            migrado = True
        if "id" not in t:
            t["id"] = uuid.uuid4().hex  # id estable para borrar sin depender de la posición
            migrado = True
        todos.append(t)

    # Se guarda al migrar para que los id no cambien entre ejecuciones
    if migrado:
        guardar(todos)
    return todos


def clave_orden(t):
    """Ordena por fecha límite; los TODOs sin fecha van al final."""
    return (t["vence"] is None, t["vence"] or "")


hoy = date.today()
todos = cargar()

st.title("Simple TODO App")

# Formulario para añadir un TODO
with st.form("nuevo", clear_on_submit=True):
    texto = st.text_input("Nuevo TODO")
    vence = st.date_input("Fecha límite", value=hoy, min_value=hoy)
    if st.form_submit_button("Añadir"):
        if texto.strip():
            todos.append({
                "id": uuid.uuid4().hex,
                "texto": texto.strip(),
                "creado": str(hoy),
                "vence": str(vence),
            })
            guardar(todos)
            st.rerun()
        else:
            st.warning("Escribe un texto para el TODO.")

# Resumen
vencidos = sum(1 for t in todos if t["vence"] and date.fromisoformat(t["vence"]) < hoy)
st.subheader("Tus TODOs")
st.caption(f"{len(todos)} en total · {vencidos} vencidos")

if not todos:
    st.info("No hay TODOs todavía. Añade el primero arriba.")

# Listado ordenado por fecha límite, con botón de borrado
for t in sorted(todos, key=clave_orden):
    with st.container(border=True):
        col1, col2 = st.columns([5, 1])
        if t["vence"]:
            vencido = date.fromisoformat(t["vence"]) < hoy
            limite = f":red[Vencido el {t['vence']}]" if vencido else f"Vence: {t['vence']}"
        else:
            limite = "Sin fecha límite"
        col1.markdown(f"**{t['texto']}**  \nCreado: {t['creado']} · {limite}")
        if col2.button("Eliminar", key=f"del_{t['id']}"):
            todos = [x for x in todos if x["id"] != t["id"]]
            guardar(todos)
            st.rerun()
