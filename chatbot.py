import streamlit as st
import groq  # API client (asegurate de tener la librería instalada)

# Configuración de la página (mejor al inicio)
st.set_page_config(page_title="Pagina para el chatbot", page_icon="🫡")

MODELOS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "meta-llama/llama-guard-4-12b",
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b"
]


def crear_cliente_groq():
    try:
        groq_api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        return None
    return groq.Groq(api_key=groq_api_key)


def inicializacion_estado_chat():
    if "mensajes" not in st.session_state:
        st.session_state["mensajes"] = []   # lista de dicts: {"role":"user"/"assistant", "content": "..."}
    if "usuario" not in st.session_state:
        st.session_state["usuario"] = None
    if "bot_respuestas" not in st.session_state:
        st.session_state["bot_respuestas"] = []


def mostrar_sidebar():
    st.sidebar.title("Elegi tu IA")
    modelo = st.sidebar.selectbox("Cual elegis?", MODELOS, index=0)
    st.sidebar.write(f"Elegiste el modelo: {modelo}")

    # Botón para limpiar el chat (opcional)
    if st.sidebar.button("Limpiar chat"):
        st.session_state["mensajes"] = []
    return modelo


def mostrar_historial():
    # Muestra todos los mensajes almacenados en el estado
    for mensaje in st.session_state["mensajes"]:
        role = mensaje.get("role", "user")
        content = mensaje.get("content", "")
        # roles válidos: "user", "assistant", "system"
        with st.chat_message(role):
            st.markdown(content)


def obtener_mensaje():
    # Único chat_input en la app (con key)
    return st.chat_input("Envia un mensaje", key="chat_input")


def agregar_mensaje_historial(role, content):
    st.session_state["mensajes"].append({"role": role, "content": content})


def mostrar_mensaje(role, content):
    with st.chat_message(role):
        st.markdown(content)


def obtener_respuesta_modelo(cliente, modelo, mensajes):
    if cliente is None:
        return "Error: no está configurada la GROQ_API_KEY en st.secrets."
    try:
        respuesta = cliente.chat.completions.create(
            model=modelo,
            messages=mensajes,
            stream=False
        )
        # Ajustá esto según la respuesta real que te devuelva la librería groq
        return respuesta.choices[0].message.content
    except Exception as e:
        st.error(f"Error al llamar al modelo: {e}")
        return "Lo siento, hubo un error al contactar al modelo."


def ejecutar_app():
    # Inicializaciones
    inicializacion_estado_chat()
    modelo = mostrar_sidebar()
    cliente = crear_cliente_groq()

    st.title("Pagina para el chatbot")

    # Mostrar historial previo
    mostrar_historial()

    # Obtener input del usuario (solo 1 vez)
    mensaje_usuario = obtener_mensaje()

    # Si el usuario escribió algo
    if mensaje_usuario:
        # Agregar y mostrar mensaje del usuario
        agregar_mensaje_historial("user", mensaje_usuario)
        mostrar_mensaje("user", mensaje_usuario)

        # Llamar al modelo y mostrar la respuesta
        respuesta = obtener_respuesta_modelo(cliente, modelo, st.session_state["mensajes"])
        agregar_mensaje_historial("assistant", respuesta)
        mostrar_mensaje("assistant", respuesta)


if _name_ == "_main_":
    ejecutar_app()
