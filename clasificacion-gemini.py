import google.generativeai as genai
import os
import textwrap
import re
from utils import list_markdown_files, load_markdown_files, get_markdown_file, get_markdown_sections


genai.configure(api_key='API KEY')


def analyze_government_docs(question: str, context: str) -> str:
    """Analyze government documents using Gemini"""
    # Select the best model for policy analysis
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
    prompt = f"""
**Role**: Senior Policy Analyst Assistant
**Task**: Analyze government planning documents to answer questions

**Context Documents** (Markdown format):
{context}

**User Question**:
{question}

**Response Requirements**:
1. Answer ONLY using information from provided documents
2. Cite specific document names and section headers
3. Compare policies across documents when relevant
4. Highlight potential implementation challenges
5. Format key points as bullet lists
6. If information is insufficient, state what's missing
7. The context and questions are in spanish, the answer must be spanish as well.

**Output Format**:
[Summary]
Give a rate between 0 to 100% about how much do the given statement is aligned with the context document.

[Analysis]
Detailed response with citations

[Recommendations]
Actionable suggestions based on documents
"""
    
    response = model.generate_content(prompt)
    return textwrap.indent(response.text, "> ")


if __name__ == "__main__":
    DOCS_DIR = "programas/"  # Directory with markdown files

    # Statements
    statements_document = get_markdown_file(".", "afirmaciones1_rg.md", clean=False)
    statement_sections = get_markdown_sections(statements_document['content'])

    archivos_programas_de_gobierno = list_markdown_files(DOCS_DIR)

    for prog_gobierno in archivos_programas_de_gobierno:
        print(f"========= Analizando {prog_gobierno} ==============\n\n")
        content = get_markdown_file(DOCS_DIR, prog_gobierno)['content']

        for statement in statement_sections:
            question = f"""
            Evalúa la afirmación llamada: ${statement.metadata['H2']} con el siguiente contenido:
            {statement.page_content}
            """
            print(f'Afirmación: {statement.page_content}\n---------------------------\n')
            respuesta = analyze_government_docs(question, content)
            print(respuesta)
            # TODO: Guardar como csv o json
            print('---------------------------')
            
