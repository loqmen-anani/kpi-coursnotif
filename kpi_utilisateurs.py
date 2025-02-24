import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


def generate_app_usage_data(start_date, num_days, target_users, final_usage_percentage):
    # Paramètres de la croissance exponentielle
    growth_rate = 0.1  # Taux de croissance initial
    # Définir le jour de stabilisation : avant ce jour, la croissance suit une loi exponentielle avec du bruit,
    # et au jour de stabilisation, on force l'atteinte du maximum.
    stabilization_day = int(num_days // 2)  # par exemple, la moitié de la période simulée
    # Calcul du nombre maximal d'utilisateurs actifs
    max_active_users = int(target_users * final_usage_percentage)

    # Initialisation des listes pour stocker les données
    dates = []
    users = []
    total_potential_users = []

    current_date = datetime.strptime(start_date, "%d/%m/%Y")
    for day in range(num_days):
        if day < stabilization_day:
            # Calcul de base de la croissance exponentielle
            baseline = max_active_users * (1 - np.exp(-growth_rate * day))
            # Ajout d'une variation aléatoire multiplicative (±5%)
            noise_factor = np.random.uniform(0.95, 1.05)
            daily_users = int(baseline * noise_factor)
            # S'assurer qu'on n'atteint pas le maximum avant stabilization_day
            daily_users = daily_users
        elif day == stabilization_day:
            daily_users = max_active_users
        else:
            daily_users = max_active_users

        # Variation pendant l'été (juillet et août)
        if current_date.month in [7, 8]:
            daily_users += np.random.randint(-100, 100)
            daily_users = max(daily_users, 0)

        # Fluctuation quotidienne mineure
        daily_users += np.random.randint(-5, 5)
        daily_users = max(daily_users, 0)

        # Génération du nombre total d'utilisateurs potentiels
        if current_date.month in [7, 8]:
            total_potential = target_users + np.random.randint(-100, 100)
        else:
            total_potential = target_users

        dates.append(current_date.strftime("%d/%m/%Y"))
        users.append(daily_users)
        total_potential_users.append(total_potential)

        current_date += timedelta(days=1)

    df = pd.DataFrame({
        "Date": dates,
        "Nombre d'utilisateurs": users,
        "Nombre total d'utilisateurs potentiels": total_potential_users
    })
    return df


# Paramètres
start_date = "01/06/2025"
num_days = 1000  # Période de simulation (par exemple, 300 jours)
target_users = 3410  # Nombre total d'utilisateurs potentiels cible
final_usage_percentage = 0.73  # Pourcentage final d'utilisateurs actifs

# Génération des données
df = generate_app_usage_data(start_date, num_days, target_users, final_usage_percentage)

df.to_csv("donnees_utilisateurs.csv", index=False)

# Affichage des premières lignes
print(df.head())

# Tracé des données
plt.figure(figsize=(14, 7))
plt.plot(df["Date"], df["Nombre d'utilisateurs"], label="Utilisateurs actifs")
plt.plot(df["Date"], df["Nombre total d'utilisateurs potentiels"], label="Utilisateurs potentiels", linestyle="--")
plt.title("Données d'utilisation de l'application")
plt.xlabel("Date")
plt.ylabel("Nombre d'utilisateurs")
plt.xticks(df["Date"][::30], rotation=45)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
