import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Utiliser un style agréable pour matplotlib
plt.style.use("seaborn-v0_8-talk")


# Charger les données
df = pd.read_csv("donnees_utilisateurs.csv")
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

# Titre du dashboard
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Dashboard d'Utilisation de l'Application</h1>", unsafe_allow_html=True)

# Filtres
st.markdown("### Filtres")
col1, col2 = st.columns(2)
with col1:
    selected_annees = st.multiselect("Sélectionnez l'année", options=annees, default=annees)
with col2:
    selected_mois_noms = st.multiselect("Sélectionnez le(s) mois", options=mois_noms, default=mois_noms)

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

# Choix du niveau d'agrégation
st.markdown("### Niveau d'agrégation")
aggregation = st.radio("Choisissez le niveau d'agrégation", options=["Journalier", "Mensuel", "Annuel"], index=0)

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

# Calcul du pourcentage d'utilisateurs et de la valeur cible (30% des potentiels)
df_agg["PourcentageUtilisateurs"] = df_agg["Nombre d'utilisateurs"] / df_agg["Nombre total d'utilisateurs potentiels"]
df_agg["TargetActive"] = df_agg["Nombre total d'utilisateurs potentiels"] * 0.30

# Affichage des KPI (basé sur la dernière date disponible)
if not df_agg.empty:
    dernier = df_agg.sort_values("Date").iloc[-1]
    col1, col2, col3 = st.columns(3)
    col1.metric("Utilisateurs actifs", int(dernier["Nombre d'utilisateurs"]))
    col2.metric("Utilisateurs potentiels", int(dernier["Nombre total d'utilisateurs potentiels"]))
    col3.metric("Pourcentage d'utilisateurs", f"{dernier['PourcentageUtilisateurs']:.2%}")
else:
    st.error("Aucune donnée ne correspond aux filtres sélectionnés.")

# Choix du type de visualisation
st.markdown("### Visualisation")
visu_type = st.radio("Type de visualisation", options=["Graphique", "Histogramme"], index=0)

fig, ax = plt.subplots(figsize=(12, 6))
if visu_type == "Graphique":
    # Courbe des valeurs réelles et de la cible
    ax.plot(df_agg["Date"], df_agg["Nombre d'utilisateurs"], label="Utilisateurs actifs",
            marker="o", linewidth=2, color="#1f77b4")
    ax.plot(df_agg["Date"], df_agg["Nombre total d'utilisateurs potentiels"], label="Utilisateurs potentiels",
            linestyle="--", marker="x", linewidth=2, color="#ff7f0e")
    ax.plot(df_agg["Date"], df_agg["TargetActive"], label="Target (30%)", linestyle=":", linewidth=2, color="#2ca02c")
else:
    width = 15  # largeur des barres en jours
    ax.bar(df_agg["Date"], df_agg["Nombre d'utilisateurs"], width=width, label="Utilisateurs actifs",
           alpha=0.8, color="#1f77b4")
    ax.bar(df_agg["Date"], df_agg["Nombre total d'utilisateurs potentiels"], width=width, label="Utilisateurs potentiels",
           alpha=0.5, color="#ff7f0e")
    # Ajouter la courbe de la target sur le même graphique
    ax.plot(df_agg["Date"], df_agg["TargetActive"], label="Target (30%)", linestyle="--", linewidth=2, color="#2ca02c")

ax.set_title("Évolution des utilisateurs", fontsize=16, fontweight="bold", color="#333333")
ax.set_xlabel("Date", fontsize=14, color="#333333")
ax.set_ylabel("Nombre d'utilisateurs", fontsize=14, color="#333333")
ax.legend(fontsize=12)
plt.xticks(rotation=45, fontsize=10)
plt.yticks(fontsize=10)
st.pyplot(fig)
