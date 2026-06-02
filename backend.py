import numpy as np
import pandas as pd


def charger_wel_y(nom_section: str) -> float:
    df = pd.read_excel("catalogue.xlsx", sheet_name="catalogue référence")
    ligne = df[df["nom_section"] == nom_section]
    if ligne.empty:
        raise ValueError(f"Section introuvable dans le catalogue : {nom_section!r}")
    return float(ligne.iloc[0]["Wel.y mm3 x103"])  # cm³


def moment_max_uniforme(q: float, xs: float, xf: float, L: float) -> float:
    """Moment fléchissant max (daN·m) pour une charge q (daN/ml) sur [xs, xf]."""
    if xf <= xs:
        raise ValueError("xf doit être strictement supérieur à xs")
    RA = q * (xf - xs) * (2 * L - xs - xf) / (2 * L)
    x_star = xs + RA / q  # abscisse où le cisaillement s'annule
    x_star = max(xs, min(x_star, xf))  # clamp dans la zone chargée
    return RA * x_star - q * (x_star - xs) ** 2 / 2


def moment_max_ponctuel(P: float, a: float, L: float) -> float:
    """Moment fléchissant max (daN·m) pour une charge P (daN) en x=a."""
    return P * a * (L - a) / L


def compute_diagrams_uniforme(
    q: float, xs: float, xf: float, L: float, n: int = 300
) -> tuple:
    RA = q * (xf - xs) * (2 * L - xs - xf) / (2 * L)
    x = np.linspace(0, L, n)
    V = np.where(x < xs, RA,
        np.where(x <= xf, RA - q * (x - xs),
                 RA - q * (xf - xs)))
    M = np.where(x < xs, RA * x,
        np.where(x <= xf, RA * x - q * (x - xs) ** 2 / 2,
                 RA * x - q * (xf - xs) * (x - (xs + xf) / 2)))
    return x, V, M


def compute_diagrams_ponctuel(
    P: float, a: float, L: float, n: int = 300
) -> tuple:
    RA = P * (L - a) / L
    x = np.linspace(0, L, n)
    V = np.where(x < a, RA, RA - P)
    M = np.where(x < a, RA * x, RA * x - P * (x - a))
    return x, V, M


def calculer_taux_travail(
    longueur: float,
    section: str,
    limite_elastique: float,
    charge_type: str,
    charge_val: float,
    xs: float | None,
    xf: float | None,
    x_app: float | None,
) -> float:
    """Retourne le taux de travail (%) de la section sous la charge donnée."""
    wel_y = charger_wel_y(section)  # cm³

    if charge_type == "Uniforme":
        if xs is None or xf is None:
            raise ValueError("xs et xf sont requis pour une charge uniforme")
        M_max = moment_max_uniforme(charge_val, xs, xf, longueur)  # daN·m
    else:
        if x_app is None:
            raise ValueError("x_app est requis pour une charge ponctuelle")
        M_max = moment_max_ponctuel(charge_val, x_app, longueur)  # daN·m

    M_max_cm = M_max * 100          # daN·m → daN·cm
    sigma = M_max_cm / wel_y        # daN/cm²
    sigma_mpa = sigma / 10          # MPa  (1 MPa = 10 daN/cm²)
    return sigma_mpa / limite_elastique * 100
