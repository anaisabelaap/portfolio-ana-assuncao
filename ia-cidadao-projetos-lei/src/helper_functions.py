"""
helper_functions.py
-------------------
Utility functions for the IA para o Cidadão pipeline.
Handles OpenAI API calls for summarization, classification,
and simplified explanation of Brazilian legislative bills.
"""

import os
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI


# ── Environment setup ──────────────────────────────────────────────────────────
load_dotenv(find_dotenv())
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4o-mini"
TEMPERATURE = 0.0


# ── Core LLM call ──────────────────────────────────────────────────────────────
def get_llm_response(prompt: str, system_message: str | None = None) -> str:
    """
    Sends a prompt to the OpenAI API and returns the model's response as a string.

    Args:
        prompt: The user message / filled prompt template.
        system_message: Optional system instruction. Defaults to a legislative
                        analyst persona if not provided.

    Returns:
        The model's text response.
    """
    if system_message is None:
        system_message = (
            "Você é um analista legislativo especializado em políticas públicas "
            "brasileiras. Responda de forma clara, objetiva e acessível ao cidadão."
        )

    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
        temperature=TEMPERATURE,
    )
    return completion.choices[0].message.content


# ── Pipeline functions ─────────────────────────────────────────────────────────
def summarize(bill_text: str, prompt_template: str) -> str:
    """
    Generates a summary of a legislative bill.

    Args:
        bill_text: Full extracted text of the bill.
        prompt_template: Prompt string with a {texto} placeholder.

    Returns:
        Summary as a string.
    """
    prompt = prompt_template.format(texto=bill_text)
    return get_llm_response(prompt)


def classify(bill_text: str, prompt_template: str) -> str:
    """
    Classifies a legislative bill into a topic category.

    Args:
        bill_text: Full extracted text of the bill.
        prompt_template: Prompt string with a {texto} placeholder.

    Returns:
        Category name as a string.
    """
    prompt = prompt_template.format(texto=bill_text)
    return get_llm_response(prompt)


def explain(bill_text: str, prompt_template: str) -> str:
    """
    Generates a simplified, citizen-friendly explanation of a legislative bill.

    Args:
        bill_text: Full extracted text of the bill.
        prompt_template: Prompt string with a {texto} placeholder.

    Returns:
        Simplified explanation as a string.
    """
    prompt = prompt_template.format(texto=bill_text)
    return get_llm_response(prompt)


def analyze_bill(bill_text: str, prompts: dict) -> dict:
    """
    Runs the full analysis pipeline on a bill: summary, classification,
    and simplified explanation.

    Args:
        bill_text: Full extracted text of the bill.
        prompts: Dictionary with keys 'summary', 'classification', 'explanation'
                 mapping to their respective prompt templates.

    Returns:
        Dictionary with keys 'resumo', 'categoria', 'explicacao_simplificada'.
    """
    print("📄 Gerando resumo...")
    resumo = summarize(bill_text, prompts["summary"])

    print("🏷️  Classificando tema...")
    categoria = classify(bill_text, prompts["classification"])

    print("💬 Gerando explicação simplificada...")
    explicacao = explain(bill_text, prompts["explanation"])

    return {
        "resumo": resumo,
        "categoria": categoria,
        "explicacao_simplificada": explicacao
    }
