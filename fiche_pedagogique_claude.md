# Fiche pédagogique — Collaborer avec une IA de code

**Formation :** Introduction au développement assisté par IA  
**Contexte :** Réalisation d'un frontend Streamlit pour le calcul de poutre isostatique  
**Outil utilisé :** Claude Code (Anthropic) — modèle Claude Sonnet 4.6  

---

## 1. Ce qu'est Claude Code

Claude Code est un assistant IA spécialisé dans le développement logiciel. Il ne se contente pas de générer du code : il **explore des fichiers**, **lit des données**, **lance des serveurs**, **prend des captures d'écran** et **vérifie visuellement** que le résultat correspond à l'intention.

Ce n'est pas un moteur de recherche, ni un simple chatbot. C'est un **agent** : il prend des décisions, choisit ses outils, et itère jusqu'à obtenir un résultat correct.

> 📝 **Notes de l'apprenant :**
> _Qu'est-ce qui vous a surpris dans cette définition ?_
>
> _______________________________________________
> _______________________________________________

---

## 2. Anatomie du premier prompt — la demande initiale

Le formateur a rédigé un prompt long et structuré. Voici pourquoi chaque partie était importante.

### Le prompt original (reconstitué)
```
Je suis developpeur python et je veux que tu produises du code exploitable par python.
Je veux que tu réalises le code d'un frontend.
L'objectif est de modéliser une poutre horizontale isostatique...

Il s'agit d'un formulaire qui contient les champs suivants :
    + Longueur en metre
    + Section : qui vient d'un catalogue existant (@catalogue.xlsx)...
    + nombre de maintiens...
    + type de la charge (liste déroulante : uniforme ou ponctuelle)
        Si uniforme → valeur (daN/ml), xs, xf
        Si ponctuelle → valeur (daN), x

Avant de commencer le developpement propose moi plusieurs solutions
que tu considère viable pour le frontend (streamlit / htmx, css ou autre)
```

### Décomposition pédagogique

| Élément du prompt | Rôle | Effet observé |
|---|---|---|
| *"Je suis développeur python"* | **Profil utilisateur** | L'IA a calibré ses propositions sur des technos Python-only |
| *"@catalogue.xlsx"* | **Référence à un fichier existant** | L'IA a lu le fichier, découvert la feuille `"catalogue référence"` et la colonne `nom_section` automatiquement |
| Structure avec `+` et indentation | **Hiérarchie des besoins** | L'IA a reproduit exactement cette structure dans le code (champs conditionnels) |
| *"Avant de commencer... propose moi"* | **Frein intentionnel** | L'IA n'a PAS codé immédiatement — elle a présenté 4 options pour laisser le choix |

### Leçon clé n°1 — Le frein intentionnel

> Sans la phrase *"Avant de commencer, propose moi plusieurs solutions"*, l'IA aurait **choisi elle-même** et codé directement. En ajoutant cette contrainte, le formateur a gardé **la décision architecturale** dans ses mains.

> 📝 **Notes de l'apprenant :**
> _Pourquoi est-il important de garder certaines décisions hors de l'IA ?_
>
> _______________________________________________
> _______________________________________________

---

## 3. La phase de proposition — choisir avant de construire

L'IA a proposé **4 technologies** avec pour chacune : un aperçu de code, des avantages et des inconvénients.

| Option proposée | Résumé |
|---|---|
| **Streamlit** ✅ | 100% Python, rapide, réactivité native |
| **Dash (Plotly)** | Python pur mais plus verbeux, meilleur pour graphiques interactifs |
| **Flask + HTMX** | Web classique, plus professionnel mais nécessite HTML/CSS |
| **Tkinter** | Desktop, aucun navigateur, peu partageable |

Le formateur a choisi **Streamlit**. Ce choix a orienté toute l'architecture suivante.

### Leçon clé n°2 — Valider avant d'implémenter

> L'IA a ensuite présenté un **plan détaillé** avant d'écrire la moindre ligne de code. Le formateur l'a approuvé. Ce n'est qu'après cette validation que le code a été produit.  
> Ce mécanisme s'appelle le **mode plan** (Plan Mode). Il protège contre les mauvaises interprétations coûteuses à corriger.

> 📝 **Notes de l'apprenant :**
> _Qu'aurait-il pu se passer si l'IA avait codé directement sans plan ?_
>
> _______________________________________________
> _______________________________________________

---

## 4. La vérification visuelle — l'IA teste ce qu'elle produit

Après avoir écrit `app.py`, l'IA ne s'est pas arrêtée. Elle a :

1. **Lancé le serveur** Streamlit sur le port 8501
2. **Ouvert un navigateur** (Playwright headless)
3. **Pris une capture d'écran**
4. **Regardé visuellement** le résultat
5. **Signalé** un avertissement de dépréciation dans les logs
6. **Corrigé** le code sans que le formateur n'ait à le demander

```
Streamlit : use_container_width sera supprimé après 2025-12-31.
→ Correction automatique : use_container_width=True  →  width="stretch"
```

### Leçon clé n°3 — L'IA ne se fie pas au code, elle teste le résultat

> Une IA de code performante ne dit pas *"le code semble correct"*. Elle **exécute**, **observe**, et **corrige**. C'est la différence entre un assistant passif et un agent actif.

> 📝 **Notes de l'apprenant :**
> _Dans votre domaine (génie civil), quelle serait l'équivalent de "tester visuellement" un calcul ?_
>
> _______________________________________________
> _______________________________________________

---

## 5. L'ajout d'un champ oublié — l'itération courte

Le formateur a réalisé après coup qu'il avait oublié un champ :

