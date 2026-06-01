# calcul-poutre-iso — contexte projet

## Objectif

Outil de calcul d'une **poutre horizontale isostatique à 1D** (2 appuis aux extrémités, profondeur y négligée).  
Le projet est découpé en deux couches : un **frontend Streamlit** (fait) et un **backend de calcul** (à faire).

---

## Lancer l'application

```bash
source env/bin/activate
streamlit run app.py
```

L'app est accessible sur `http://localhost:8501`.

---

## Structure du projet

```
calcul-poutre-iso/
├── app.py               # Frontend Streamlit (formulaire + schéma matplotlib)
├── catalogue.xlsx       # Catalogue de sections métalliques
├── requirements.txt     # pandas, openpyxl, streamlit, matplotlib
├── env/                 # Environnement virtuel Python 3.12
└── exemple_image_poutre.jpg  # Référence visuelle originale de la poutre
```

---

## Frontend — `app.py`

### Champs du formulaire (colonne gauche)

| Champ | Type | Détail |
|---|---|---|
| Longueur | `float` (m) | min=0.1, max=100, défaut=6.0 |
| Section | `str` (dropdown) | Lu depuis `catalogue.xlsx`, feuille `"catalogue référence"`, colonne `nom_section` (150 sections : IPE, IPN, HEA…) |
| Limite élastique fy | `float` (MPa) | défaut=235.0 (acier S235) |
| Nombre de maintiens | `int` (0–10) | Génère N champs d'abscisses xi dynamiquement |
| Type de charge | dropdown | `"Uniforme"` ou `"Ponctuelle"` |
| → Uniforme | `float` (daN/ml) + xs + xf | Charge répartie entre xs et xf |
| → Ponctuelle | `float` (daN) + x_app | Charge concentrée en x_app |

### Zone taux de travail

Affichée en bas de la colonne formulaire via `st.metric`. Elle lit `st.session_state["taux_travail"]` (float, %).  
- Si la clé est absente → `st.info("En attente du calcul backend.")`
- Si présente → indicateur vert (≤ 100 %) ou rouge (> 100 %) avec delta affiché

**C'est le point d'entrée du backend** : le backend doit écrire dans `st.session_state["taux_travail"]` avant le re-render.

### Visualisation matplotlib (colonne droite)

Fonction `draw_beam(longueur, section, maintiens, charge_type, charge_val, xs, xf, x_app)`.

**Principe clé — fenêtre fixe :**  
Quelle que soit la longueur réelle, le dessin occupe toujours un espace d'affichage fixe `D = 6.0` unités (calé sur le rendu validé pour L=6 m). Toutes les coordonnées réelles sont normalisées par `scale = D / longueur`. Les labels affichent toujours les valeurs métriques réelles.

```python
D = 6.0                  # espace d'affichage fixe
scale = D / longueur     # facteur de normalisation
def d(x): return x * scale  # convertit mètres réels → unités display
```

**Éléments dessinés :**
- Poutre : rectangle bleu `#5B9BD5` de `(0, beam_y)` à `(D, beam_y + beam_h)`
- Appuis : triangles bleus aux extrémités (x=0 et x=D) + hachures de sol
- Maintiens : marqueurs `^` verts aux abscisses normalisées, labels en mètres réels
- Charge uniforme : barre rouge + flèches vers le bas entre `d(xs)` et `d(xf)`, label `q = XX daN/ml`
- Charge ponctuelle : flèche rouge vers le bas en `d(x_app)`, label `P = XX daN`
- Cotation L : double flèche grise au-dessus, label `L = XX m` en mètres réels
- Section : badge texte en haut à gauche (coordonnées axes, invariant au zoom)

Axes fixes : `xlim = [-0.5, 6.5]`, `ylim = [1.05, 4.1]` environ, `aspect="equal"`, `axis("off")`.

---

## Catalogue — `catalogue.xlsx`

- Feuille : `"catalogue référence"`
- 150 lignes × 28 colonnes
- Colonne clé pour le dropdown : `nom_section` (ex : `IPE 80`, `HEA 200`…)
- Autres colonnes utiles pour le backend : `h`, `b`, `tw`, `tf`, `A`, `Iy`, `Iz`, `Wel.y`, `Wel.z`, `G`, `It`, `Iw`

```python
df = pd.read_excel("catalogue.xlsx", sheet_name="catalogue référence")
```

---

## Ce qui reste à faire — Backend

Le backend doit :
1. Récupérer les paramètres depuis `st.session_state` (ou via un bouton "Calculer")
2. Retrouver les propriétés de la section choisie dans `catalogue.xlsx` (filtrer sur `nom_section`)
3. Calculer les sollicitations (moment fléchissant max, effort tranchant) selon le type de charge
4. Calculer la contrainte normale max : `σ = M_max / Wel.y`
5. Calculer le taux de travail : `taux = σ / fy × 100` (avec `fy = limite_elastique` en MPa)
6. Écrire le résultat dans `st.session_state["taux_travail"]`

### Formules de base (poutre isostatique, appuis simples en 0 et L)

**Charge uniforme** `q` (daN/ml) sur `[xs, xf]` :
```
M_max ≈ q * (xf - xs)² / 8   (si xs=0 et xf=L, sinon calcul exact par intégration)
```

**Charge ponctuelle** `P` (daN) en `a = x_app` :
```
M_max = P * a * (L - a) / L   (moment en x = a)
```

Les unités de `Wel.y` dans le catalogue sont en **cm³**. Convertir `M` en daN·cm avant le calcul de σ.

---

## Dépendances

```
pandas
openpyxl
streamlit
matplotlib
```

Installation : `pip install -r requirements.txt` (dans `env/`).
