import streamlit as st
from lord.main import call_current_node, process_user_input, delete_memory

st.title("LORD")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    response = f"LordGpt: {call_current_node()['text']}"
    st.session_state.messages.append({"role": "assistant", "content": response})

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    response_text = process_user_input(prompt)
    response = f"LordGpt: {call_current_node()['text']}"
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Clear conversation button
if st.button("Limpa conversa"):
    st.session_state.messages = []
    delete_memory()
    response = f"LordGpt: {call_current_node()['text']}"
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()