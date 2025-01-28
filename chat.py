import streamlit as st
from openai import OpenAI
import base64
from PIL import Image
import io

# Initialize OpenAI client with OpenRouter
@st.cache_resource
def get_client():
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=st.secrets["OPENROUTER_API_KEY"]
    )

# Function to encode image to base64
def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("AI Chat Assistant")

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# File uploader for images
uploaded_file = st.file_uploader("Upload an image (optional)", type=['png', 'jpg', 'jpeg'])
image_url = None

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

# Accept user input
prompt = st.chat_input("What's your question?")

if prompt:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare the messages for the API
    messages = []
    if uploaded_file is not None:
        # If there's an image, create a message with both text and image
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encode_image(image)}"
                    }
                }
            ]
        })
    else:
        # If no image, just send the text
        messages.append({
            "role": "user",
            "content": prompt
        })

    # Display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            client = get_client()
            completion = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://your-site-url.com",  # Replace with your site URL
                    "X-Title": "AI Chat Assistant",
                },
                model="google/gemini-exp-1206:free",
                messages=messages
            )
            assistant_response = completion.choices[0].message.content
            message_placeholder.markdown(assistant_response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            
        except Exception as e:
            message_placeholder.error(f"Error: {str(e)}")

# Add a clear chat button
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()