> *"j'avais oublié un champ que tu vas devoir rajouter, il s'agit de la limite elastique du matériau en MPa (il s'agit d'une valeur float)"*

**Ce que l'IA a fait :**
- Lu le fichier existant pour trouver le bon endroit (entre Section et Nombre de maintiens)
- Ajouté le champ dans le formulaire
- Ajouté la valeur dans le récapitulatif
- Relancé l'app et pris une capture de vérification

**Ce que l'IA n'a PAS fait :**
- Réécrire tout le fichier
- Poser des questions inutiles
- Inventer une valeur par défaut sans logique (235 MPa = acier S235, standard)

### Leçon clé n°4 — Les prompts courts sont puissants si le contexte est établi

> Une fois le projet construit et compris, une instruction d'une ligne suffit. L'IA connaît le projet, le style de code, et les conventions. Elle **contextualise automatiquement** la demande.

> 📝 **Notes de l'apprenant :**
> _Quelle différence y a-t-il entre donner du contexte au début et devoir le répéter à chaque message ?_
>
> _______________________________________________
> _______________________________________________

---

## 6. La correction d'un comportement visuel — décrire l'intention, pas le code

Le formateur a demandé :

> *"la taille de la fenêtre où tu affiche le dessin doit être fixe. La visualisation que tu proposes pour les poutres de 6 m est super garde la."*

Il n'a **pas dit comment faire**. Il a dit **ce qu'il voulait** (fenêtre fixe) et **ce qui lui plaisait** (le rendu à 6 m).

L'IA a compris qu'il fallait :
- Fixer les dimensions matplotlib (`figsize=(12, 5)`)
- Normaliser toutes les coordonnées réelles dans un espace d'affichage fixe `D = 6.0`
- Tester avec 3 longueurs différentes (2 m, 6 m, 15 m) pour prouver la stabilité

### Leçon clé n°5 — Décrire l'objectif, pas l'implémentation

> Vous n'avez pas besoin de savoir **comment** normaliser des coordonnées matplotlib. Vous devez savoir **ce que vous voulez** : une fenêtre qui ne bouge pas. L'IA traduit l'intention en technique.
>
> C'est exactement comme donner un cahier des charges à un ingénieur : vous décrivez le comportement attendu, il choisit la méthode.

> 📝 **Notes de l'apprenant :**
> _Citez un exemple dans votre pratique où vous donnez un objectif sans imposer la méthode._
>
> _______________________________________________
> _______________________________________________

---

## 7. La documentation pour le futur — `CLAUDE.md`

Le formateur a demandé :

> *"je veux que tu réalise un document pour le future toi en markdown indiquant tout le context necessaire pour toi afin que tu puisses reprendre le travail facilement."*

L'IA a produit `CLAUDE.md` — un fichier que **la prochaine session** lira automatiquement au démarrage. Il contient :
- Comment lancer l'app
- Les champs du formulaire et leurs types
- L'astuce de la fenêtre fixe (avec l'extrait de code clé)
- La structure du catalogue Excel
- Les formules pour le backend à venir

### Leçon clé n°6 — L'IA n'a pas de mémoire entre les sessions

> Contrairement à un collègue humain, l'IA repart de zéro à chaque nouvelle conversation. `CLAUDE.md` est l'équivalent d'un **compte-rendu de réunion** que vous laissez sur le bureau pour le lendemain. Sans lui, vous devriez tout réexpliquer.

> 📝 **Notes de l'apprenant :**
> _Que mettriez-vous dans un CLAUDE.md pour un projet de calcul de charpente métallique ?_
>
> _______________________________________________
> _______________________________________________
> _______________________________________________

---

## 8. Récapitulatif — les 6 règles d'interaction observées

| # | Règle | Exemple concret |
|---|---|---|
| 1 | **Donner son profil** | *"Je suis développeur python"* |
| 2 | **Référencer les fichiers existants** | `@catalogue.xlsx`, `@exemple_image_poutre.jpg` |
| 3 | **Freiner avant l'implémentation** | *"Avant de commencer, propose moi plusieurs solutions"* |
| 4 | **Valider le plan** | Approbation du plan détaillé avant que le code soit écrit |
| 5 | **Décrire l'objectif, pas le code** | *"la fenêtre doit être fixe, garde le rendu 6 m"* |
| 6 | **Documenter pour la continuité** | Demande de `CLAUDE.md` en fin de session |

---

## 9. Ce que l'IA a apporté vs ce que le formateur a apporté

| Formateur (vous, demain) | IA (Claude) |
|---|---|
| Connaissance du domaine (génie civil, poutres, daN, MPa) | Connaissance technique (Streamlit, matplotlib, Python) |
| Décision architecturale (Streamlit vs Dash) | Implémentation et débogage |
| Validation visuelle (*"c'est super, garde ça"*) | Normalisation des coordonnées, correction des warnings |
| Cahier des charges (champs, comportements) | Traduction en code fonctionnel |
| Mémoire du projet (CLAUDE.md) | Exécution précise et vérifiable |

> **Ce que cette session démontre :** L'IA est un amplificateur de compétences, pas un remplaçant. Plus vous connaissez votre domaine métier, plus vos prompts sont précis, et plus le résultat est pertinent.

---

## 10. Exercice pratique

À partir de ce que vous avez observé, rédigez le prompt que vous utiliseriez pour demander à l'IA d'implémenter le **backend de calcul** (moment fléchissant + taux de travail). Appliquez les règles 1 à 4.

> 📝 **Votre prompt :**
>
> _______________________________________________
> _______________________________________________
> _______________________________________________
> _______________________________________________
> _______________________________________________
> _______________________________________________
> _______________________________________________
