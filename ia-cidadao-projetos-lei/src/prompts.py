# ============================================
# PROMPTS — PROJETO IA PARA O CIDADÃO
# ============================================

SUMMARY_PROMPT = """
Você é um analista legislativo especializado em políticas públicas.

Resuma o Projeto de Lei abaixo em até 3 parágrafos claros e objetivos.
Utilize linguagem acessível ao cidadão comum.
Não invente informações nem faça suposições.

Texto do Projeto de Lei:
{texto}
"""


CLASSIFICATION_PROMPT = """
Você é um analista legislativo.

Classifique o Projeto de Lei abaixo em UMA das categorias:
- Saúde
- Educação
- Segurança Pública
- Economia
- Meio Ambiente
- Direitos Humanos
- Infraestrutura
- Tecnologia e Inovação
- Administração Pública

Texto do Projeto de Lei:
{texto}

Responda apenas com o nome da categoria.
"""


SIMPLIFIED_EXPLANATION_PROMPT = """
Explique o Projeto de Lei abaixo como se estivesse falando com
uma pessoa sem formação jurídica.

Use linguagem simples, direta e exemplos práticos, se necessário.

Texto do Projeto de Lei:
{texto}
"""


TOPICS_EXTRACTION_PROMPT = """
A partir do Projeto de Lei abaixo, extraia:
- os principais temas abordados
- os possíveis impactos sociais
- os grupos mais afetados

Responda em formato de lista, com frases curtas e objetivas.

Texto do Projeto de Lei:
{texto}
"""
