import io
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="KPI CoursNotif",  # Le nom de l'onglet
    page_icon="logo.png",  # Chemin vers ton logo
    layout="wide"  # Passage en mode large
)
plt.style.use("seaborn-v0_8-talk")

# Toggle pour sélectionner Réussite ou Échec
statut = st.radio("Sélectionnez le statut", options=["Réussite", "Échec"], index=0)
filename = "donnees_utilisateurs.csv" if statut == "Réussite" else "donnees_utilisateurs_echec.csv"

# Charger les données en fonction du statut
df = pd.read_csv(filename)
df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors='coerce')

# Mapping des mois en français
mois_dict = {
    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
    5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
    9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
}

# Extraction des années et des mois disponibles
annees = sorted(df["Date"].dt.year.unique())
mois_numeriques = sorted(df["Date"].dt.month.unique())
mois_noms = [mois_dict[m] for m in mois_numeriques]

# Création d'un layout à deux colonnes : gauche pour les contrôles, droite pour le plot
left_col, right_col = st.columns([0.4, 0.6])

with left_col:
    st.markdown("<h1 style='text-align: center; color: #982926;'>KPI de l'application CoursNotif</h1>",
                unsafe_allow_html=True)

    st.markdown("### Filtres")
    col1, col2 = st.columns(2)
    with col1:
        selected_annees = st.multiselect("Années", options=annees, default=annees)
    with col2:
        selected_mois_noms = st.multiselect("Mois", options=mois_noms, default=mois_noms)

    # Conversion des mois sélectionnés en chiffres
    selected_mois = []
    for nom in selected_mois_noms:
        for key, value in mois_dict.items():
            if value == nom:
                selected_mois.append(key)

    # Filtrer les données
    df_filtered = df[
        df["Date"].dt.year.isin(selected_annees) &
        df["Date"].dt.month.isin(selected_mois)
        ]

    st.markdown("### Niveau d'agrégation")
    aggregation = st.radio("", options=["Journalier", "Mensuel", "Annuel"], index=0)

    if aggregation == "Mensuel":
        df_filtered = df_filtered.copy()
        df_filtered["Année"] = df_filtered["Date"].dt.year
        df_filtered["Mois"] = df_filtered["Date"].dt.month
        df_agg = df_filtered.groupby(["Année", "Mois"]).agg({
            "Nombre d'utilisateurs": "max",
            "Nombre total d'utilisateurs potentiels": "max"
        }).reset_index()
        df_agg["Date"] = pd.to_datetime(df_agg["Année"].astype(str) + "-" + df_agg["Mois"].astype(str) + "-01")
    elif aggregation == "Annuel":
        df_filtered = df_filtered.copy()
        df_filtered["Année"] = df_filtered["Date"].dt.year
        df_agg = df_filtered.groupby("Année").agg({
            "Nombre d'utilisateurs": "max",
            "Nombre total d'utilisateurs potentiels": "max"
        }).reset_index()
        df_agg["Date"] = pd.to_datetime(df_agg["Année"].astype(str) + "-01-01")
    else:
        df_agg = df_filtered.copy()

    # Calcul des KPI
    df_agg["PourcentageUtilisateurs"] = df_agg["Nombre d'utilisateurs"] / df_agg[
        "Nombre total d'utilisateurs potentiels"]
    df_agg["TargetActive"] = df_agg["Nombre total d'utilisateurs potentiels"] * 0.30

    if not df_agg.empty:
        dernier = df_agg.sort_values("Date").iloc[-1]
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        col_kpi1.metric("Utilisateurs actifs", int(dernier["Nombre d'utilisateurs"]))
        col_kpi2.metric("Utilisateurs potentiels", int(dernier["Nombre total d'utilisateurs potentiels"]))
        if dernier["PourcentageUtilisateurs"] >= 0.30:
            col_kpi3.markdown(
                f"<h3 style='text-align: center; color: green;'>Pourcentage d'utilisateurs : {dernier['PourcentageUtilisateurs']:.2%} 😊</h3>",
                unsafe_allow_html=True
            )
        else:
            col_kpi3.markdown(
                f"<h3 style='text-align: center; color: red;'>Pourcentage d'utilisateurs : {dernier['PourcentageUtilisateurs']:.2%} 😞</h3>",
                unsafe_allow_html=True
            )
    else:
        st.error("Aucune donnée ne correspond aux filtres sélectionnés.")

    st.markdown("### Visualisation")
    visu_type = st.radio("Type de visualisation", options=["Graphique", "Histogramme"], index=0)

with right_col:
    # Création du plot
    fig, ax = plt.subplots(figsize=(10, 7))
    if visu_type == "Graphique":
        ax.plot(df_agg["Date"], df_agg["Nombre d'utilisateurs"], label="Utilisateurs actifs",
                linewidth=2, color="#1f77b4")
        ax.plot(df_agg["Date"], df_agg["Nombre total d'utilisateurs potentiels"], label="Utilisateurs potentiels",
                linestyle="--", marker="x", linewidth=2, color="#ff7f0e")
        ax.plot(df_agg["Date"], df_agg["TargetActive"], label="Target (30%)", linestyle=":", linewidth=2,
                color="#2ca02c")
    else:
        width = 15  # largeur des barres en jours
        ax.bar(df_agg["Date"], df_agg["Nombre d'utilisateurs"], width=width, label="Utilisateurs actifs",
               alpha=0.8, color="#1f77b4")
        ax.bar(df_agg["Date"], df_agg["Nombre total d'utilisateurs potentiels"], width=width,
               label="Utilisateurs potentiels",
               alpha=0.5, color="#ff7f0e")
        ax.plot(df_agg["Date"], df_agg["TargetActive"], label="Target (30%)", linestyle="--", linewidth=2,
                color="#2ca02c")

    ax.set_xlabel("Date", fontsize=14, color="#333333")
    ax.set_ylabel("Nombre d'utilisateurs", fontsize=14, color="#333333")
    ax.legend(fontsize=8)
    plt.xticks(rotation=45, fontsize=6)
    plt.yticks(fontsize=8)

    # Exporter la figure en SVG et l'afficher de manière vectorisée
    buf = io.StringIO()
    fig.savefig(buf, format="svg")
    svg = buf.getvalue()
    html_code = f"""
    <div style="width:100%; overflow-x:auto;">
        {svg}
    </div>
    """
    components.html(html_code, height=1200, width=1500, scrolling=True)
