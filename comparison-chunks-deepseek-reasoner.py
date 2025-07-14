# Programa para clasificar planes de gobierno de acuerdo a una lista de afirmaciones
# usando el , y deepseek-reasoner con su API
# LICENCIA: GPLv3. (C) Rodrigo Garcia 2025

import requests
import json
import os
import re
from collections import defaultdict
from utils import list_markdown_files, load_markdown_files, get_markdown_file, get_markdown_sections


# Configuration
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"
PLANS_DIR = "programas"
SUMMARY_PLANS_DIR = "programas/summaries"
STATEMENTS_FILE = 'afirmaciones1_rg.md'


def chunk_document(content, chunk_size=5000):
    """Split document into manageable chunks using semantic boundaries"""
    chunks = []
    current_chunk = ""
    
    # Split by major sections (## headings)
    # TODO: Find and analize the use of langchain_text_splitters
    sections = re.split(r'\n## ', content)
    for section in sections:
        if not section.strip():
            continue
            
        # Add heading back if it was removed by split
        if not section.startswith('#'):
            section = "## " + section
            
        # Further split large sections
        if len(section) > chunk_size:
            sub_sections = re.split(r'\n### |\n- ', section)
            for sub in sub_sections:
                if len(current_chunk) + len(sub) < chunk_size:
                    current_chunk += sub + "\n"
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sub + "\n"
        else:
            if len(current_chunk) + len(section) < chunk_size:
                current_chunk += section + "\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = section + "\n"
    
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks


def deepseek_chat(prompt, context="", temperature=0.1, max_tokens=5000):
    """Call DeepSeek Reasoning API"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = [{"role": "user", "content": prompt}]
    if context:
        messages.insert(0, {"role": "system", "content": context})
    
    payload = {
        "model": "deepseek-reasoner",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    response = requests.post(API_ENDPOINT, headers=headers, json=payload)
    return response.json()


def summarize_plan(plan_name, content):
    """Generate a structured summary of a government plan"""
    prompt = f"""
Generate a structured summary of the government plan "{plan_name}" using this format in spanish language:

## {plan_name} Summary
### Objetivos principales
- Objetivo 1
- Objetivo 2

### Pilares o principios principales
- Pilar 1
- Pilar 2

### Actores involucrados
- Actor 1
- Actor 2
    
### Desarrollo económico e industrial
- Política o estrategia 1
- Política o estrategia 2

#### Sectores objetivo
- Sector 1
- Sector 2
    
#### Medidas y acciones concretas
- Medida 1 (Presupuesto: $, Plazo de Implementación)
- Medida 2 (Presupuesto: $, Plazo de Implementación)

### Construcción y administración del estado

#### Políticas tributarias
- Política 1
- Política 2

##### Medidas y acciones concretas
- Medida 1 (Presupuesto: $, Plazo de Implementación)
- Medida 2 (Presupuesto: $, Plazo de Implementación)

#### Optimización de procesos estatales

##### Medidas y acciones concretas
- Medida 1 (Presupuesto: $, Plazo de Implementación)
- Medida 2 (Presupuesto: $, Plazo de Implementación)

### Políticas agropecuarias y forestales

#### Sectores objetivo
- Sector 1
- Sector 2

#### Medidas y acciones concretas
- Medida 1 (Presupuesto: $, Plazo de Implementación)
- Medida 2 (Presupuesto: $, Plazo de Implementación)

### Justicia

#### Medidas y acciones concretas
- Medida 1 (Presupuesto: $, Plazo de Implementación)
- Medida 2 (Presupuesto: $, Plazo de Implementación)

### Ciencia y tecnología

#### Medidas y acciones concretas
- Medida 1 (Presupuesto: $, Plazo de Implementación)
- Medida 2 (Presupuesto: $, Plazo de Implementación)

### Educación y arte

#### Sectores objetivo
- Sector 1
- Sector 2

#### Medidas y acciones concretas
- Medida 1 (Presupuesto: $, Plazo de Implementación)
- Medida 2 (Presupuesto: $, Plazo de Implementación)
    
### Recursos naturales y energía

#### Políticas principales

- Política 1
- Política 2

#### Medidas y acciones concretas
- Medida 1 (Presupuesto: $, Plazo de Implementación)
- Medida 2 (Presupuesto: $, Plazo de Implementación)

### Política exterior

#### Políticas principales
- Política 1
- Política 2

#### Medidas y acciones concretas
- Medida 1 (Presupuesto: $, Plazo de Implementación)
- Medida 2 (Presupuesto: $, Plazo de Implementación)

### Bienestar social y migración

#### Políticas principales    
- Política 1
- Política 2

#### Sectores objetivo
- Sector 1
- Sector 2
#### Medidas y acciones concretas
- Medida 1 (Presupuesto: $, Plazo de Implementación)
- Medida 2 (Presupuesto: $, Plazo de Implementación)

### Medio ambiente y tierras

#### Políticas principales    
- Política 1
- Política 2

#### Medidas y acciones concretas
- Medida 1 (Presupuesto: $, Plazo de Implementación)
- Medida 2 (Presupuesto: $, Plazo de Implementación)

