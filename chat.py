import os
import json
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# -------- CONFIG --------
# Set this in your terminal before running:
# export GROQ_API_KEY="your_actual_key_here"
api_key = os.environ.get("GROQ_API_KEY")
MEMORY_FILE = "chat_memory.json"
MODEL_NAME = "llama-3.3-70b-versatile"

# -------- MEMORY HANDLING --------
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []


def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

# -------- INIT CLIENT --------
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    st.error("❌ GROQ_API_KEY not found. Set it in your terminal before running the app.")
    st.stop()

client = Groq(api_key=api_key)

# -------- STREAMLIT UI --------
st.set_page_config(page_title="Groq ChatGPT", layout="centered")
st.title("💬 Groq ChatGPT Web App")

# Load chat history into session state
if "messages" not in st.session_state:
    st.session_state.messages = load_memory()

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    else:
        with st.chat_message("assistant"):
            st.write(msg["content"])

# Chat input box
user_input = st.chat_input("Type your message here...")

if user_input:
    # Show user message in UI
    with st.chat_message("user"):
        st.write(user_input)

    # Append to memory
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Prepare messages for model (include a system prompt)
    messages_for_model = [
        {"role": "system", "content": "You are a helpful AI assistant. Remember useful user preferences."}
    ] + st.session_state.messages

    # Get response from Groq
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                messages=messages_for_model,
                model=MODEL_NAME,
            )
            ai_reply = response.choices[0].message.content
            st.write(ai_reply)

    # Save assistant reply
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
    save_memory(st.session_state.messages)

# Clear chat button
if st.button("🧹 Clear Chat History"):
    st.session_state.messages = []
    save_memory([])
    st.rerun()
