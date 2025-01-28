import streamlit as st
from openai import OpenAI

# Initialize session state for messages and processing status
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending" not in st.session_state:
    st.session_state.pending = False

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("OpenRouter API Key", type="password")
    http_referer = st.text_input("HTTP Referer (optional)")
    x_title = st.text_input("X-Title (optional)")

# Main chat interface
st.title("🤖 Image Chatbot")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        for part in message["content"]:
            if part["type"] == "text":
                st.markdown(part["text"])
            elif part["type"] == "image_url":
                st.image(part["image_url"]["url"], caption="Uploaded Image")

# Handle pending responses
if st.session_state.pending:
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        
        extra_headers = {}
        if http_referer:
            extra_headers["HTTP-Referer"] = http_referer
        if x_title:
            extra_headers["X-Title"] = x_title

        with st.spinner("Thinking..."):
            completion = client.chat.completions.create(
                extra_headers=extra_headers,
                model="google/gemini-exp-1206:free",
                messages=st.session_state.messages,
            )
            
            assistant_response = completion.choices[0].message.content
            
            # Add assistant response to chat history
            st.session_state.messages.append({
                "role": "assistant",
                "content": [{"type": "text", "text": assistant_response}]
            })
            
            st.session_state.pending = False
            st.rerun()
            
    except Exception as e:
        st.error(f"Error processing request: {str(e)}")
        st.session_state.pending = False
        st.stop()

# Chat input form
with st.form("chat_input"):
    text_input = st.text_input("Tu mensaje", key="text_input")
    image_url = st.text_input("URL de la imagen", key="image_url")
    submitted = st.form_submit_button("Enviar")

if submitted:
    if not api_key:
        st.error("🔑 Please enter your API key in the sidebar")
        st.stop()
    
    content = []
    if text_input.strip():
        content.append({"type": "text", "text": text_input})
    if image_url.strip():
        content.append({"type": "image_url", "image_url": {"url": image_url}})
    
    if not content:
        st.error("💬 Ingresa un mensaje o la URL de una imagen")
        st.stop()
    
    # Add user message to chat history
    st.session_state.messages.append({
        "role": "user",
        "content": content
    })
    
    st.session_state.pending = True
    st.rerun()