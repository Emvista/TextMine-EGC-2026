MANUALLY_SELECTED_EXAMPLES = [
    {
        # Un cas où le contexte est très clair. ---
        "acronym": "AC",
        "text": "1.3. Résumé des modifications Suppression des BB75000 – 75100 – 75400 suite à la parution d’une AC nationale. Restrictions EURO4000-II.  RA-RT-5151B- Version 02 du 03-04-2017 Page 1",
        "options": {
            "Amélioration Continue": False,
            "Autorité de Certification": False,
            "Agent d'aCcompagnement ": False,
            "AURILLAC": False,
            "Attestation de Compatibilité du matériel roulant à l'infrastructure": True,
            "Accord Cadre": False, 
            "Agent du service Commercial ": False, 
            "Agent Circulation ": False, 
            "Action Corrective": False, 
            "ACcès": False

        },
        "raisonnement": "Le contexte mentionne la parution d'une 'AC' qui indique des modifications à ce qui semble être des types de trains. Seule la proposition 'Attestation de Compatibilité du matériel roulant à l'infrastructure' indique un document susceptible de contenir des modifications, dont des suppressions."
    },
    {
        # --- Un cas plus subtil qui demande une connaissance du domaine. ---
        "acronym": "BV",
        "text": " Ligne 395000 : Dreux BV (km 81,181) à la limite de région (km 132,000) compatibilité : NON (quais non compatibles à Verneuil-sur-Avre voie 1 km 117,204 et à Bourth voie 2 km 126,742) / restrictions : néant. ",
        "options": {
            "Bureau de Vente": False,
            "Bassin Versant": False,
            "Bâtiment des Voyageurs : en langage courant, ce sont les gares.": True
        },
        "raisonnement" : "L'acronyme 'BV' désigne un type de bâtiment dédié aux voyageurs. Dans le langage courant, ce type de bâtiment s'appelle en effet 'gare'. Il faut ici une connaissance du domaine pour comprendre que 'BV' désigne en réalité le même concept que celui du langage courant mais de façon spécifique au métier et plus précise. On peut inférer que c'est un bâtiment car il se situe sur une ligne (de train), dans une ville peuplée (Dreux) et qu'il est question de la compatibilité des quais (de gare)."
    },
    {
        # --- Un cas où plusieurs options semblent plausibles. ---
        "acronym": "PL",
        "text": "HLP haut le pied LRA  limite de résistance des attelages PL pleine ligne PN passage à niveau RFN réseau ferré national ",
        "options": {
            "Poids Lourd": False,
            "Pleine Ligne": True,
            "Panneaux Lumineux": False,
            "Poste de Ligne": False,
            "Plateforme Logistique": False
        },
        "raisonnement": "Le texte est une liste d'acronymes ferroviaires avec leurs définitions. Bien que 'PL' puisse signifier 'Poids Lourd' ou 'Plateforme Logistique' dans un contexte de transport plus large et que 'Poste de Ligne' soit un terme technique plausible, le contexte immédiat donne la définition exacte : 'PL pleine ligne'. Il faut donc privilégier la définition fournie localement dans la phrase."
    },
    {
        # --- Exemple 4 (Négatif, Cas -1) ---
        "acronym": "SE",
        "text": "500 ;  UM 500  - 1500 V : US néant,  UM Autorisée (uniquement avec TGV 33000 et 923000) si l’espacement entre deux UM de TGV SE par sens de circulation est supérieur à : - 15 min entre les deux premières circulations ",
        "options": {
            "Soudure Electrique": False, 
            "Signalisation Électrique": False, 
            "Sous-ensemble": False, 
            "Secteur Elementaire": False, 
            "Service Electrique.  SEG : Service Electrique Général (HT/BT).  SES : Service Electrique Signalisation.   SET : Service Electrique Téléphonie.": False, 
            "SAINT ETIENNE CHATEAUCREUX": False
        },
        "raisonnement": "L'acronyme 'SE' est apposé à 'TGV' (formant 'TGV SE'), suggérant un type de TGV. Aucune des options proposées ne correspond à un type de TGV (comme 'Sud-Est'). Par conséquent, aucune option n'est correcte."
    }
]

# Expérience 6

