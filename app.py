import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


@st.cache_data
def load_catalogue():
    df = pd.read_excel("catalogue.xlsx", sheet_name="catalogue référence")
    return df["nom_section"].tolist()


def draw_beam(longueur, section, maintiens, charge_type, charge_val, xs=None, xf=None, x_app=None):
    fig, ax = plt.subplots(figsize=(12, 5))

    # Espace d'affichage fixe : toujours équivalent au rendu d'une poutre de 6 m
    D = 6.0
    scale = D / longueur  # normalise les coordonnées réelles → display

    def d(x):
        return x * scale

    beam_y = 2.0
    beam_h = 0.4
    beam_color = "#5B9BD5"
    beam_edge = "#2E75B6"
    tri_h = 0.55
    tri_w = 0.21  # taille fixe des triangles (calée sur le rendu 6 m)
    margin = 0.5  # marges fixes

    # Corps de la poutre
    ax.add_patch(mpatches.FancyBboxPatch(
        (0, beam_y), D, beam_h,
        boxstyle="square,pad=0",
        facecolor=beam_color, edgecolor=beam_edge, linewidth=1.5, zorder=3
    ))

    # Appuis triangulaires aux extrémités
    for x_sup_d in [0, D]:
        triangle = plt.Polygon(
            [[x_sup_d, beam_y],
             [x_sup_d - tri_w, beam_y - tri_h],
             [x_sup_d + tri_w, beam_y - tri_h]],
            closed=True, facecolor=beam_color, edgecolor=beam_edge, linewidth=1.5, zorder=2
        )
        ax.add_patch(triangle)
        ax.plot([x_sup_d - tri_w * 1.3, x_sup_d + tri_w * 1.3],
                [beam_y - tri_h, beam_y - tri_h],
                color=beam_edge, linewidth=1.5, zorder=2)
        hatch_x = np.linspace(x_sup_d - tri_w * 1.3, x_sup_d + tri_w * 1.3, 7)
        for hx in hatch_x:
            ax.plot([hx, hx - 0.08], [beam_y - tri_h, beam_y - tri_h - 0.12],
                    color=beam_edge, linewidth=0.8, zorder=2)

    # Points de maintien (coordonnées normalisées, labels en mètres réels)
    for i, x_m in enumerate(maintiens):
        xd = d(x_m)
        ax.plot(xd, beam_y + beam_h / 2, marker="^", markersize=10,
                color="#27AE60", markeredgecolor="#1A7A45", linewidth=0, zorder=4)
        ax.text(xd, beam_y + beam_h + 0.12, f"x{i+1}={x_m:.2f}m",
                ha="center", va="bottom", fontsize=7.5, color="#27AE60")

    # Charges
    if charge_type == "Uniforme" and xs is not None and xf is not None and xf > xs:
        xs_d, xf_d = d(xs), d(xf)
        n_arrows = max(4, int((xf_d - xs_d) / 0.3))
        x_arrows = np.linspace(xs_d, xf_d, n_arrows)
        arrow_len = 0.55
        bar_y = beam_y + beam_h + arrow_len

        ax.hlines(bar_y, xs_d, xf_d, colors="#E74C3C", linewidth=2.0, zorder=5)
        for xa in x_arrows:
            ax.annotate("", xy=(xa, beam_y + beam_h),
                        xytext=(xa, bar_y),
                        arrowprops=dict(arrowstyle="-|>", color="#E74C3C",
                                        lw=1.5, mutation_scale=10))
        ax.text((xs_d + xf_d) / 2, bar_y + 0.12,
                f"q = {charge_val:.0f} daN/ml",
                ha="center", va="bottom", fontsize=9, color="#E74C3C",
                fontweight="bold")

    elif charge_type == "Ponctuelle" and x_app is not None:
        xd = d(x_app)
        arrow_len = 0.7
        ax.annotate("", xy=(xd, beam_y + beam_h),
                    xytext=(xd, beam_y + beam_h + arrow_len),
                    arrowprops=dict(arrowstyle="-|>", color="#E74C3C",
                                   lw=2.0, mutation_scale=13))
        ax.text(xd, beam_y + beam_h + arrow_len + 0.08,
                f"P = {charge_val:.0f} daN",
                ha="center", va="bottom", fontsize=9, color="#E74C3C",
                fontweight="bold")

    # Cotation longueur (double flèche, label en mètres réels)
    cote_y = beam_y + beam_h + 1.15
    ax.annotate("", xy=(D, cote_y), xytext=(0, cote_y),
                arrowprops=dict(arrowstyle="<->", color="#555555", lw=1.2,
                                mutation_scale=10))
    ax.text(D / 2, cote_y + 0.08, f"L = {longueur:.2f} m",
            ha="center", va="bottom", fontsize=10, color="#333333")
    for xr in [0, D]:
        ax.plot([xr, xr], [beam_y + beam_h + 0.05, cote_y],
                color="#AAAAAA", linewidth=0.8, linestyle="--", zorder=1)

    # Nom de la section
    ax.text(0.01, 0.97, f"Section : {section}", transform=ax.transAxes,
            va="top", ha="left", fontsize=9.5, color="#2C3E50",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor="#CCCCCC", alpha=0.85))

    ax.set_xlim(-margin, D + margin)
    ax.set_ylim(beam_y - tri_h - 0.4, beam_y + beam_h + 1.7)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("#F8F9FA")
    plt.tight_layout()
    return fig


