
import os
import json
import time
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from google import genai
from google.genai import types
from collections import defaultdict


from prompts import MANUALLY_SELECTED_EXAMPLES, PROMPT_TEMPLATE_EXP_10

# ======================================================================================
# --- CONFIGURATION ---
# ======================================================================================
load_dotenv()
API_KEY = os.getenv('TOKEN')
if not API_KEY:
    raise ValueError("ERREUR: TOKEN Gemini introuvable. Vérifiez votre fichier .env")

# Chemins des fichiers
INPUT_TEST_FILE = "data/test_v4.jsonl"
LEXICON_FILE = "data/lexique-des-acronymes-sncf.json"
BATCH_FILE = "batch_requests.jsonl"
OUTPUT_FILE = "submissions/submission.csv"
DEBUG_FILE = "debug_results.jsonl"
NUM_FEW_SHOTS = 4
MAX_TEST_EXAMPLES_TO_PROCESS = None
MODEL_NAME = 'gemini-2.5-pro' # Ou 'gemini-3-pro-preview' maintenant

# ======================================================================================
# --- FONCTIONS UTILITAIRES ---
# ======================================================================================
def load_examples(file_path): 
    """Charge les exemples depuis un fichier .jsonl.""" 
    try: 
        with open(file_path, 'r', encoding='utf-8') as f: 
            return [json.loads(line) for line in f] 
    except FileNotFoundError: 
        print(f"ERREUR: Le fichier {file_path} est introuvable.") 
        return []

