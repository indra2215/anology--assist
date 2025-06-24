import streamlit as st
import requests

# --- Ask user for their Hugging Face API key ---
st.title("🧠 Analogy Assist")
st.subheader("Learn Complex Concepts Through Simple Analogies")

user_token = st.text_input(
    "🔑 Enter your Hugging Face API token to use this app:",
    type="password",
    help="Get your token from https://huggingface.co/settings/tokens"
)

if not user_token:
    st.warning("Please enter your Hugging Face API token above to continue.")
    st.stop()

hf_token = user_token

# --- Page configuration (fixed comma bug) ---
st.set_page_config(
    page_title="Analogy Assist",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- API Configuration ---
API_URL = "https://api-inference.huggingface.co/models/google/gemma-7b-it"

def get_headers():
    return {
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": "application/json"
    }

def query_api(prompt):
    headers = get_headers()
    payload = {"inputs": prompt}
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {str(e)}")
        return None

def create_analogy_prompt(concept, learning_mode, difficulty_level, context=""):
    base_context = f"Context: {context}\n" if context else ""
    if learning_mode == "Simple Analogy Explanation":
        prompt = f"""Explain the concept of '{concept}' using a simple, relatable analogy. 
{base_context}
Make it {difficulty_level} level and easy to understand. Use everyday objects or situations that most people are familiar with.

Format your response as:
**Concept:** {concept}
**Analogy:** [Your analogy here]
**Explanation:** [How the analogy relates to the concept]
"""
    elif learning_mode == "Multiple Analogies Comparison":
        prompt = f"""Provide 3 different analogies to explain '{concept}' from different perspectives. 
{base_context}
Make it {difficulty_level} level. Show how each analogy highlights different aspects of the concept.

Format your response as:
**Concept:** {concept}
**Analogy 1:** [First analogy and explanation]
**Analogy 2:** [Second analogy and explanation]  
**Analogy 3:** [Third analogy and explanation]
**Summary:** [How all analogies work together to explain the concept]
"""
    elif learning_mode == "Interactive Analogy Building":
        prompt = f"""Help me build an analogy for '{concept}' step by step. 
{base_context}
Make it {difficulty_level} level. Start by asking what familiar thing or situation I'd like to compare it to, then guide me through building the analogy.

Start with: "Let's build an analogy for {concept} together! What's something from your daily life that you're very familiar with that we could potentially compare to {concept}?"
"""
    elif learning_mode == "Problem-Solving with Analogies":
        prompt = f"""I need to solve a problem or understand a challenge related to '{concept}'. 
{base_context}
Make it {difficulty_level} level. Use analogies to help me understand the problem and potential solutions.

Format your response as:
**Problem/Challenge:** [Identify the key challenge with {concept}]
**Analogy:** [Use an analogy to explain the problem]
**Solution Approach:** [Use the same analogy to suggest solutions]
**Application:** [How to apply this understanding practically]
"""
    else:  # Story-Based Learning
        prompt = f"""Create an engaging story that naturally incorporates and explains '{concept}' through analogies. 
{base_context}
Make it {difficulty_level} level. The story should make the concept memorable and easy to understand.

Format your response as:
**Story Title:** [Creative title]
**Story:** [Your engaging story that explains {concept}]
**Key Takeaways:** [Main points about {concept} from the story]
"""
    return prompt

# --- Sidebar for configuration ---
st.sidebar.header("⚙️ Configuration")

learning_modes = [
    "Simple Analogy Explanation",
    "Multiple Analogies Comparison", 
    "Interactive Analogy Building",
    "Problem-Solving with Analogies",
    "Story-Based Learning"
]

selected_mode = st.sidebar.selectbox(
    "🎯 Choose Learning Mode:",
    learning_modes,
    help="Select how you'd like to receive analogy-based understanding"
)

difficulty_level = st.sidebar.select_slider(
    "📊 Difficulty Level:",
    options=["Beginner", "Intermediate", "Advanced"],
    value="Intermediate"
)

mode_descriptions = {
    "Simple Analogy Explanation": "Get a single, clear analogy to understand any concept",
    "Multiple Analogies Comparison": "Compare multiple analogies to see different aspects of a concept",
    "Interactive Analogy Building": "Work together to build custom analogies step by step",
    "Problem-Solving with Analogies": "Use analogies to understand and solve problems",
    "Story-Based Learning": "Learn through engaging stories that incorporate analogies"
}

st.sidebar.info(f"**{selected_mode}:** {mode_descriptions[selected_mode]}")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 💡 What would you like to understand?")
    if 'selected_concept' in st.session_state:
        default_concept = st.session_state.selected_concept
        del st.session_state.selected_concept
    else:
        default_concept = ""
    concept = st.text_input(
        "Enter a concept, topic, or idea:",
        value=default_concept,
        placeholder="e.g., Machine Learning, Photosynthesis, Stock Market, Quantum Physics...",
        help="Type any concept you'd like to understand through analogies"
    )
    context = st.text_area(
        "Additional Context (Optional):",
        placeholder="Provide any specific context, background, or particular aspect you want to focus on...",
        height=100,
        help="This helps create more targeted and relevant analogies"
    )

with col2:
    st.markdown("### 📚 Quick Examples")
    example_concepts = [
        "Artificial Intelligence",
        "Blockchain Technology", 
        "Climate Change",
        "Stock Market Volatility",
        "Neural Networks",
        "Photosynthesis",
        "Supply Chain Management",
        "Quantum Computing"
    ]
    st.markdown("**Try these concepts:**")
    for example in example_concepts[:4]:
        if st.button(example, key=f"example_{example}"):
            st.session_state.selected_concept = example

if st.button("🚀 Generate Analogy", type="primary", use_container_width=True):
    if not concept:
        st.warning("Please enter a concept to explain!")
    else:
        with st.spinner("Creating your analogy..."):
            prompt = create_analogy_prompt(concept, selected_mode, difficulty_level, context)
            response = query_api(prompt)
            if response and isinstance(response, list) and "generated_text" in response[0]:
                st.markdown("---")
                st.markdown("### 🎯 Your Analogy-Based Explanation")
                explanation = response[0]["generated_text"].strip()
                st.markdown(explanation)
                st.markdown("---")
                st.markdown("### 💬 Was this helpful?")
                colf1, colf2, colf3 = st.columns(3)
                with colf1:
                    if st.button("👍 Very Helpful"):
                        st.success("Thank you for your feedback!")
                with colf2:
                    if st.button("👌 Somewhat Helpful"):
                        st.info("Thanks! We'll keep improving.")
                with colf3:
                    if st.button("👎 Not Helpful"):
                        st.warning("Sorry about that. Try a different learning mode or add more context.")
                if st.button("🔄 Try Different Learning Mode"):
                    st.rerun()
            else:
                st.error("Failed to generate analogy. Please check your API configuration and try again.")

st.markdown("---")
st.markdown("### 💡 Tips for Better Analogies")

tips_col1, tips_col2 = st.columns(2)

with tips_col1:
    st.markdown("""
    **For Better Results:**
    - Be specific about what aspect you want to understand
    - Provide context about your background knowledge
    - Try different learning modes for the same concept
    - Use the difficulty level that matches your needs
    """)

with tips_col2:
    st.markdown("""
    **Learning Modes Guide:**
    - **Simple:** Quick, single analogy explanation
    - **Multiple:** Compare different perspectives
    - **Interactive:** Build analogies together
    - **Problem-Solving:** Focus on practical applications
    - **Story-Based:** Learn through memorable narratives
    """)