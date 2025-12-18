import pandas as pd
import jsonlines
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, classification_report
import joblib
from tqdm import tqdm
import os
import warnings
import json 
from datetime import datetime 

# Ignorer les avertissements pour une sortie plus propre
warnings.filterwarnings('ignore')

# --- CONFIGURATION ---
# Définir les chemins en fonction de la structure du projet
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
EXPERIMENTS_DIR = os.path.join(BASE_DIR, 'experiments')

# Créer les dossiers s'ils n'existent pas
os.makedirs(EXPERIMENTS_DIR, exist_ok=True)

TRAIN_FILE = os.path.join(DATA_DIR, 'train_v2.jsonl')
TEST_FILE = os.path.join(DATA_DIR, 'test_v4.jsonl')
MODEL_NAME = 'baseline_tfidf_logreg'

# --- FONCTIONS DE TRAITEMENT ---

def load_data(file_path):
    """Charge les données depuis un fichier JSON Lines."""
    records = []
    with jsonlines.open(file_path) as reader:
        for obj in reader:
            records.append(obj)
    return records

def preprocess_for_training(data):
    """
    Transforme les données d'entraînement.
    Crée une ligne par option (contexte, acronyme, option) avec un label 0 ou 1.
    """
    processed_data = []
    for record in tqdm(data, desc="Preprocessing Training Data"):
        context = record['text']
        acronym = record['acronym']
        for option, label in record['options'].items():
            # Créer une chaîne de caractères combinant toutes les informations textuelles
            feature_text = f"Acronyme: {acronym}. Contexte: {context}. Option: {option}"
            processed_data.append({
                'feature': feature_text,
                'label': 1 if label else 0
            })
    return pd.DataFrame(processed_data)
    
def preprocess_for_testing(data):
    """
    Transforme les données de test.
    Crée une ligne par option pour la prédiction.
    """
    processed_data = []
    for record in tqdm(data, desc="Preprocessing Test Data"):
        record_id = record['id']
        context = record['text']
        acronym = record['acronym']
        for i, option in enumerate(record['options']):
            feature_text = f"Acronyme: {acronym}. Contexte: {context}. Option: {option}"
            processed_data.append({
                'id': record_id,
                'option_index': i,
                'feature': feature_text
            })
    return pd.DataFrame(processed_data)

# --- SCRIPT PRINCIPAL ---

if __name__ == "__main__":
    print("--- Étape 0: Baseline TF-IDF + Logistic Regression (v2 avec tracking) ---")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment_name = f"{timestamp}_{MODEL_NAME}"
    experiment_dir = os.path.join(EXPERIMENTS_DIR, experiment_name)
    os.makedirs(experiment_dir, exist_ok=True)
    
    # Définition des chemins de sauvegarde pour cette expérience spécifique
    model_save_path = os.path.join(experiment_dir, 'model.joblib')
    submission_file_path = os.path.join(experiment_dir, 'submission.csv')
    report_file_path = os.path.join(experiment_dir, 'report.json')

    print(f"\n[1/6] Démarrage de l'expérience : {experiment_name}")
    print(f"      -> Les résultats seront sauvegardés dans : {experiment_dir}")

    # 2. Chargement des données
    print("\n[2/6] Chargement des données...")
    train_raw = load_data(TRAIN_FILE)
    test_raw = load_data(TEST_FILE)
    print(f"  - {len(train_raw)} exemples d'entraînement chargés.")
    print(f"  - {len(test_raw)} exemples de test chargés.")

    # 2. Prétraitement des données d'entraînement
    print("\n[3/6] Prétraitement des données d'entraînement...")
    train_df = preprocess_for_training(train_raw)
    
    # Séparation des features (X) et de la cible (y)
    X = train_df['feature']
    y = train_df['label']

    # Division en jeux d'entraînement et de validation pour évaluer le modèle
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"  - Données d'entraînement transformées en {len(train_df)} paires (contexte, option).")
    print(f"  - Distribution des labels dans le jeu complet: \n{y.value_counts(normalize=True)}")


    # 3. Entraînement du modèle
    print("\n[4/6] Entraînement du pipeline (TF-IDF + Logistic Regression)...")
    # Création d'un pipeline qui enchaîne la vectorisation TF-IDF et la régression logistique
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=15000)),
        ('clf', LogisticRegression(solver='liblinear', random_state=42, class_weight='balanced'))
    ])
    
    # Entraînement sur le jeu d'entraînement
    pipeline.fit(X_train, y_train)
    
    # Évaluation sur le jeu de validation
    print("  - Évaluation du modèle sur le jeu de validation :")
    y_pred_val = pipeline.predict(X_val)
    f1_val = f1_score(y_val, y_pred_val, average='binary')
    report_dict = classification_report(y_val, y_pred_val, output_dict=True)

    print(f"  - F1-score (validation): {f1_val:.4f}")
    print("    -> Rapport de classification (validation):")
    print(classification_report(y_val, y_pred_val))
    
    # Sauvegarde du modèle
    joblib.dump(pipeline, model_save_path)
    print(f"  - Modèle sauvegardé dans {model_save_path}")

    # 5. Prédiction sur le jeu de test
    print("\n[5/6] Prédiction sur le jeu de test...")
    test_df = preprocess_for_testing(test_raw)
    DECISION_THRESHOLD = 0.5
    test_df['prediction'] = (pipeline.predict_proba(test_df['feature'])[:, 1] > DECISION_THRESHOLD).astype(int)

    # 5. Création du fichier de soumission
    print("\n[6/6] Création des fichiers de résultats...")
    submission_map = {}
    for _, row in test_df.iterrows():
        if row['prediction'] == 1:
            if row['id'] not in submission_map:
                submission_map[row['id']] = []
            submission_map[row['id']].append(str(row['option_index']))

    # Création du DataFrame final de soumission
    submission_df = pd.DataFrame(test_raw)[['id']]
    submission_df['prediction'] = submission_df['id'].apply(lambda x: submission_map.get(x, []))

    # Formattage pour correspondre à l'exemple
    submission_df['prediction'] = submission_df['prediction'].apply(lambda x: '[' + ','.join(x) + ']')

    submission_df.to_csv(submission_file_path, index=False)
    print(f"  - Fichier de soumission sauvegardé dans {submission_file_path}")

    # Fonction utilitaire pour s'assurer que les paramètres sont sérialisables en JSON
    def sanitize_params(params):
        """Convertit les valeurs non-sérialisables d'un dictionnaire en chaînes de caractères."""
        sanitized = {}
        for key, value in params.items():
            # Vérifie si le type de la valeur est l'un des types de base de JSON
            if isinstance(value, (str, int, float, bool, list, dict, type(None))):
                sanitized[key] = value
            else:
                # Si ce n'est pas le cas, on le convertit en sa représentation textuelle
                sanitized[key] = str(value)
        return sanitized

    results_summary = {
        'experiment_name': experiment_name,
        'model_name': MODEL_NAME,
        'timestamp': timestamp,
        'metrics_validation': {
            'f1_score': f1_val,
            'classification_report': report_dict
        },
        'parameters': {
            'tfidf': sanitize_params(pipeline.named_steps['tfidf'].get_params()),
            'logistic_regression': sanitize_params(pipeline.named_steps['clf'].get_params()),
            'decision_threshold': DECISION_THRESHOLD
        }
    }

    with open(report_file_path, 'w') as f:
        json.dump(results_summary, f, indent=4)
        
    print(f"  - Rapport de performance sauvegardé dans {report_file_path}")
    print("\n--- Expérience terminée avec succès ! ---")
