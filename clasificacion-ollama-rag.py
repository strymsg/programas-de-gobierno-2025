# Programa para clasificar planes de gobierno de acuerdo a una lista de afirmaciones
# usando ollama, chroma db y mxbai-embed-large
# LICENCIA: GPLv3. (C) Rodrigo Garcia 2025

import ollama
import chromadb
import json
import os
from datetime import datetime as dt
from chromadb.utils.embedding_functions.ollama_embedding_function import OllamaEmbeddingFunction

from utils import list_markdown_files, load_markdown_files, get_markdown_file, get_markdown_sections


PLANS_DIR = "programas"
EMBEDDING_MODEL = "mxbai-embed-large"
REASONING_MODEL = "mistral"
OUTPUT_DIR = "data/comparisons-rag"

# Initialize Ollama embedding function
ollama_ef = OllamaEmbeddingFunction(
    model_name=EMBEDDING_MODEL,
    url="http://localhost:11434"
)

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="gov_plan_db")
collection = chroma_client.get_or_create_collection(
    name="gov_plans",
    embedding_function=ollama_ef
)


def chunk_document(plan_text, plan_name):
    """Split document preserving semantic structure"""
    chunks = []
    current_chunk = ""
    current_header = "Introduction"
    
    for line in plan_text.split('\n'):
        # TODO: Change chunking to use langchain
        if line.startswith('## '):
            if current_chunk:
                chunks.append({
                    "text": current_chunk.strip(),
                    "header": current_header,
                    "plan": plan_name
                })
            current_header = line[3:].strip()
            current_chunk = ""
        else:
            current_chunk += line + "\n"
    
    if current_chunk:
        chunks.append({
            "text": current_chunk.strip(),
            "header": current_header,
            "plan": plan_name
        })
    
    # Add to ChromaDB
    collection.add(
        documents=[c["text"] for c in chunks],
        metadatas=[{"plan": c["plan"], "section": c["header"]} for c in chunks],
        ids=[f"{plan_name}_{i}" for i in range(len(chunks))]
    )
    return chunks


def compare_plans(statement, statement_name):
    """Comparative analysis using RAG"""
    # Retrieve relevant chunks
    results = collection.query(
        query_texts=[statement],
        n_results=15,
        include=["documents", "metadatas"]
    )
    
    # Group evidence by plan
    plan_evidence = {}
    for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
        plan_name = meta['plan']
        if plan_name not in plan_evidence:
            plan_evidence[plan_name] = []
        plan_evidence[plan_name].append({
            "section": meta['section'],
            "text": doc,
            "plan": meta['plan'],
        })
    
    print("-------- plan evidence ----------")
    print(plan_evidence)

    print('Sending prompt...')
    # Generate comparison prompt
    prompt = f"""
## Government Plan Comparison Task
**Statement**: {statement_name}: "{statement}"

### Retrieved Evidence:
{json.dumps(plan_evidence, indent=2, ensure_ascii=False)}

### Instructions:
1. Compare alignment of ALL plans (0-100 scale) to the given statement with name: {statement_name}
2. To evaluate best plans take into account that:
  - Not only have more mentions and descriptions to support the statement than the others, but also contains data, estimations and facts about it.
  - A plan is generally considered with better alignment if it has more data, facts, strategies and descriptions to support the statement.
  - A plan is generally considered with worse alignment than others if it has poor descriptions, less mentions or worse support with data, facts, or strategies.
  - A plan is considered worse aligned than others if it directly contradicts or is against the statement.
3. Identify BEST aligned plan with:
   - Exact citations (plan + section)
   - Direct quotes
4. Identify WORST aligned plan with contradictions
5. Output JSON with structure:
{{
  "statement": "...",
  "comparisons": {{
    "Plan A": {{
      "score": 7,
      "evidence": [
        {{"plan": "...", "section": "...", "quote": "...", "relevance": "..."}}
      ]
    }}
  }},
  "best_aligned": {{
    "plan": "...",
    "reason": "...",
    "key_evidence": "..."
  }},
  "second_best_aligned": {{
    "plan": "...",
    "reason": "...",
    "key_evidence": "..."
  }},
  "second_worst_aligned": {{
    "plan": "...",
    "reason": "...",
    "contradictory_quote": "..."
  }}
  "worst_aligned": {{
    "plan": "...",
    "reason": "...",
    "contradictory_quote": "..."
  }}
}}
5. All text will be in spanish and output text must be in spanish too.
"""
    # Get comparison from Ollama LLM
    response = ollama.generate(
        model=REASONING_MODEL,
        prompt=prompt,
        options={"temperature": 0.1}
    )
    return json.loads(response['response'])


def save_government_plan_evaluations(plan_name: str, evaluation: str, as_json=True):
    """Saves the given government plan evaluation results using today's date
    in format YYYY-MM-DD_{plan_name}_evaluation inside data/ folder"""
    filename = f"{OUTPUT_DIR}/{plan_name}_{dt.strftime(dt.now(), '%Y-%m-%d')}_evaluation"
    if as_json:
        filename += '.json'

    with open(filename, 'w', encoding='utf-8', newline='') as f:
        if as_json:
            json.dump(evaluation, f, indent=2, ensure_ascii=False)
        else:
            f.write(evaluation)

    print(f"Saved evaluation to {filename}.")


def save_statement_comparisson(statement_name, evaluation: str, as_json=True):
    """Saves the given statement name evaluation from comparisson among all plans results.
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


## ============================ MAIN ============================
if __name__ == "__main__":
    # Statements
    statements_document = get_markdown_file(".", "afirmaciones1_rg.md", clean=False)['content']
    archivos_programas_de_gobierno = list_markdown_files(PLANS_DIR)

    # Chunking and storing every plan in chroma db
    for i, prog_gobierno in enumerate(archivos_programas_de_gobierno):
        print(f"______Procesando y recolectando embedings de {i}: {prog_gobierno}__________\n")
        government_plan = get_markdown_file(PLANS_DIR, prog_gobierno)
        chunk_document(government_plan['content'], government_plan['name'])

    # Statements
    statements_document = get_markdown_file(".", "afirmaciones1_rg.md", clean=False)
    statement_sections = get_markdown_sections(statements_document['content'])        
    
    for statement in statement_sections:
        name = statement.metadata['H2']
        content = statement.page_content
        print(f'\n+++++++++++ Comparando "{name}":\n{content}\n++++++++++++++++')
        results = compare_plans(content, name)
        print(results)
        
        try:
            save_statement_comparisson(name, results, as_json=False)
        except Exception as E:
            print(f"No se pudo guardar como texto plano {name}")
            print(E)

        try:
            save_statement_comparisson(name, results, as_json=True)
        except Exception as E:
            print(f"No se pudo guardar como json {name}")
            print(E)

    print('End.')
