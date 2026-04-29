import streamlit as st
import os
from pathlib import Path
from src.helper_functions import analyze_bill
from src.extract_text import extract_pdf_to_text
from src.prompts import (
    SUMMARY_PROMPT,
    CLASSIFICATION_PROMPT,
    SIMPLIFIED_EXPLANATION_PROMPT
)

# --- Page Configuration ---
st.set_page_config(
    page_title="IA para o Cidadão | AI Policy Analyzer",
    page_icon="🏛️",
    layout="centered"
)

# --- Custom CSS for Professional Look ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        font-weight: 600;
    }
    .result-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- Header Section ---
col1, col2 = st.columns([1, 5])
with col1:
    st.title("🏛️")
with col2:
    st.title("IA para o Cidadão")
    st.caption("Democratizando o acesso à legislação brasileira através de IA Generativa.")

st.markdown("---")

# --- Sidebar / Settings ---
with st.sidebar:
    st.header("⚙️ Configurações")
    st.info("Este projeto utiliza **GPT-4o-mini** para processar documentos legislativos complexos.")
    
    demo_mode = st.toggle("Modo de Demonstração", value=False, help="Ative para visualizar resultados sem necessidade de API Key.")
    
    api_key = st.text_input(
        "OpenAI API Key", 
        type="password", 
        disabled=demo_mode,
        placeholder="sk-..."
    )
    
    if api_key and not demo_mode:
        os.environ["OPENAI_API_KEY"] = api_key

    st.divider()
    st.markdown("### Sobre a Autora")
    st.markdown("[LinkedIn](https://www.linkedin.com/in/ana-isabel-assuncao-ap/)")

# --- Main App Logic ---
st.subheader("1. Upload do Documento")
uploaded_file = st.file_uploader("Arraste ou selecione o PDF do Projeto de Lei (PL)", type="pdf")

if uploaded_file:
    temp_path = Path(f"temp_{uploaded_file.name}")
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    with st.status("Processando documento...", expanded=False) as status:
        st.write("Lendo PDF...")
        txt_path = extract_pdf_to_text(temp_path)
        with open(txt_path, "r", encoding="utf-8") as f:
            bill_text = f.read()
        status.update(label="Texto extraído com sucesso!", state="complete", expanded=False)

    st.subheader("2. Análise da IA")
    if st.button("🚀 Iniciar Análise Inteligente"):
        if not api_key and not demo_mode:
            st.warning("⚠️ Por favor, insira sua OpenAI API Key ou ative o Modo de Demonstração na barra lateral.")
        else:
            if demo_mode:
                with st.spinner("Simulando análise (Demo Mode)..."):
                    # Mock data based on your real project analysis 
                    analysis_results = {
                        "categoria": "Tecnologia e Inovação",
                        "resumo": "O Projeto de Lei nº 2338/2023 estabelece o marco legal da Inteligência Artificial no Brasil. O texto foca na proteção de direitos fundamentais, na governança de sistemas de alto risco e na definição de responsabilidades para fornecedores e operadores de IA.",
                        "explicacao_simplificada": "Imagine um manual de regras para robôs e empresas. Este projeto garante que você saiba quando uma IA é usada e que ela não pode te discriminar injustamente."
                    }
            else:
                with st.spinner("Analisando cláusulas e termos técnicos..."):
                    prompts_map = {
                        "summary": SUMMARY_PROMPT,
                        "classification": CLASSIFICATION_PROMPT,
                        "explanation": SIMPLIFIED_EXPLANATION_PROMPT
                    }
                    analysis_results = analyze_bill(bill_text, prompts_map)

            # --- Results Display ---
            st.success("Análise concluída!")
            
            # Category Highlight
            st.markdown(f"""
                <div class="result-card">
                    <span style='color: #666; font-size: 0.9em;'>TEMA IDENTIFICADO</span>
                    <h3 style='margin-top: 0;'>🏷️ {analysis_results['categoria']}</h3>
                </div>
            """, unsafe_allow_html=True)
            
            st.write("") # Spacer

            tab_summary, tab_explanation = st.tabs(["📄 Resumo Técnico", "💡 Linguagem Cidadã"])
            
            with tab_summary:
                st.markdown(analysis_results["resumo"])
            
            with tab_explanation:
                st.info(analysis_results["explicacao_simplificada"])

    # Cleanup
    if temp_path.exists(): os.remove(temp_path)
    if txt_path.exists(): os.remove(txt_path)