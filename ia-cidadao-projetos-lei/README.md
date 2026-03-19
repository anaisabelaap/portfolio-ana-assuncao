# 🏛️ IA para o Cidadão — Legislative Bill Analyzer

> Data & AI Portfolio Project  
> Ana Isabel Assunção · [LinkedIn](https://www.linkedin.com/in/ana-isabel-assuncao-ap/)

---

## Overview

Brazilian legislative bills (Projetos de Lei) are dense, technical documents written in legal language that most citizens cannot easily understand or track. This project automates the analysis of any bill using GPT-4o-mini, making civic information accessible to everyone.

**Test document:** PL 2338/2023 — the Brazilian Artificial Intelligence Regulation Bill, one of the most significant tech policy proposals currently under debate in Congress.

---

## The Problem

Brazil's Chamber of Deputies publishes hundreds of bills per year as public PDFs. The language is technical, the documents are long, and there is no accessible tool for a citizen to quickly understand what a bill proposes, who it affects, or what its risks are.

---

## Solution

A Python pipeline that:
1. Extracts text from any PDF bill using `pdfplumber`
2. Sends the text to GPT-4o-mini with carefully engineered prompts
3. Returns a structured JSON with summary, topic classification, and plain-language explanation

---

## Project Structure

```
ia-cidadao-projetos-lei/
├── analise_pl.ipynb          ← Main demonstrative notebook
├── src/
│   ├── extract_text.py       ← PDF text extraction (CLI tool)
│   ├── helper_functions.py   ← OpenAI API pipeline functions
│   └── prompts.py            ← Prompt templates
├── data/
│   ├── PL2338_2023.pdf       ← Source bill (input)
│   ├── out_texts/
│   │   └── PL2338_2023.txt   ← Extracted text
│   └── resultado_pl.json     ← Analysis output (real API run)
└── requirements.txt
```
Note: PDF and extracted text files are not included in this repository. Download any bill from camara.leg.br and run extract_text.py to generate them.
---

## Key Technical Decisions

**Why pdfplumber?**  
Government PDFs are often scanned or poorly formatted. `pdfplumber` handles both text-based and complex layout PDFs better than `PyPDF2` for Brazilian government documents specifically.

**Why separate prompt templates?**  
Each task (summarization, classification, explanation) has a different cognitive goal and requires a different LLM instruction style. Keeping prompts in a dedicated `prompts.py` file makes them easy to iterate and test independently without touching the pipeline logic.

**Why GPT-4o-mini?**  
Legislative bills can be very long. GPT-4o-mini offers a 128k context window at low cost, making it practical to send entire bills without chunking. For production use with very long bills, a chunking + map-reduce summarization strategy would be added.

**Why structured JSON output?**  
The pipeline outputs a clean JSON file designed for downstream use — feeding into a Streamlit dashboard, a database, or an API response. The structure is consistent regardless of which bill is analyzed.

---

## Sample Output

Real output from analyzing PL 2338/2023 (see `data/resultado_pl.json`):

**Category:** `Tecnologia e Inovação`

**Summary (excerpt):** The bill establishes rules for the responsible development and use of AI systems in Brazil, protecting fundamental rights and ensuring safety and reliability. It emphasizes human oversight, transparency, auditability, and the right to contest automated decisions.

**Citizen-friendly explanation (key points):**
- You have the right to **know** when you're interacting with an AI system
- You can **contest** automated decisions (e.g. credit denial, job rejection)
- **High-risk systems** (health, safety, employment) face stricter requirements
- Companies are **liable** for damages caused by their AI systems

---

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Add your OpenAI API key to a .env file
echo "OPENAI_API_KEY=your-key-here" > .env

# Extract text from a PDF bill
python -m src.extract_text data/PL2338_2023.pdf -o data/out_texts/

# Run the analysis notebook
jupyter notebook analise_pl.ipynb
```

---

## Stack

`Python` · `pdfplumber` · `OpenAI API (GPT-4o-mini)` · `Prompt Engineering` · `python-dotenv` · `JSON`
