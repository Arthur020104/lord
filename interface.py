import streamlit as st
from agents.lord import generate_question,get_user_input, get_user_info
st.title("LORD")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    response = f"LordGpt: {generate_question()['text']}"
    #with st.chat_message("assistant"):
    #    st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    response_text = get_user_input(prompt)
    response = f"LordGpt: {generate_question()['text']}"
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})