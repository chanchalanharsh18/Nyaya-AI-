import streamlit as st
import time
from vector_database import index_pdf, upload_pdf
from rag_pipeline import answer_query, retrieve_docs, llm_model, generate_report

# --- Page Configuration ---
st.set_page_config(page_title="NyayaAI", page_icon="⚖️", layout="centered")

# --- Custom Styling ---
st.markdown("""
    <style>
        .sidebar-header {
            font-size: 24px;
            font-weight: 800;
            margin-bottom: 20px;
            text-align: center;
        }
        /* Highlight the chat input bar */
        div[data-testid="stChatInput"] {
            border: 1px solid #94A3B8 !important;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.08) !important;
            border-radius: 12px !important;
            background-color: #FFFFFF !important;
            overflow: hidden !important;
        }
        div[data-testid="stChatInput"]:focus-within {
            border: 1px solid #94A3B8 !important;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.08) !important;
        }
        /* Strip internal Streamlit focus styling */
        div[data-testid="stChatInput"] > div, 
        div[data-testid="stChatInput"] > div:focus-within {
            border: none !important;
            box-shadow: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session states
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None

# --- Sidebar ---
with st.sidebar:
    st.markdown("<div class='sidebar-header'>⚖️ NyayaAI</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #059669; font-weight: bold;'>🟢 Active Session</p>", unsafe_allow_html=True)
    st.divider()
    
    st.markdown("### 📄 Document Upload")
    uploaded_file = st.file_uploader("Upload PDF or DOCX", type="pdf", accept_multiple_files=False, label_visibility="collapsed")
    
    if uploaded_file:
        if uploaded_file.name != st.session_state.uploaded_filename:
            st.session_state.uploaded_filename = uploaded_file.name
            with st.spinner("Indexing document..."):
                file_path = upload_pdf(uploaded_file)
                index_pdf(file_path)
            st.success(f"Loaded: {uploaded_file.name}")
        else:
            st.success(f"Loaded: {uploaded_file.name}")
            
        st.divider()
        st.markdown("### 🔍 Document Actions")
        
        if st.button("✨ Generate Summary", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Please generate a detailed, comprehensive summary of the uploaded document, highlighting the main purpose, key arguments, and critical details."})
            st.rerun()
            
        if st.button("🚩 Analyze Risks", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Please analyze this document for risk flags. List the risks with their severity (High, Medium, Low) and provide a brief description for each. Format nicely in markdown."})
            st.rerun()
            
    st.divider()
    
    if st.button("🗑️ Clear Chat & Start New", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.session_state.uploaded_filename = None
        st.rerun()

# --- Main Layout (Chat Interface) ---
st.title("NyayaAI Chat")

for msg in st.session_state.messages:
    avatar_icon = "⚖️" if msg["role"] == "assistant" else "👤"
    st.chat_message(msg["role"], avatar=avatar_icon).write(msg["content"])

# Process AI generation if the last message was from the user
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    user_query = st.session_state.messages[-1]["content"]
    with st.chat_message("assistant", avatar="⚖️"):
        with st.spinner("Generating response..."):
            history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[:-1][-5:]])
            
            if st.session_state.uploaded_filename:
                retrieved_docs = retrieve_docs(user_query, st.session_state.uploaded_filename)
            else:
                retrieved_docs = [] # General query
                
            response = answer_query(documents=retrieved_docs, model=llm_model, query=user_query, history=history)
            st.write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Chat input (always at the bottom)
if prompt := st.chat_input("Ask questions about the attached document or general query..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()