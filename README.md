# calcul-poutre-iso

Outil de calcul d'une poutre horizontale isostatique (2 appuis simples aux extrémités). Saisie des paramètres via un formulaire web, visualisation du schéma en temps réel, calcul du taux de travail de la section métallique.

## Aperçu

- **Charge uniforme ou ponctuelle** sur une portée partielle ou totale
- **150 sections métalliques** (IPE, IPN, HEA…) issues d'un catalogue Excel
- **Taux de travail** calculé selon la contrainte normale maximale, comparé à la limite élastique fy
- **Schéma matplotlib** de la poutre mis à jour dynamiquement (appuis, charge, maintiens, cotation)

## Installation

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Lancement

```bash
source env/bin/activate
streamlit run app.py
```

L'application est accessible sur `http://localhost:8501`.

## Utilisation

1. Renseigner la **longueur** de la poutre, la **section** et la **limite élastique fy**
2. Ajouter éventuellement des **points de maintien** latéraux (abscisses en m)
3. Choisir le **type de charge** :
   - *Uniforme* : intensité `q` (daN/ml), entre `xs` et `xf`
   - *Ponctuelle* : intensité `P` (daN) en `x_app`
4. Cliquer sur **Calculer** — le taux de travail s'affiche en vert (marge) ou rouge (dépassement)

## Formules appliquées

**Charge uniforme** `q` (daN/ml) sur `[xs, xf]` — calcul exact par équilibre :

```
RA     = q × (xf − xs) × (2L − xs − xf) / (2L)
x*     = xs + RA / q
M_max  = RA × x* − q × (x* − xs)² / 2        [daN·m]
```

**Charge ponctuelle** `P` (daN) en `a` :

```
M_max = P × a × (L − a) / L                   [daN·m]
```

**Contrainte et taux de travail** :

```
σ    = M_max [daN·cm] / Wel.y [cm³]           [daN/cm²]
σ    = σ / 10                                  [MPa]
taux = σ / fy × 100                            [%]
```

## Structure

```
calcul-poutre-iso/
├── app.py           # Frontend Streamlit
├── backend.py       # Calcul des sollicitations et du taux de travail
├── catalogue.xlsx   # Catalogue de sections (feuille "catalogue référence")
└── requirements.txt
```

## Dépendances

```
pandas
openpyxl
streamlit
matplotlib
```
