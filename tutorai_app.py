import streamlit as st
import os
from google import genai 
from google.genai.errors import APIError 
import time

# --- Mock Authentication (Simplified) ---
# We keep this logic to ensure a session ID exists for adaptive conversation
if 'is_authenticated' not in st.session_state:
    st.session_state.is_authenticated = True 
    st.session_state.user_id = f"anon_user_{int(time.time())}"

def sign_in_anonymously():
    st.session_state.is_authenticated = True
    st.session_state.user_id = f"anon_user_{int(time.time())}"
    return st.session_state.user_id

# --- The AI's Brain: Mega-Prompt Engineering ---
def generate_ai_tutor_prompt(student_query, history):
    ITS_PROMPT = f"""
    You are **TutorAI**, an expert, personalized, one-on-one tutor for a third-year IT student learning basic Python. 
    Your teaching must be **adaptive, encouraging, and immediately address misconceptions**.

    **1. DOMAIN KNOWLEDGE (Syllabus):** Your expertise covers ONLY: Python Overview, Variables, Data Types, Operators, Control Structures (if/else, loops, nested), Functions, Lists/Tuples/Dictionaries/Sets, List Comprehensions, Exception Handling, Regex, Basic OOP (Classes, Objects, Encapsulation, Inheritance, Polymorphism), File Handling, and Python with MySQL.
    
    **2. TUTORING STRATEGY & FEEDBACK (The AI Logic):**
    * **Diagnosis & NLU:** First, analyze the student's query for **misconceptions** or confusion.
    * **Adaptive Response:** Provide a **step-by-step, brief explanation** tailored to their confusion. Use **analogies** and **simple, correct Python code examples** relevant to IT students.
    * **Progress Tracking:** Acknowledge the student's previous interaction (if available in history) to simulate personalized learning and continuity.
    * **Format:** Use clear Markdown formatting (bolding, code blocks, lists) for professional clarity.

    **3. MANDATORY ADDITIONS (Career/Beauty):**
    * **The Beauty:** Always conclude your response with a short, encouraging paragraph on the **beauty and importance of the Python concept** they asked about.
    * **Career Tip:** Always follow that with a brief tip on a **career option** directly related to that specific Python concept (e.g., if they ask about OOP, mention **Software Development/Engineering**).

    **4. CURRENT CONTEXT:**
    * **Student's Previous Interactions (History):** {history if history else 'None'}
    * **Student's Current Query:** {student_query}

    Respond **only** with the tutoring content, following all the above rules.
    """
    return ITS_PROMPT

def get_ai_response(prompt):
    api_key = os.environ.get("GEMINI_API_KEY") 
    if not api_key:
         return "ERROR: GEMINI_API_KEY not found. Please set your API key in your environment variables."
    
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt
        )
        return response.text
        
    except APIError as e:
        return f"An AI API error occurred: {e}. Check your API key's validity."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# --- APP STARTUP & INITIALIZATION ---
st.set_page_config(page_title="TutorAI: Personalized Python Tutor", layout="wide")

# Initialize chat history (only for the current session)
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [("TutorAI", "👋 Hello! I'm TutorAI, an expert, adaptive tutor here to help you master Python programming. Ask me anything!")]


# --- Custom CSS for clean look and hiding placeholder text ---
st.markdown("""
<style>
    /* Global Font and Background */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    .stApp { background: #0D1117; color: #C9D1D9; font-family: 'Inter', sans-serif; }
    
    /* FIX: Hide the distracting "keyboard_double_arrow_right" text */
    .stApp [data-testid="stSidebar"] + div button > div { visibility: hidden; width: 0px !important; }
    .stApp [data-testid="stSidebar"] + div button::before {
        content: "\u2261"; /* Unicode for hamburger icon */
        visibility: visible !important;
        font-size: 28px; color: #00C49A; position: relative; left: -15px;
    }
    
    /* Sidebar Styling (Still needed for settings, even if empty) */
    .stApp [data-testid="stSidebar"] { background-color: #161B22; color: #C9D1D9; }
    .main-title { display: flex; align-items: center; gap: 15px; color: #C9D1D9; }
    .main-title h1 { font-weight: 800; letter-spacing: -1px; }

    /* Chat Input Styling - Fixed at the bottom */
    div.stChatInput {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #161B22; 
        padding: 10px 15px;
        border-top: 1px solid #30363D;
        z-index: 999;
    }
    
    /* Push content above the fixed chat input */
    .block-container { 
        padding-bottom: 100px; /* Space for the chat input */
    }
    
    /* Input Text Area inside the chat input */
    div.stChatInput textarea {
        background-color: #0D1117 !important; 
        border: 1px solid #30363D !important;
        color: #C9D1D9 !important;
        border-radius: 12px;
    }

    /* Message colors */
    div[data-testid="stChatMessage"]:nth-child(even) { background-color: #161B22; } /* TutorAI */
    div[data-testid="stChatMessage"]:nth-child(odd) { background-color: #0D1117; } /* User */
    
    /* *** FINAL FIX: Completely hide the Session Active button and its container *** */
    .st-emotion-cache-1kyxreq { visibility: hidden; width: 0px !important; }
    .st-emotion-cache-1kyxreq + div { visibility: hidden; width: 0px !important; }
    .st-emotion-cache-1kyxreq + div + div { visibility: hidden; width: 0px !important; }

</style>
""", unsafe_allow_html=True)

# --- HEADER (Title) ---
# We use a single column now for a clean, centered look
col1, = st.columns([1])

with col1:
    st.markdown(
        """
        <div class="main-title">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#00C49A" width="40px" height="40px">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zM7 9h2V7H7v2zm8 0h2V7h-2v2zm-4 4h2v-2h-2v2zm-4 0h2v-2H7v2zm8 0h2v-2h-2v2zm-4 4h2v-2h-2v2z"/>
            </svg>
            <h1>TutorAI: Personalized Python Tutor</h1>
        </div>
        """, unsafe_allow_html=True
    )
    
st.markdown("---")

# --- MAIN CHAT DISPLAY AREA ---
# Display the chat thread history
for role, content in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(content)
            
# --- CHAT INPUT (Fixed at bottom) ---
if prompt := st.chat_input("What is your question about Python?"):
    
    # 1. Add user message to history
    st.session_state.chat_history.append(("user", prompt))
    
    # Show user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Prepare History for Adaptation 
    history_for_prompt = st.session_state.chat_history[-10:]
    history_text = "\n".join([f"{role}: {content}" for role, content in history_for_prompt])
    
    # 3. Generate the Mega-Prompt and Get AI Response
    mega_prompt = generate_ai_tutor_prompt(prompt, history_text)
    
    with st.chat_message("TutorAI"):
        with st.spinner("TutorAI is thinking, analyzing your knowledge, and adapting the best explanation..."):
            ai_explanation = get_ai_response(mega_prompt)
        st.markdown(ai_explanation)

    # 4. Add AI response to history
    st.session_state.chat_history.append(("TutorAI", ai_explanation))
    
    st.rerun()