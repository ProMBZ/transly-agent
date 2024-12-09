import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv  # For loading .env file

# 🔥 Load API Keys from .env file
load_dotenv()

# 🔑 API Keys
gemini_api_key = os.getenv("GEMINI_API_KEY")  # Load from .env file

# 🚨 Check if the keys are loaded properly
if not gemini_api_key:
    st.error("API key not found! Please add GEMINI_API_KEY to your .env file.")
    st.stop()

# Configure the genai library for Gemini
genai.configure(api_key=gemini_api_key)

# 🔥 Short-Term Memory to store user session data
if "conversation_memory" not in st.session_state:
    st.session_state.conversation_memory = []

if "user_preferences" not in st.session_state:
    st.session_state.user_preferences = {}

def update_memory(user_id, key, value):
    """
    Updates the user's memory with a specific key-value pair.
    """
    if user_id not in st.session_state.user_preferences:
        st.session_state.user_preferences[user_id] = {}
    st.session_state.user_preferences[user_id][key] = value

def get_user_memory(user_id, key):
    """
    Retrieves the memory for a specific user and key.
    """
    return st.session_state.user_preferences.get(user_id, {}).get(key, None)

# 🔥 Gemini Chat Session Setup
generation_config = {
    "temperature": 1.0,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 512,
}

# **Start the Gemini Chat Session**
chat_session = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=(
        "You are a helpful language translation assistant named Transly. "
        "Your main goal is to translate words and sentences from one language to another. "
        "If the user does not specify the target language, you should politely ask for it. "
        "If the user has previously requested translations from specific languages, remember their preferences. "
        "Respond in a friendly, conversational, and simple tone."
    )
).start_chat()

# 🔥 Chatbot Response Logic
def chatbot_response(user_input, user_id="user_1"):
    """
    Handles user input, interacts with Gemini, and returns a response.
    """
    try:
        if "translate" in user_input.lower():
            # Extract the phrase and the language from the input
            if "to" in user_input:
                parts = user_input.split(" to ")
                if len(parts) == 2:
                    text_to_translate = parts[0].replace("translate", "").strip()
                    target_language = parts[1].strip()
                    update_memory(user_id, 'preferred_language', target_language)
                else:
                    text_to_translate = user_input.replace("translate", "").strip()
                    target_language = get_user_memory(user_id, 'preferred_language') or 'Spanish'
            else:
                text_to_translate = user_input.replace("translate", "").strip()
                target_language = get_user_memory(user_id, 'preferred_language') or 'Spanish'

            # Ask Gemini to translate
            response = chat_session.send_message(
                f"Translate '{text_to_translate}' into {target_language}."
            )
            
            st.session_state.conversation_memory.append(
                {"role": "user", "parts": [user_input]}
            )
            st.session_state.conversation_memory.append(
                {"role": "assistant", "parts": [response.text]}
            )
            
            return f"Translated to **{target_language}**: {response.text}"

        if "exit" in user_input.lower() or "quit" in user_input.lower() or "q" in user_input.lower():
            return "Exiting Transly. Goodbye! 👋"

        # Call Gemini for general responses
        response = chat_session.send_message(user_input)
        st.session_state.conversation_memory.append(
            {"role": "user", "parts": [user_input]}
        )
        st.session_state.conversation_memory.append(
            {"role": "assistant", "parts": [response.text]}
        )
        return response.text

    except Exception as e:
        return "An error occurred while generating a response. Please try again later."

# 🔥 Main Streamlit UI
st.title("🌐 Transly: Your Language Translator Bot")
st.write("Welcome! I can help you translate words and phrases into different languages. 🗣️")

# Greet the user
if "greeted" not in st.session_state:
    st.session_state.greeted = True
    st.write("👋 Hello! You can type commands like **'Translate Hello to Spanish'** or **'What is Good Morning in French?'**")

# Chat input
user_input = st.text_input("Type your message here and press Enter:")

if user_input:
    response = chatbot_response(user_input)
    st.write(f"🤖 Transly: {response}")
