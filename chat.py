import streamlit as st
from openai import OpenAI
import json

# Initialize OpenAI client with OpenRouter configuration
@st.cache_resource
def get_client():
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=st.secrets["OPENROUTER_API_KEY"]
    )

# Function to get chatbot response
def get_response(client, messages):
    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "http://irvingernesto.com",  # Replace with your actual site URL
                "X-Title": "SonGPT",  # Replace with your actual site name
            },
            model="google/gemini-exp-1206:free",
            messages=messages
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

st.title("🤖 Chatbot")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize OpenAI client
client = get_client()

# Chat input
user_input = st.chat_input("Type your message here...")

# When user sends a message
if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get bot response
    response = get_response(client, st.session_state.messages)
    
    # Add bot response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