PROMPT_TEMPLATE_EXP_6 = """
Tu es un expert en désambiguïsation d'acronymes dans des documents techniques ferroviaires. Ta mission est de choisir la bonne définition d'un acronyme parmi une liste, en te basant sur deux sources : le contexte du texte et un lexique de référence.

Ta méthode est la suivante :
1.  **Contexte 1 (Texte) :** Analyse le texte où l'acronyme apparaît.
2.  **Contexte 2 (Lexique) :** Consulte les définitions fournies ci-dessous, issues d'un lexique SNCF. Elles sont une aide pour confirmer ton choix ou résoudre un doute. Le contexte du texte prime si le lexique est ambigu ou contradictoire.
3.  **Réflexion :** Analyse brièvement comment le texte et le lexique t'aident à faire un choix. Explique en une phrase pourquoi une option est la plus pertinente.
4.  **Sortie :** Fournis ta réponse finale sous la forme d'un objet JSON valide contenant uniquement la clé "index_correct". La valeur est l'index (un entier) de l'option choisie.

S'il n'y a pas de bonne réponse ou si tu es incertain, indique-le dans ta réflexion et réponds avec l'index -1.

{few_shot_examples}
---
**EXEMPLE À TRAITER**

**Contexte 1 (Texte) :**
```json
{example_json}
```
Contexte 2 (Lexique SNCF pour l'acronyme "{acronym}") : {lexicon_context}
Sortie attendue : **
"""

# Expérience 7

PROMPT_TEMPLATE_EXP_7 = """
    Tu es un expert en désambiguïsation d'acronymes dans des documents techniques ferroviaires. Ta mission est de choisir la bonne définition d'un acronyme parmi une liste, en te basant sur deux sources : le contexte du texte et un lexique de référence.

    Ta méthode est la suivante :
    1.  **Contexte 1 (Texte) :** Analyse le texte où l'acronyme apparaît.
    2.  **Contexte 2 (Lexique) :** Consulte les définitions fournies ci-dessous, issues d'un lexique SNCF. Elles sont une aide pour confirmer ton choix ou résoudre un doute. Le contexte du texte prime si le lexique est ambigu ou contradictoire.
    3.  **Réflexion :** Analyse brièvement comment le texte et le lexique t'aident à faire un choix.
    4.  **Sortie :** Fournis ta réponse finale sous la forme d'un objet JSON valide contenant uniquement la clé "index_correct". La valeur est l'index (un entier) de l'option choisie.

    S'il n'y a pas de bonne réponse, réponds avec l'index -1.

    ---
    **EXEMPLE À TRAITER**

    **Contexte 1 (Texte) :**
    ```json
    {example_json}
    ````
    ## **Contexte 2 (Lexique SNCF pour l'acronyme "{acronym}") :** {lexicon_context}

    **Sortie attendue :**
    """


# Expérience 9

PROMPT_TEMPLATE_EXP_9 = """
    Tu es un expert en désambiguïsation d'acronymes dans des documents techniques ferroviaires. Ta mission est de choisir la bonne définition d'un acronyme parmi une liste, en te basant sur deux sources : le contexte du texte et un lexique de référence.

    Ta méthode est la suivante :
    1.  **Contexte 1 (Texte) :** Analyse le texte où l'acronyme apparaît.
    2.  **Contexte 2 (Lexique) :** Consulte les définitions fournies ci-dessous, issues d'un lexique SNCF. Elles sont une aide pour confirmer ton choix ou résoudre un doute. Le contexte du texte prime si le lexique est ambigu ou contradictoire.
    3.  **RÈGLE IMPORTANTE :** Si plusieurs options te semblent correctes et décrivent la même entité (par exemple, une version courte "Réseau Ferré" et une version longue "Réseau Ferré. Description..."), **tu dois TOUJOURS privilégier l'option la plus longue et la plus descriptive.**
    4.  **Réflexion :** Analyse brièvement ton choix en mentionnant la Règle 3 si tu l'as appliquée.
    5.  **Sortie :** Fournis ta réponse finale sous la forme d'un objet JSON valide contenant uniquement la clé "index_correct". La valeur est l'index (un entier) de l'option choisie.

    S'il n'y a pas de bonne réponse, réponds avec l'index -1.

    ---
    **EXEMPLE À TRAITER**

    **Contexte 1 (Texte) :**
    ```json
    {example_json}
    ````
    ## **Contexte 2 (Lexique SNCF pour l'acronyme "{acronym}") :** {lexicon_context}

    **Sortie attendue :**
    """

# Expérience 10