def load_sncf_lexicon(file_path):
    """Charge le lexique et le structure pour une recherche rapide par acronyme."""
    print(f"Chargement du lexique : {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        definitions_map = defaultdict(list)
        for item in data:
            if item.get('abreviation') and item.get('definition'):
                clean_def = item['definition'].replace('_x000D_\n', ' ').strip()
                definitions_map[item['abreviation']].append(clean_def)
        return definitions_map
    except FileNotFoundError:
        print(f"ERREUR: Le fichier lexique {file_path} est introuvable.")
        return {}
    except json.JSONDecodeError:
        print(f"ERREUR: Le fichier lexique {file_path} n'est pas un JSON valide.")
        return {}

def format_few_shot_example_cot(example): 
    """Formate un exemple avec sa chaîne de pensée (Chain of Thought)."""
    correct_index = -1 
    options_dict = example.get("options", {}) 
    for i, (option, is_correct) in enumerate(options_dict.items()): 
        if is_correct: correct_index = i 
        break

    input_data = {
        "text": example.get("text", ""),
        "acronym": example.get("acronym", ""),
        "options": list(options_dict.keys())
    }

    # Récupère le raisonnement
    raisonnement = example.get("raisonnement", "Aucune réflexion fournie.")

    return f"""---
    Exemple de référence :

    Entrée :

    JSON

    {json.dumps(input_data, ensure_ascii=False, indent=2)}
    Sortie attendue : Réflexion: {raisonnement}

    JSON

    {{
    "index_correct": {correct_index}
    }}
    ```"""

if __name__ == "__main__":
    client = genai.Client(api_key=API_KEY)

    print("Étape 0: Chargement du lexique SNCF...")
    sncf_lexicon = load_sncf_lexicon(LEXICON_FILE)
    if not sncf_lexicon:
        print("AVERTISSEMENT: Le lexique est vide. L'injection de connaissances RAG sera désactivée.")

    print("Étape 1: Préparation du fichier d'entrée pour le traitement par lot...")
    gold_examples = MANUALLY_SELECTED_EXAMPLES[:NUM_FEW_SHOTS]
    
    few_shot_prompt_part = "\n".join([format_few_shot_example_cot(ex) for ex in gold_examples])
    
    test_examples = load_examples(INPUT_TEST_FILE)
    if not test_examples:
        exit()

    with open(BATCH_FILE, 'w', encoding='utf-8') as f:
        for example in tqdm(test_examples, desc="Génération des requêtes RAG"):
            example_id = example.get('id')
            acronym_to_find = example.get("acronym", "")
            
            input_data = {
                "text": example.get("text", ""),
                "acronym": acronym_to_find,
                "options": example.get("options", [])
            }

            definitions = sncf_lexicon.get(acronym_to_find, [])
            if not definitions:
                lexicon_context_str = "Aucune définition trouvée dans le lexique SNCF pour cet acronyme."
            else:
                lexicon_context_str = "Voici des définitions connues (source: lexique SNCF) :\n" + "\n".join([f"- {d}" for d in definitions])

            prompt = PROMPT_TEMPLATE_EXP_10.format(
                example_json=json.dumps(input_data, ensure_ascii=False, indent=2),
                acronym=acronym_to_find,
                lexicon_context=lexicon_context_str
            )
            
            request = {
                "custom_id": example_id,
                "request": {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generation_config": {"temperature": 0}
                }
            }
            f.write(json.dumps(request) + '\n')
        
        print(f"Fichier d'entrée '{BATCH_FILE}' créé avec {len(test_examples)} requêtes.")

    print(f"\nÉtape 2: Envoi du fichier '{BATCH_FILE}' et création du job batch...")
    
    uploaded_file = client.files.upload(
        file=BATCH_FILE,
        config=types.UploadFileConfig(display_name='batch-input-file-rag', mime_type='text/plain')
    )
    
    batch_job = client.batches.create(
        model=f"models/{MODEL_NAME}",
        src=uploaded_file.name,
        config={'display_name': "inference_job_desambiguisation_rag"}
    )
    print(f"Job batch créé: {batch_job.name}. Le traitement démarre en arrière-plan.")

    print("\nÉtape 3: Surveillance du statut du job (vérification toutes les 30s)...")
    
    completed_states = {'JOB_STATE_SUCCEEDED', 'JOB_STATE_FAILED', 'JOB_STATE_CANCELLED', 'JOB_STATE_EXPIRED'}

    while batch_job.state.name not in completed_states:
        print(f"  - Statut actuel: {batch_job.state.name}")
        time.sleep(30)
        batch_job = client.batches.get(name=batch_job.name)

    print(f"Job terminé avec le statut: {batch_job.state.name}")

    if batch_job.state.name == 'JOB_STATE_SUCCEEDED':
        print("\nÉtape 4: Le job a réussi. Récupération et traitement des résultats...")
        
        result_file_name = batch_job.dest.file_name
        result_file_content = client.files.download(file=result_file_name).decode('utf-8')

        print("--- CONTENU BRUT DU FICHIER DE RÉSULTATS (pour débogage) ---")
        print(result_file_content[:2000]) 
        with open(DEBUG_FILE, "w", encoding="utf-8") as f:
            f.write(result_file_content)
        print(f"--- Le contenu brut a été sauvegardé dans le fichier {DEBUG_FILE} ---")
        
        submission_map = {}
        result_lines = result_file_content.strip().split('\n')

        for line in tqdm(result_lines, desc="Parsing des résultats"):
            original_id = "inconnu" # Valeur par défaut
            try:
                result = json.loads(line)
                original_id = result.get("custom_id")

                if "response" not in result or "candidates" not in result["response"]:
                    tqdm.write(f"AVERTISSEMENT: Pas de réponse valide pour l'ID {original_id}. Ligne: {line}")
                    submission_map[original_id] = []
                    continue 

                response_text_raw = result["response"]["candidates"][0]["content"]["parts"][0]["text"]
                json_start_index = response_text_raw.find('{')
                json_end_index = response_text_raw.rfind('}')

                if json_start_index != -1 and json_end_index != -1:
                    json_str = response_text_raw[json_start_index : json_end_index + 1]
                    
                    # --- NOUVELLE LOGIQUE DE PARSING (gère listes et entiers) ---
                    parsed_json = json.loads(json_str)
                    correct_indices = parsed_json.get("index_correct", -1)

                    if correct_indices == -1:
                        submission_map[original_id] = []  # Cas -1
                    elif isinstance(correct_indices, list):
                        # Cas multi-label (pour l'expérience D)
                        submission_map[original_id] = [str(idx) for idx in correct_indices]
                    else:
                        # Cas single-label (pour les expériences A et C)
                        submission_map[original_id] = [str(correct_indices)]
                    # --- FIN DE LA NOUVELLE LOGIQUE ---
                        
                else:
                    tqdm.write(f"AVERTISSEMENT: Impossible de trouver un bloc JSON pour l'ID {original_id}. Réponse brute: {response_text_raw}")
                    submission_map[original_id] = []
                
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                tqdm.write(f"AVERTISSEMENT: Erreur de parsing inattendue pour l'ID {original_id}. Erreur: {e}")
                submission_map[original_id] = []

        print("\nCréation du fichier de soumission final...")
        submission_df = pd.DataFrame(test_examples)[['id']]
        submission_df['prediction'] = submission_df['id'].apply(lambda x: '[' + ','.join(submission_map.get(x, [])) + ']')
        
        # S'assurer que le dossier de soumission existe
        os.makedirs("submissions", exist_ok=True)
        submission_df.to_csv(OUTPUT_FILE, index=False)
        print(f"\nInférence terminée. Le fichier de soumission est prêt : {OUTPUT_FILE}")

    else:
        print(f"ERREUR: Le job a échoué. Détails: {batch_job.error}")