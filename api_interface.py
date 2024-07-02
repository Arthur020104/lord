import streamlit as st
import requests

# Define the base URL of your Flask app
FLASK_URL = "http://127.0.0.1:5000"

# Generate a unique token for the conversation
def get_token():
    response = requests.post(f"{FLASK_URL}/start_conversation")
    return response.json().get("token")

# Process user input
def process_user_input(user_input):
    token = st.session_state.get("token")
    headers = {"Authorization": token}
    response = requests.post(f"{FLASK_URL}/process_user_input", headers=headers, data=user_input.encode('utf-8'))
    return response.json()

# Call the current node
def call_current_node():
    token = st.session_state.get("token")
    headers = {"Authorization": token}
    response = requests.post(f"{FLASK_URL}/call_current_node", headers=headers)
    return response.json().get("text")

# Reset agent memory
def reset_memory():
    token = st.session_state.get("token")
    headers = {"Authorization": token}
    requests.post(f"{FLASK_URL}/reset_memory", headers=headers)

# Start a new conversation
def start_conversation():
    token = get_token()
    st.session_state["token"] = token
    call_current_node()

# Initialize Streamlit session state
if "token" not in st.session_state:
    start_conversation()

st.title("LORD")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    response = f"LordGpt: {call_current_node()}"
    st.session_state.messages.append({"role": "assistant", "content": response})

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    process_user_input(prompt)
    response = f"LordGpt: {call_current_node()}"
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Clear conversation button
if st.button("Limpa conversa"):
    st.session_state.messages = []
    reset_memory()
    response = f"LordGpt: {call_current_node()}"
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
