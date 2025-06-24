import streamlit as st
import os
import requests
import json

# Configure the page
st.set_page_config(
    page_title="HF Router Chat App",
    page_icon="🤖",
    layout="wide"
)

# API Configuration
API_URL = "https://router.huggingface.co/fireworks-ai/inference/v1/chat/completions"

def get_headers(api_key):
    """Get headers with API token"""
    if not api_key:
        return None
    
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

def query_api(messages, api_key, model="accounts/fireworks/models/deepseek-r1-0528", max_tokens=1000, temperature=0.7):
    """Query the HF Router API"""
    headers = get_headers(api_key)
    if not headers:
        return None
    
    payload = {
        "messages": messages,
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    
    try:
        with st.spinner("🤔 Thinking..."):
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

# App Header
st.title("🤖 HF Router Chat Application")
st.markdown("*Chat with AI models via Hugging Face Router API*")

# Sidebar for configuration
with st.sidebar:
    st.header("🔑 API Configuration")
    
    # API Key input
    api_key = st.text_input(
        "Hugging Face API Token",
        type="password",
        placeholder="hf_xxxxxxxxxxxxxxxxx",
        help="Enter your Hugging Face API token. Get one at https://huggingface.co/settings/tokens"
    )
    
    if not api_key:
        st.warning("⚠️ Please enter your HF API token to use the app")
        st.markdown("""
        **To get your API token:**
        1. Go to [Hugging Face Settings](https://huggingface.co/settings/tokens)
        2. Create a new token with 'Read' permissions
        3. Copy and paste it above
        """)
    else:
        st.success("✅ API token entered")
    
    st.divider()
    
    st.header("⚙️ Model Settings")
    
    # Model selection
    model = st.selectbox(
        "Model",
        ["accounts/fireworks/models/deepseek-r1-0528"],
        help="Select the AI model to use"
    )
    
    # Parameters
    max_tokens = st.slider("Max Tokens", 100, 2000, 1000, 50)
    temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
    
    st.divider()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything...", disabled=not api_key):
    if not api_key:
        st.error("Please enter your API token in the sidebar first.")
        st.stop()
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    response_data = query_api(st.session_state.messages, api_key, model, max_tokens, temperature)
    
    if response_data and "choices" in response_data:
        assistant_message = response_data["choices"][0]["message"]["content"]
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": assistant_message})
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(assistant_message)
    
    # Rerun to update the display
    st.rerun()

# Example usage section
with st.expander("📋 Example Code", expanded=False):
    st.code('''
import requests

API_URL = "https://router.huggingface.co/fireworks-ai/inference/v1/chat/completions"

def query(api_token, payload):
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

# Usage with your API token
api_token = "hf_your_token_here"
response = query(api_token, {
    "messages": [
        {
            "role": "user",
            "content": "What is the capital of France?"
        }
    ],
    "model": "accounts/fireworks/models/deepseek-r1-0528"
})

print(response["choices"][0]["message"])
    ''', language='python')

# Footer
st.divider()
st.markdown("*Built with Streamlit and Hugging Face Router API*")

# Instructions
if not api_key:
    st.info("""
    🔑 **API Token Required**
    
    This app requires your personal Hugging Face API token to function.
    
    **To get started:**
    1. **Get your API token**: Visit [Hugging Face Tokens](https://huggingface.co/settings/tokens)
    2. **Create a new token** with 'Read' permissions
    3. **Enter the token** in the sidebar
    4. **Start chatting** with the AI model!
    
    **Why do you need your own token?**
    - Ensures fair usage and rate limiting per user
    - Gives you direct access to HF Router API
    - No shared resource limitations
    """)
elif not st.session_state.messages:
    st.info("""
    👋 **Ready to Chat!** 
    
    Your API token is configured. You can now:
    - Type any question in the chat input below
    - Adjust model parameters in the sidebar
    - View your conversation history
    
    **Example questions to try:**
    - "What is the capital of France?"
    - "Explain quantum computing in simple terms"
    - "Write a short poem about technology"
    """)
