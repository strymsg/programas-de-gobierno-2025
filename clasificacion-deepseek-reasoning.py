# Programa para clasificar planes de gobierno de acuerdo a una lista de afirmaciones
# usando el llms deepseek-reasoner y usando su API
# LICENCIA: GPLv3. (C) Rodrigo Garcia 2025


import json
from openai import OpenAI
import os
from datetime import datetime as dt

from utils import list_markdown_files, load_markdown_files, get_markdown_file, get_markdown_sections


client = OpenAI(
    api_key=os.getenv("OPENAPI_API_KEY"),
    base_url="https://api.deepseek.com")


def evaluate_alignment(government_plan: str, plan_name: str, statements):
    """Ask deepseek how well the given statement align with the given government plan
    """

    system_prompt = f"""
    You are a policy analyst evaluating alignment between statements and government plans.
    Analyze these government plans and evaluate how well each statement aligns with them.
    The government Plan named "{plan_name}" is in Markdown format and spanish language:
    
    {government_plan}
    """

    user_prompt = """
    Evaluate alignment for the following statements in markdown format on 0 to 100 .   
    Have in mind that the statements are in markdown and each level 2 header is the name of the statement followed by the statement's content:"""

    for i, statement in enumerate(statements, 1):
        user_prompt += f"\n{statement}"

    user_prompt += """
    \n\nProvied JSON output with:
    - government_plan_name
    - statement_name: (extract from level 2 header)
    - alignment_score: Take the following approaches to score:
      -100: Fully aligned and supported with data, more than three mentions and related descriptions.
      -80: Clearly aligned but may lack of some details, for instance it mentions and describes the statement but lacks some data to support every proposition.
      -70: Well aligned but lack of details and contains two to three mentions with short descriptions and lack of some data.
      -60: Aligned but lack of many details or data, the plan mentions and describes the statement one or two times, but with little data.
      -50:Pretends to be aligned but is mentioned only once with data and description.
      -40:Pretends to be but poorly aligned due to the breverty of description. Typically there is at most one mention to the statement but with short description and might have no data to support.
      -30: Pretends to be poorly aligned. There is at most a mention to the statement but no description or data to support it.
      -20: Almost not aligned. There is not a mention to the statement but other parts of the plan might be related.
      -0: Not aligned at all. Not even a mention or relation to other statemtns.
    - justification: Cite Government's Plan sections that you used to give the score and what makes it deserve this score.
    - answers must be in spanish language
    """

    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]

    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=messages,
        response_format={
            'type': 'json_object'
        },
        temperature=0.34,
    )

    return response


def save_government_plan_evaluations(plan_name: str, evaluation: str, as_json=True):
    """Saves the given government plan evaluation results using today's date
    in format YYYY-MM-DD_{plan_name}_evaluation inside data/ folder"""
    filename = f"data/{plan_name}_{dt.strftime(dt.now(), '%Y-%m-%d')}_evaluation"
    if as_json:
        filename += '.json'

    with open(filename, 'w', encoding='utf-8', newline='') as f:
        if as_json:
            json.dump(evaluation, f, indent=2, ensure_ascii=False)
        else:
            f.write(evaluation)

    print(f"Saved evaluation to {filename}.")

# ========================= MAIN =========================
if __name__ == "__main__":
    DOCS_DIR = "programas/"  # Directory with markdown files

    # Statements
    statements_document = get_markdown_file(".", "afirmaciones1_rg.md", clean=False)['content']
    #statement_sections = get_markdown_sections(statements_document['content'])
    archivos_programas_de_gobierno = list_markdown_files(DOCS_DIR)

    # For every document, evaluate with every statement
    for i, prog_gobierno in enumerate(archivos_programas_de_gobierno):
        print(f"============= Analizando {i}: {prog_gobierno} =================\n")
        government_plan = get_markdown_file(DOCS_DIR, prog_gobierno)
        
        response = evaluate_alignment(
            government_plan['content'],
            prog_gobierno,
            statements_document)

        print("--------- respuesta -----------------------------------")
        print(' : : : : : : : : contenido : : : : : :')
        print(response.choices[0].message.content)
        
        try:
            save_government_plan_evaluations(
                prog_gobierno,
                response.choices[0].message.content, as_json=False)
        except Exception as E:
            print(f"No se pudo guardar como texto plano {government_plan['name']}")
            print(E)

        try:
            # TODO: revisar por que al json de respuesta le falta un [ al inicio
            response_json = json.loads(f'[ {response.choices[0].message.content}')
            save_government_plan_evaluations(
                prog_gobierno,
                response_json, as_json=True)
        except Exception as E:
            try:
                response_json = json.loads(response.choices[0].message.content)
                save_government_plan_evaluations(
                    prog_gobierno,
                    response_json, as_json=True)
            except Exception as E2:
                print(f"No se pudo guardar como json {government_plan['name']}")
                print(E)
        print('-------------------------------------------------------')

    print('End.')