Plan content:
{content[:20000]}  # Only send beginning for summarization
"""
    response = deepseek_chat(prompt)
    print(response)
    print()
    return response['choices'][0]['message']['content']


def summarize_large_plan(content):
    """Generate a summarizations from chunks of document sections"""
    chunks = chunk_document(content)
    summaresi = []
    for chunk in chunks:
        response = deepseek_chat(f"Summarize this policy section: {chunk}")
        summaries.append(response)
    return "\n".join(summaries)


def compare_plans(plans, statement, statement_name, load_from_disk=False):
    """Compare multiple plans against a statement"""
    # Step 1: Summarize each plan
    summaries = {}
    for name, content in plans.items():

        filename = f"{SUMMARY_PLANS_DIR}/{name}.summary.md"
        if load_from_disk is True and os.path.isfile(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                summaries[name] = f.read()
                print(f'Resumen cargado de {filename}')
        else:
            summaries[name] = summarize_plan(name, content)
            print(f"Resumen generado para {name}")
            print(f' ****\n {summaries[name]} \n.')
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(summaries[name])
                print(f'Resumen guardado en {filename}')
            
    # Step 2: Create comparison context
    context = "## Government Plan Summaries\n"
    for name, summary in summaries.items():
        context += f"\n### {name}\n{summary}\n"
    
    # Step 3: Generate comparison
    prompt = f"""
You are a policy analyst evaluating alignment between statements and government plans ALL in spanish language.
Perform comparative analysis of government plans regarding the following statement named:
    "{statement_name}" with content: "{statement}"

### Tasks:
1. Compare alignment of ALL plans (0-10 scale)
2. Identify BEST aligned plan with:
   - Specific policy references
   - Key quotes showing alignment
   - It has mas more data and facts to support the statement
   - It has more mentions and descriptions
   - It contains more estimations and strategies to support the statement
3. Identify WORST aligned plan with:
   - Policy contradictions
   - Evidence of misalignment
   - It has poor descriptions, less mentions or worse support with data, facts or strategies
4. Provide detailed justifications in spanish language

### Output Format (JSON):
{{
  "statement": "Original statement",
  "comparisons": [
    {{
      "plan_name": "Plan A",
      "alignment_score": 7,
      "key_evidence": [
        "Excerpt from plan",
        "Budget allocation detail"
      ],
      "justification": "Explanation of alignment"
    }}
  ],
  "best_aligned": {{
    "plan_name": "Plan X",
    "primary_reason": "Key reason",
    "strongest_evidence": "Most relevant quote"
  }},
  "second_best_aligned": {{
    "plan_name": "Plan X",
    "primary_reason": "Key reason",
    "strongest_evidence": "Most relevant quote"
  }},
  "second_worst_aligned": {{
    "plan_name": "Plan X",
    "primary_reason": "Key reason",
    "strongest_evidence": "Conflicting policy text"
  }},
  "worst_aligned": {{
    "plan_name": "Plan Y",
    "primary_reason": "Key reason",
    "contradictory_evidence": "Conflicting policy text"
  }}
}}
"""
    response = deepseek_chat(prompt, context=context)
    print(response)
    content = response['choices'][0]['message']['content']
    
    # Extract JSON from response
    try:
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        return json.loads(content[json_start:json_end])
    except Exception as e:
        print(f'Error JSON parsinf failed', e)
        return content


def save_statement_comparison(statement_name, evaluation: str, as_json=True):
    """Saves the given statement name evaluation from comparison among all plans results.
    Saves in a filename wiht format {statement_name}_YYYY-MM-DD_comparisson inside
    data/comparissons folder
    """

    filename = f"data/{statement_name}_{dt.strftime(dt.now(), '%Y-%m-%d')}_comparisson"

    if as_json:
        filename += '.json'

    with open(filename, 'w', encoding='utf-8', newline='') as f:
        if as_json:
            json.dump(evaluation, f, indent=2, ensure_ascii=False)
        else:
            f.write(evaluation)

    print(f"Saved comparisson to {filename}")

    
# ===================== Main execution ======================
if __name__ == "__main__":

    plans = {}
    # Loading government plans
    government_plan_files = list_markdown_files(PLANS_DIR)

    for prog_gobierno in government_plan_files:
        _plan = get_markdown_file(PLANS_DIR, prog_gobierno)
        plans[_plan['name']] = _plan['content']
    
    # Statements to evaluate (in Spanish)
    statements_document = get_markdown_file(".", STATEMENTS_FILE, clean=False)
    statement_sections = get_markdown_sections(statements_document['content'])
    
    # Compare plans
    for statement in statement_sections:
        name = statement.metadata["H2"]
        content = statement.page_content
        print(f'\n\n Comparando para {name} ****\n{content}')
        results = compare_plans(plans, content, name, load_from_disk=True)
        print(' ------------ respuesta ---------------------')
        print(results)

        try:
            save_statement_comparison(name, results, as_json=False)
        except Exception as E:
            print(f"No se pudo guardar como texto plano {name}")
            print(E)

        try:
            response_json = json.loads(results)
            save_statement_comparison(name, response_json, as_json=True)
        except Exception as E:
            print(f"No se pudo guardar como json {name}")
            print(E)
        
    print('Finalizado.')
