# calcul-poutre-iso — contexte projet

## Objectif

Outil de calcul d'une **poutre horizontale isostatique à 1D** (2 appuis aux extrémités, profondeur y négligée).  
Le projet est découpé en deux couches : un **frontend Streamlit** (fait) et un **backend de calcul** (fait).

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
├── backend.py           # Backend de calcul (moment, contrainte, taux de travail)
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

Un bouton **"Calculer"** (type="primary") précède cette zone. Sur clic, il appelle `calculer_taux_travail()` depuis `backend.py` et écrit le résultat dans `st.session_state["taux_travail"]`.

**Important** : `delta_color` doit toujours être `"inverse"` dans `st.metric` — car le delta vaut `taux - 100` (négatif quand il y a de la marge), et Streamlit colore en rouge les deltas négatifs avec `"normal"`.

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

## Backend — `backend.py`

### Fonctions

#### `charger_wel_y(nom_section) → float`
Lit `catalogue.xlsx`, filtre sur `nom_section`, retourne la colonne `"Wel.y mm3 x103"` en **cm³**.  
Lève `ValueError` si la section est introuvable.

#### `moment_max_uniforme(q, xs, xf, L) → float`
Formule exacte par équilibre (fonctionne sur portée partielle) :
```
RA     = q * (xf - xs) * (2*L - xs - xf) / (2*L)
x_star = xs + RA / q          # abscisse où V = 0
M_max  = RA * x_star - q * (x_star - xs)**2 / 2   # daN·m
```
Cas xs=0, xf=L → M_max = q×L²/8 (vérifié).

#### `moment_max_ponctuel(P, a, L) → float`
```
M_max = P * a * (L - a) / L   # daN·m
```

#### `calculer_taux_travail(...) → float`
Enchaîne les étapes de calcul et retourne le taux (%) :
1. `wel_y` (cm³) ← catalogue
2. `M_max` (daN·m) selon le type de charge
3. `M_max_cm = M_max * 100` (daN·m → daN·cm)
4. `sigma = M_max_cm / wel_y` (daN/cm²)
5. `sigma_mpa = sigma / 10` (1 MPa = 10 daN/cm²)
6. `taux = sigma_mpa / fy * 100` (%)

### Conversions d'unités clés
- `Wel.y` catalogue : valeurs directement en **cm³** (la colonne `"Wel.y mm3 x103"` indique ×10³ mm³ = cm³)
- Moment : travailler en **daN·cm** pour que `σ = M/W` soit en daN/cm²
- `1 MPa = 10 daN/cm²` → diviser par 10 pour convertir en MPa

---

## Diagrammes M(x) et V(x)

Affichés dans la colonne droite **après le premier clic sur "Calculer"**, sous le schéma de la poutre.

### Backend — nouvelles fonctions dans `backend.py`

#### `compute_diagrams_uniforme(q, xs, xf, L, n=300) → tuple[ndarray, ndarray, ndarray]`
Retourne `(x, V, M)` — tableaux numpy sur `n` points réguliers entre 0 et L.

```python
RA = q * (xf - xs) * (2*L - xs - xf) / (2*L)
V(x) = RA            si x < xs
       RA - q(x-xs)  si xs ≤ x ≤ xf
       RA - q(xf-xs) si x > xf
M(x) = RA·x                           si x < xs
       RA·x - q(x-xs)²/2              si xs ≤ x ≤ xf
       RA·x - q(xf-xs)·(x-(xs+xf)/2) si x > xf
```

#### `compute_diagrams_ponctuel(P, a, L, n=300) → tuple[ndarray, ndarray, ndarray]`
Retourne `(x, V, M)`.

```python
RA = P * (L - a) / L
V(x) = RA      si x < a
       RA - P  si x ≥ a
M(x) = RA·x          si x < a
       RA·x - P(x-a) si x ≥ a
```

### Frontend — `draw_diagrams(x, V, M)` dans `app.py`

Figure matplotlib avec 2 sous-graphes (`sharex=True`) :
- Haut : V(x) en rouge `#E74C3C` avec remplissage alpha 0.15
- Bas : M(x) en bleu `#5B9BD5` avec remplissage alpha 0.15

### Session state

Les tableaux sont calculés dans le handler du bouton "Calculer" et stockés dans `st.session_state["diagrammes"]` en même temps que `taux_travail`. Les diagrammes n'apparaissent pas avant le premier calcul.

---

## Dépendances

```
pandas
openpyxl
streamlit
matplotlib
numpy
```

Installation : `pip install -r requirements.txt` (dans `env/`).