PROMPT_TEMPLATE_EXP_10 = """
    Tu es un expert en désambiguïsation d'acronymes dans des documents techniques ferroviaires. Ta mission est de choisir la bonne définition d'un acronyme en suivant une méthode de raisonnement rigoureuse.

    Ta méthode est la suivante :

    **Étape 1 : Analyse Initiale.**
    -   Analyse le **Contexte 1 (Texte)** pour comprendre l'usage de l'acronyme.
    -   Consulte le **Contexte 2 (Lexique)** pour voir les définitions officielles.
    -   Identifie une ou deux options candidates qui semblent les plus pertinentes basées sur cette première analyse.

    **Étape 2 : Application des Règles et Vérification.**
    -   **Règle Principale :** Le contexte du texte prime TOUJOURS. Si le texte définit explicitement l'acronyme, ce choix est prioritaire.
    -   **Règle d'Arbitrage (TRÈS IMPORTANTE) :** Si, après l'analyse, plusieurs options semblent correctes ou décrivent la même entité (par ex. une version courte "Réseau Ferré" et une longue "Réseau Ferré. Description..."), **tu dois TOUJOURS privilégier l'option la plus longue et la plus descriptive.**
    -   **Vérification finale :** L'option choisie est-elle parfaitement cohérente avec le Contexte 1 ?

    **Étape 3 : Sortie.**
    1.  **Réflexion :** Décris brièvement ton raisonnement en suivant les étapes 1 et 2. Mentionne explicitement si tu as appliqué la Règle d'Arbitrage.
    2.  **Sortie JSON :** Fournis ta réponse finale sous la forme d'un objet JSON valide contenant uniquement la clé "index_correct".

    S'il n'y a pas de bonne réponse, réponds avec l'index -1.

    ---
    **EXEMPLE À TRAITER**

    **Contexte 1 (Texte) :**
    ```json
    {example_json}
    ````
    ## **Contexte 2 (Lexique SNCF pour l'acronyme "{acronym}") :** {lexicon_context}

    **Sortie attendue :**
    """























# ==============================================================================
# STRATÉGIE FINALE (EXPÉRIENCE H) - Celle utilisée pour la 3ème place
# ==============================================================================
# Cette stratégie combine l'analyse contextuelle, l'injection de lexique (RAG)
# et une heuristique de sélection de la définition la plus longue en cas de doute.
TAG_STRATEGY_BEST = """
Tu es un expert en désambiguïsation d'acronymes dans des documents techniques ferroviaires. Ta mission est de choisir la bonne définition d'un acronyme en suivant une méthode de raisonnement rigoureuse.

Ta méthode est la suivante :

**Étape 1 : Analyse Initiale.**
-   Analyse le **Contexte 1 (Texte)** pour comprendre l'usage de l'acronyme.
-   Consulte le **Contexte 2 (Lexique)** pour voir les définitions officielles.
-   Identifie une ou deux options candidates qui semblent les plus pertinentes basées sur cette première analyse.

**Étape 2 : Application des Règles et Vérification.**
-   **Règle Principale :** Le contexte du texte prime TOUJOURS. Si le texte définit explicitement l'acronyme, ce choix est prioritaire.
-   **Règle d'Arbitrage (TRÈS IMPORTANTE) :** Si, après l'analyse, plusieurs options semblent correctes ou décrivent la même entité (par ex. une version courte "Réseau Ferré" et une longue "Réseau Ferré. Description..."), **tu dois TOUJOURS privilégier l'option la plus longue et la plus descriptive.**
-   **Vérification finale :** L'option choisie est-elle parfaitement cohérente avec le Contexte 1 ?

**Étape 3 : Sortie.**
1.  **Réflexion :** Décris brièvement ton raisonnement en suivant les étapes 1 et 2. Mentionne explicitement si tu as appliqué la Règle d'Arbitrage.
2.  **Sortie JSON :** Fournis ta réponse finale sous la forme d'un objet JSON valide contenant uniquement la clé "index_correct".

S'il n'y a pas de bonne réponse, réponds avec l'index -1.

---
**EXEMPLE À TRAITER**

**Contexte 1 (Texte) :**
```json
{example_json}

```

## **Contexte 2 (Lexique SNCF pour l'acronyme "{acronym}") :** {lexicon_context}

**Sortie attendue :**
"""

# ==============================================================================

# AUTRES STRATÉGIES EXPLORÉES

# ==============================================================================

# Stratégie "Arbitre Expert" (Expérience I)

TAG_STRATEGY_ARBITRE = """
Tu es un arbitre expert en désambiguïsation d'acronymes...
[... Le reste de votre prompt I ...]
"""

# Stratégie "La plus longue" simple (Expérience E)

TAG_STRATEGY_LONGUE = """
[... Votre prompt E ...]
"""


