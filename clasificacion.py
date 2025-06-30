# Programa para clasificar planes de acuerdo a una lista de afirmaciones usando llms

# from langchain_core.prompts import ChatPromptTemplate
# from langchain_ollama.llms import OllamaLLM

import ollama
import os

from utils import list_markdown_files, load_markdown_files, get_markdown_file, get_markdown_sections

def ask_deepseek(question: str, context: str, model: str = "deepseek-r1:1.5b") -> str:
    """Query DeepSeek via Ollama with engineered prompt"""
    prompt = f"""
[SYSTEM ROLE]
You are a policy analyst that review documents in markdown format and help to determine how much those documents are aligned with given afirmations.
".

[CONTEXT]
{context}

[INSTRUCTIONS]
1. Revisa en detalle documento  sin resumirlo, intenta memorizar tanto como se posible.
2. Revisa las afirmaciones que se te den.
3. Busca en el documento información que resplade a las afirmaciones dadas.
4. Emite una puntuación de 0 a 100% respecto a qué tan alineada está cada afirmación con el documento dado.    
5. Cuando se te pida evaluar una afirmación, debes citar las secciones del documento que respalden la puntuación.
6. Las preguntas serán en español y debes también responder en este idioma.

[QUESTION]
{question}
"""
    
    response = ollama.chat(
        model=model,
        messages=[{'role': 'user', 'content': prompt}],
        options={'temperature': 0.2}
    )
    return response['message']['content']


if __name__ == "__main__":
    # Configuration
    DOCS_DIR = "programas/"  # Directory with markdown files
    #MODEL = "deepseek-r1:14b-qwen-distill-q8_0"  # Ollama model name
    MODEL = "deepseek-r1:1.5b"  # Ollama model name

    # Statements
    statements_document = get_markdown_file(".", "afirmaciones1_rg.md", clean=False)
    statement_sections = get_markdown_sections(statements_document['content'])
    archivos_programas_de_gobierno = list_markdown_files(DOCS_DIR)

    # For every document, evaluate with every statement
    for prog_gobierno in archivos_programas_de_gobierno:
        print(f"========= Analizando {prog_gobierno} ==============\n\n")
        content = get_markdown_file(DOCS_DIR, prog_gobierno)['content']

        for statement in statement_sections:
            question = f"""
            Evalúa la afirmación llamada: ${statement.metadata['H2']} con el siguiente contenido:
            {statement.page_content}
            """
            print(f'Afirmación: {statement.page_content}\n---------------------------\n')
            respuesta = ask_deepseek(question, content, MODEL)
            print(respuesta)
            # TODO: Guardar como csv o json
            print('---------------------------')
    
    # Load context
    #context = load_markdown_files(DOCS_DIR)
    
    # Interactive QA loop
    while True:
        question = input("\nYour question (type 'exit' to quit): ")
        if question.lower() == 'exit':
            break
        print("\nThinking...")
        answer = ask_deepseek(question, context, MODEL)
        print(f"\nANSWER: {answer}")
