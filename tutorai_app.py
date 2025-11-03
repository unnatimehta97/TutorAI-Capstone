import streamlit as st
import os
from google import genai 
from google.genai.errors import APIError 

# --- The AI's Brain: Mega-Prompt Engineering ---
# This function creates the detailed instruction set for the Gemini model,
# which acts as the Domain Model, NLU, and Tutoring Strategy.
def generate_ai_tutor_prompt(student_query, history):
    ITS_PROMPT = f"""
    You are **TutorAI**, an expert, personalized, one-on-one tutor for a third-year IT student learning basic Python. 
    Your teaching must be **adaptive, encouraging, and immediately address misconceptions**.

    **1. DOMAIN KNOWLEDGE (Syllabus):** Your expertise covers ONLY: Python Overview, Variables, Data Types, Operators, Control Structures (if/else, loops, nested), Functions, Lists/Tuples/Dictionaries/Sets, List Comprehensions, Exception Handling, Regex, Basic OOP (Classes, Objects, Encapsulation, Inheritance, Polymorphism), File Handling, and Python with MySQL.
    
    **2. TUTORING STRATEGY & FEEDBACK (The AI Logic):**
    * **Diagnosis & NLU:** First, analyze the student's query for **misconceptions** or confusion.
    * **Adaptive Response:** Provide a **step-by-step, brief explanation** tailored to their confusion. Use **analogies** and **simple, correct Python code examples** relevant to IT students.
    * **Hints:** If the question implies a problem-solving attempt, offer a gentle **hint** first, before giving the full solution.
    * **Progress Tracking:** Acknowledge the student's previous interaction (if available in history) to simulate personalized learning and continuity.
    * **Format:** Use Markdown formatting (bolding, code blocks) for professional clarity.

    **3. MANDATORY ADDITIONS (Career/Beauty):**
    * **The Beauty:** Always include a short, encouraging paragraph on the **beauty and importance of the Python concept** they asked about.
    * **Career Tip:** Always follow that with a brief tip on a **career option** directly related to that specific Python concept (e.g., if they ask about OOP, mention **Software Development/Engineering**).

    **4. CURRENT CONTEXT:**
    * **Student's Previous Interactions (History):** {history if history else 'None'}
    * **Student's Current Query:** {student_query}

    Respond **only** with the tutoring content, following all the above rules. Do not include any conversational filler like "Hello," or "I see." Start directly with the diagnosis and explanation.
    """
    return ITS_PROMPT

# --- Function to Call the AI Model ---
def get_ai_response(prompt):
    # CRITICAL: This retrieves the key set in your terminal (using 'set' or 'export') 
    # or Streamlit Cloud Secrets.
    api_key = os.environ.get("GEMINI_API_KEY") 
    
    if not api_key:
         return "ERROR: GEMINI_API_KEY not found. Please set your API key in your environment variables."
    
    try:
        # Initialize the client
        client = genai.Client(api_key=api_key)
        
        # Call the fast and capable model
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt
        )
        return response.text
        
    except APIError as e:
        return f"An AI API error occurred: {e}. Check your API key's validity."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# --- Frontend Configuration and Layout ---
st.set_page_config(page_title="TutorAI: AI-Powered Python Tutor", layout="centered")

st.title("🧠 TutorAI: Your Personalized Python Tutor")
st.markdown("---")

# Store interaction history for adaptive tutoring
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
    
st.info("👋 Hello! I'm TutorAI, an expert, adaptive tutor. Ask me anything about Python!")

# --- Main Interaction Area ---
# Text area for the student's question
student_input = st.text_area(
    "What is your question about Python (e.g., 'What is encapsulation?', or 'How does a for loop work?')", 
    height=150, 
    key="input_area"
)

# Button to submit the question
if st.button("Get Guidance", use_container_width=True):
    if student_input:
        
        # 1. Prepare History for Adaptation
        history_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in st.session_state.chat_history])
        
        # 2. Generate the Mega-Prompt
        mega_prompt = generate_ai_tutor_prompt(student_input, history_text)
        
        # 3. Get AI Response
        with st.spinner("TutorAI is thinking, analyzing your knowledge, and adapting the best explanation..."):
            ai_explanation = get_ai_response(mega_prompt) # CALL TO THE GEMINI API
        
        # 4. Update UI and History (The Interaction Module)
        st.subheader("🤖 TutorAI's Personalized Feedback:")
        st.markdown(ai_explanation)
        
        # 5. Store Interaction for simulated progress tracking
        # Store the interaction (using only the first 100 characters of the answer for brevity)
        st.session_state.chat_history.append((student_input, ai_explanation[:100] + "...")) 

        # NOTE: We removed the error-causing line st.session_state.input_area = ""

    else:
        st.warning("Please type your question above to start tutoring!")

# --- Display Chat History (Simulated Student Model) ---
st.markdown("---")
if st.session_state.chat_history:
    st.subheader("Previous Interactions (Simulated Student Progress)")
    # Show the last 5 interactions to save space
    for q, a in st.session_state.chat_history[-5:]:
        with st.expander(f"Student: {q[:50]}..."):
            # Displaying the response summary
            st.markdown(f"**Question:** {q}")
            st.markdown(f"**TutorAI Response Summary:** {a}")
            

            

        
