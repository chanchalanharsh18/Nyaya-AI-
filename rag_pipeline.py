from langchain_groq import ChatGroq
import os
from vector_database import retrieve_docs as retrieve_filtered_docs
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
load_dotenv()

# Step1: Setup LLM (Use Llama 3.3 70B with Groq)
llm_model = ChatGroq(model="llama-3.3-70b-versatile")

# Step2: Retrieve Docs
def retrieve_docs(query, file_name):
    return retrieve_filtered_docs(query, file_name)

def get_context(documents):
    context = "\n\n".join([doc.page_content for doc in documents])
    return context

# Step3: Answer Question with Follow-Up Support
custom_prompt_template = """
You are NyayaAI, an expert legal assistant specializing in the Indian Constitution, the Indian Penal Code (IPC), Bharatiya Nyaya Sanhita (BNS), and general Indian law.

Your goal is to provide highly accurate, professional, and helpful legal advice.
If the user's question relates to a specific uploaded document, use the context provided below.
If the user's question is a general legal query or asks for advice on charges, risk levels, or legal procedures, use your extensive internal knowledge of Indian law to provide a detailed, accurate answer including relevant Sections, Articles, and Acts.

Previous Conversation:
{history}

Question: {question} 
Context from Uploaded Document (if any):
{context} 

Answer:
"""

def answer_query(documents, model, query, history=""):
    context = get_context(documents)
    prompt = ChatPromptTemplate.from_template(custom_prompt_template)
    chain = prompt | model
    response = chain.invoke({"question": query, "context": context, "history": history})
    return response.content



# Step5: Generate Downloadable Report using ReportLab
def generate_report(user_queries, ai_responses):
    pdf_path = "Nyaya_AI_Report.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Nyaya-AI Report")
    c.setFont("Helvetica", 12)
    c.drawString(100, 730, "Below is a record of your conversation with Nyaya-AI.")
    
    y = 700
    max_width = 450  # Maximum width for text before wrapping
    line_height = 15
    
    for question, answer in zip(user_queries, ai_responses):
        c.setFont("Helvetica-Bold", 12)
        q_lines = simpleSplit(f"Q: {question}", "Helvetica-Bold", 12, max_width)
        a_lines = simpleSplit(f"A: {answer}", "Helvetica", 12, max_width)
        
        for line in q_lines:
            c.drawString(100, y, line)
            y -= line_height
        
        c.setFont("Helvetica", 12)
        for line in a_lines:
            c.drawString(100, y, line)
            y -= line_height
        
        y -= 20  # Extra space between Q&A
        
        if y < 50:  # Prevent text from overflowing
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 750
    
    c.save()
    return pdf_path