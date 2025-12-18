# Désambiguïsation d'acronymes ferroviaires - Défi TextMine (EGC 2026)

Ce dépôt contient l'implémentation de la méthode **TAG (Terminology Augmented Generation)** développée par l'équipe **Mokipo_** pour le défi [TextMine - EGC 2026](https://www.kaggle.com/competitions/defi-text-mine-egc-2026/overview) organisé par la SNCF.

Cette approche a permis d'obtenir la **2ème place** au classement final avec un **F1-score de 88,14%**.

## 📌 Présentation du projet

La tâche consiste à identifier la forme étendue correcte d'un acronyme au sein d'un texte réglementaire ferroviaire parmi une liste de candidats potentiels. 

Le défi majeur de cette édition résidait dans l'asymétrie des données et la nécessité d'un raisonnement contextuel fin. Notre approche privilégie l'utilisation d'un Grand Modèle de Langage (LLM) augmenté par un lexique métier via une stratégie de prompting en trois étapes :
1. **Analyse contextuelle** du texte source.
2. **Injection de connaissances** via le lexique SNCF.
3. **Application d'heuristiques de décision** (priorité à la définition la plus descriptive).

## 🚀 Contenu du dépôt

Conformément aux engagements de l'article publié, ce dépôt met à disposition :
* `TextMine2026.pdf` : L'article (v2) déposé pour la compétition.
* `LLM_inference.py` : Le script principal utilisant l'API Gemini (mode Batch) pour l'inférence.
* `prompts.py` : Le catalogue d'une sélection des stratégies de prompting testées (dont la stratégie H, la plus performante).
* `data/lexique-des-acronymes-sncf.json` : Le lexique de référence utilisé pour l'augmentation des données.
* `baseline-tfidf.py` : Script de référence pour la baseline statistique.

## 🛠️ Installation & utilisation

### Prérequis
* Python 3.9+
* Une clé API Google Gemini

### Installation
```bash
git clone [https://github.com/Emvista/TextMine-EGC-2026.git](https://github.com/Emvista/TextMine-EGC-2026.git)
cd TextMine-EGC-2026
pip install -r requirements.txt
```

## 📖 Citation

Si vous utilisez ces travaux dans vos recherches, merci de citer l'article suivant :

> **Lucas Aubertin (2025).** *D'une asymétrie de corpus à une heuristique ciblée : une méthodologie LLM pour le défi TextMine - EGC 2026.* Actes de la conférence EGC 2026.

ou la version bibtex

```bibtex
@inproceedings{aubertin2026textmine,
  title={D'une asymétrie de corpus à une heuristique ciblée : une méthodologie LLM pour le défi TextMine - EGC 2026},
  author={Aubertin, Lucas},
  booktitle={Actes de la conférence EGC},
  year={2026},
  organization={Emvista}
}
```



