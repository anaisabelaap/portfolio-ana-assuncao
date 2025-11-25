# ============================================
# CHEFBOT — NOTEBOOK DEMONSTRATIVO (SIMULADO)
# ============================================

# OBJETIVO:
# Este notebook demonstra, de forma simplificada, o pipeline utilizado
# no projeto ChefBot: análise de ingredientes, extração via NLP,
# criação de base de receitas simulada e recomendação básica.
#
# ATENÇÃO:
# Este notebook usa dados e códigos SIMULADOS, pois o projeto oficial
# envolveu prototipagem e arquitetura conceitual.
# ============================================


# ---------------------------
# IMPORTS
# ---------------------------
import pandas as pd
import spacy

# Carregando modelo pequeno para demonstração
nlp = spacy.load("en_core_web_sm")


# ---------------------------
# Criando uma base simulada de receitas
data = {
    "recipe_id": [1, 2, 3, 4],
    "name": ["Macarrão ao Alho", "Omelete Proteico", "Frango com Legumes", "Arroz Colorido"],
    "ingredients": [
        "macarrão, alho, azeite, sal",
        "ovos, queijo, espinafre, sal",
        "frango, cenoura, abobrinha, alho",
        "arroz, cenoura, ervilha, cebola"
    ]
}

recipes = pd.DataFrame(data)
recipes

# ---------------------------

# Função simples para extrair ingredientes de um texto livre

def extrair_ingredientes(texto):
    doc = nlp(texto)
    tokens = [token.text.lower() for token in doc if not token.is_stop and token.is_alpha]
    return tokens

exemplo_usuario = "Tenho frango, cenoura e um pouco de arroz sobrando"
extrair_ingredientes(exemplo_usuario)

# ---------------------------

# Função para recomendar receitas baseadas nos ingredientes disponíveis
def recomendar(ingredientes_usuario, df):
    df["match"] = df["ingredients"].apply(
        lambda x: len(set(x.split(", ")) & set(ingredientes_usuario))
    )
    recomendadas = df.sort_values(by="match", ascending=False)
    return recomendadas[["name", "ingredients", "match"]]

ingredientes_usuario = ["frango", "cenoura", "arroz"]
recomendar(ingredientes_usuario, recipes)

# ---------------------------

def fluxo_chatbot_simulado(texto_usuario):
    ingredientes = extrair_ingredientes(texto_usuario)
    print("Ingredientes detectados:", ingredientes)

    rec = recomendar(ingredientes, recipes).head(1)

    print("\nRecomendação sugerida:")
    print(rec)

fluxo_chatbot_simulado("Tenho arroz, frango e cenoura sobrando. O que posso fazer?")

# ---------------------------

print(
"""
Este notebook demonstra:
- Base simulada de receitas;
- NLP simplificado com spaCy;
- Recomendações por matching;
- Fluxo inicial do chatbot.

O projeto original inclui:
- Arquitetura em nuvem,
- KPIs de engajamento,
- Dashboard Power BI,
- Simulação de integração via WhatsApp,
- Etapas de projeto ágil.

"""
)
# FIM DO NOTEBOOK DEMONSTRATIVO
