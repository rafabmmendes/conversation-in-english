import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import json

# --- CONFIGURAÇÕES INICIAIS ---
genai.configure(api_key="SUA_CHAVE_API_AQUI")
engine = pyttsx3.init()

def speak(text):
    """Faz a IA falar o texto."""
    engine.say(text)
    engine.runAndWait()

def listen():
    """Captura o áudio do microfone e transforma em texto."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Ouvindo... Pode falar!")
        audio = r.listen(source)
        try:
            return r.recognize_google(audio, language="en-US")
        except:
            return None

# --- INTERFACE E ESTADO ---
st.set_page_config(page_title="LingoAI Master", page_icon="🎤")
st.title("🎤 LingoAI: Learn by Speaking")

if "xp" not in st.session_state:
    st.session_state.xp = 0
    st.session_state.history = []
    st.session_state.level = "Beginner"

# --- SIDEBAR (GAMIFICAÇÃO E CONFIGS) ---
with st.sidebar:
    st.header(f"⭐ XP: {st.session_state.xp}")
    st.progress(min(st.session_state.xp / 1000, 1.0))
    
    st.session_state.level = st.selectbox("Seu Nível:", ["Beginner", "Intermediate", "Advanced"])
    tema = st.text_input("Tema da Aula:", "Job Interview")
    
    if st.button("Resetar Progresso"):
        st.session_state.xp = 0
        st.rerun()

# --- LÓGICA DA IA ---
model = genai.GenerativeModel('gemini-1.5-flash')

system_prompt = f"""
You are an expert English Tutor. 
Student Level: {st.session_state.level}. Topic: {tema}.
Rules:
1. Converse naturally but always provide a 'Feedback' section in JSON format at the end of your response.
2. The JSON should include: "corrections" (string), "vocabulary_tip" (string), and "xp_earned" (int: 10-50).
3. If the student is a Beginner, use simpler words.
"""

# --- UI DE CHAT ---
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Botões de interação
col1, col2 = st.columns(2)
user_input = None

with col1:
    if st.button("🎤 Falar (Microfone)"):
        user_input = listen()
        if not user_input:
            st.warning("Não consegui te ouvir. Tente novamente.")

with col2:
    text_input = st.chat_input("Ou digite aqui...")
    if text_input:
        user_input = text_input

# Processamento da Resposta
if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Chamada da IA
    full_prompt = f"{system_prompt}\nStudent: {user_input}\nTeacher:"
    response = model.generate_content(full_prompt)
    
    # Separando texto de feedback (assumindo que a IA segue o formato)
    full_text = response.text
    
    # Adicionando XP e exibindo
    st.session_state.xp += 20 # Simplificado para o exemplo
    
    with st.chat_message("assistant"):
        st.markdown(full_text)
        if st.button("🔈 Ouvir Pronúncia"):
            speak(full_text.split("JSON")[0]) # Fala apenas o texto, não o JSON

    st.session_state.history.append({"role": "assistant", "content": full_text})