def main():
    st.set_page_config(
        page_title="Calcul Poutre Isostatique",
        page_icon="🏗️",
        layout="wide"
    )
    st.title("Calcul de poutre isostatique")

    col_form, col_visu = st.columns([1, 2], gap="large")

    with col_form:
        st.subheader("Paramètres")

        sections = load_catalogue()

        longueur = st.number_input(
            "Longueur (m)", min_value=0.1, max_value=100.0,
            value=6.0, step=0.5, format="%.2f"
        )
        section = st.selectbox("Section", sections)
        limite_elastique = st.number_input(
            "Limite élastique fy (MPa)", min_value=0.0,
            value=235.0, step=5.0, format="%.1f"
        )

        n_maintiens = int(st.number_input(
            "Nombre de maintiens", min_value=0, max_value=10,
            value=0, step=1
        ))
        maintiens = []
        if n_maintiens > 0:
            st.caption("Abscisses des points de maintien (m) :")
            cols_m = st.columns(min(n_maintiens, 3))
            for i in range(n_maintiens):
                with cols_m[i % 3]:
                    x_m = st.number_input(
                        f"x{i+1}", min_value=0.0, max_value=longueur,
                        value=round(longueur * (i + 1) / (n_maintiens + 1), 2),
                        step=0.1, format="%.2f",
                        key=f"maintien_{i}"
                    )
                    maintiens.append(x_m)

        st.divider()
        st.subheader("Charge")
        charge_type = st.selectbox("Type de charge", ["Uniforme", "Ponctuelle"])

        xs = xf = x_app = None
        if charge_type == "Uniforme":
            charge_val = st.number_input(
                "Valeur de la charge (daN/ml)", min_value=0.0,
                value=100.0, step=10.0
            )
            c1, c2 = st.columns(2)
            with c1:
                xs = st.number_input(
                    "Début xs (m)", min_value=0.0, max_value=longueur,
                    value=0.0, step=0.1, format="%.2f"
                )
            with c2:
                xf = st.number_input(
                    "Fin xf (m)", min_value=0.0, max_value=longueur,
                    value=longueur, step=0.1, format="%.2f"
                )
            if xf <= xs:
                st.warning("xf doit être supérieur à xs.")
        else:
            charge_val = st.number_input(
                "Valeur de la charge (daN)", min_value=0.0,
                value=500.0, step=50.0
            )
            x_app = st.number_input(
                "Abscisse d'application (m)", min_value=0.0,
                max_value=longueur, value=round(longueur / 2, 2),
                step=0.1, format="%.2f"
            )

        st.divider()
        st.subheader("Résultat")
        taux = st.session_state.get("taux_travail", None)
        if taux is not None:
            color = "normal" if taux <= 100 else "inverse"
            st.metric(
                label="Taux de travail",
                value=f"{taux:.1f} %",
                delta=f"{taux - 100:.1f} % {'(dépassement)' if taux > 100 else '(marge)'}",
                delta_color=color
            )
        else:
            st.info("Taux de travail : en attente du calcul backend.")

    with col_visu:
        st.subheader("Schéma de la poutre")
        fig = draw_beam(
            longueur, section, maintiens,
            charge_type, charge_val, xs, xf, x_app
        )
        st.pyplot(fig, width="stretch")

        with st.expander("Récapitulatif des paramètres"):
            data = {
                "Paramètre": ["Longueur", "Section", "Limite élastique fy", "Nb maintiens", "Type de charge", "Valeur charge"],
                "Valeur": [
                    f"{longueur:.2f} m",
                    section,
                    f"{limite_elastique:.1f} MPa",
                    str(n_maintiens),
                    charge_type,
                    f"{charge_val:.0f} {'daN/ml' if charge_type == 'Uniforme' else 'daN'}"
                ]
            }
            if charge_type == "Uniforme":
                data["Paramètre"] += ["xs", "xf"]
                data["Valeur"] += [f"{xs:.2f} m", f"{xf:.2f} m"]
            else:
                data["Paramètre"].append("x application")
                data["Valeur"].append(f"{x_app:.2f} m")
            if maintiens:
                for i, xm in enumerate(maintiens):
                    data["Paramètre"].append(f"Maintien {i+1}")
                    data["Valeur"].append(f"{xm:.2f} m")
            st.dataframe(pd.DataFrame(data), hide_index=True, width="stretch")


if __name__ == "__main__":
    main()
