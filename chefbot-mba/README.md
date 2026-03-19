# 🍳 ChefBot — AI-Powered Recipe Recommendation

> MBA Final Project | Data Science & AI  
> Ana Isabel Assunção · [LinkedIn](https://www.linkedin.com/in/ana-isabel-assuncao-ap/)

---

## Overview

ChefBot is a conversational assistant that recommends recipes based on ingredients
the user already has at home — reducing food waste through intelligent, accessible AI.

The core insight behind the project: most food waste happens not because people
lack ingredients, but because they lack ideas. ChefBot bridges that gap through
NLP and a recommendation engine integrated into WhatsApp — a channel already used
by virtually every Brazilian household.

---

## The Problem

Food waste in Brazilian households and restaurants is driven largely by ingredients
that expire before being used. A practical, low-friction tool accessible via
WhatsApp could shift behavior without requiring users to install anything new.

---

## Technical Architecture

```
WhatsApp User
     │
     ▼
WhatsApp Business API
     │
     ▼
LangChain Conversation Manager
     │
     ├── spaCy pt_core_news_sm  →  Ingredient extraction from Portuguese free text
     │
     ├── TF-IDF + Cosine Similarity  →  Recipe ranking & recommendation
     │
     └── MongoDB  →  Recipe storage + interaction logging
               │
               ▼
         Power BI Dashboard  →  KPI monitoring
```

---

## What's in This Folder

| File | Description |
|---|---|
| `chefbot_demo.py` | Full demonstrative pipeline: NLP, recommendation engine, chatbot flow, and KPI simulation |
| `requirements.txt` | Python dependencies |

> ⚠️ This notebook is demonstrative. The production version integrates live
> MongoDB, WhatsApp Business API, and a deployed LangChain agent. Architecture
> and logic reflect a production-ready design.

---

## Key Technical Decisions

**Why spaCy with `pt_core_news_sm`?**  
The user communicates in Portuguese. Using an English model would break ingredient
extraction entirely — a common beginner mistake. The Portuguese model correctly
lemmatizes words like "cenouras" → "cenoura" and handles Brazilian informal text.

**Why TF-IDF instead of simple keyword matching?**  
TF-IDF assigns importance weights to terms across the whole recipe corpus.
Rare ingredients (like "cogumelos") get higher weights than common ones (like "sal"),
so recommendations are more meaningful than a basic overlap count.

**Why WhatsApp?**  
98% of Brazilian smartphone users have WhatsApp. A tool that lives inside an app
people already open 20+ times a day has infinitely lower adoption friction than
any dedicated app or website.

---

## KPIs Tracked (Power BI Dashboard)

- Total interactions and unique users (engagement)
- Recommendation satisfaction rate (user feedback)
- Average TF-IDF similarity score per recommendation (quality)
- Estimated food waste avoided per session (impact)
- Top recommended recipes by week (demand patterns)

---

## Stack

`Python` · `spaCy (pt_core_news_sm)` · `scikit-learn` · `TF-IDF` · `LangChain`  
`MongoDB` · `WhatsApp Business API` · `Power BI` · `Pandas` · `NumPy`

---

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt
python -m spacy download pt_core_news_sm

# Run the demo notebook
jupyter notebook chefbot_demo.py
# or open as a Python script
python chefbot_demo.py
```
