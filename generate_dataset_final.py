# ==============================================================================
# SCRIPT DE GÉNÉRATION D'UN DATASET DE POINTAGE FINAL (VERSION CORRIGÉE)
# ==============================================================================
import pandas as pd
import numpy as np
from datetime import date, timedelta, datetime
import random

# --- CONFIGURATION (Structure de l'entreprise) ---
NUM_EMPLOYEES = 100
START_DATE = date(2024, 1, 1)
END_DATE = date(2024, 12, 31)

# MODIFIÉ : Les noms de départements et directions sont maintenant "propres", sans préfixes.
# C'est la seule modification nécessaire dans ce fichier.
COMPANY_STRUCTURE = {
    "Tech": ["Cloud", "Data & IA", "Cybersécurité"],
    "Telecom": ["Réseaux Fixes", "Réseaux Mobiles", "Support Technique"],
    "Corporate": ["Marketing", "RH", "Finance"]
}

TEMPS_THEORIQUE_TIMEDELTA = timedelta(hours=8)
MOROCCAN_HOLIDAYS = [date(2024, 1, 1), date(2024, 1, 11), date(2024, 4, 10), date(2024, 5, 1), date(2024, 6, 17), date(2024, 7, 8), date(2024, 7, 30), date(2024, 8, 14), date(2024, 8, 20), date(2024, 9, 16), date(2024, 11, 6), date(2024, 11, 18)]

# --- Listes de Noms Marocains ---
MOROCCAN_LAST_NAMES = ["Alaoui", "Bennani", "Cherkaoui", "Tazi", "Fassi", "Kettani", "Saadi", "Guerraoui", "Berrada", "El Fassi", "Lahlou", "Benjelloun", "Kadiri", "Amrani", "Belkadi", "Slaoui", "Zniber", "Sekkat", "Benomar", "Tber", "Mikou", "Bencherif", "El Mokri", "Seffar", "Benkirane", "Fihri", "Alami", "Benmansour", "Belhaj", "Guessous", "Chraibi", "Tahiri", "Jabiri", "Ouazzani"]
MOROCCAN_MALE_FIRST_NAMES = ["Mohammed", "Ahmed", "Youssef", "Karim", "Rachid", "Hassan", "Said", "Ali", "Omar", "Driss", "Mehdi", "Amine", "Adam", "Sami", "Anas", "Hicham", "Yassine", "Khalid", "Hamza", "Adil", "Walid"]
MOROCCAN_FEMALE_FIRST_NAMES = ["Fatima", "Khadija", "Amina", "Aicha", "Zineb", "Leila", "Nadia", "Salma", "Meryem", "Sofia", "Kenza", "Rania", "Imane", "Hind", "Ghita", "Nawal", "Lamia", "Sara", "Majda", "Asmae", "Lina"]

def format_timedelta(td):
    if pd.isna(td) or td is None: return ""
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

# --- GÉNÉRATION DES EMPLOYÉS ---
employees = []
for i in range(NUM_EMPLOYEES):
    direction = random.choice(list(COMPANY_STRUCTURE.keys()))
    departement = random.choice(COMPANY_STRUCTURE[direction])
    
    profile = np.random.choice(['ponctuel', 'souvent_en_retard', 'teletravailleur'], p=[0.5, 0.3, 0.2])
    
    nom = random.choice(MOROCCAN_LAST_NAMES)
    prenom = random.choice(MOROCCAN_MALE_FIRST_NAMES) if random.random() < 0.5 else random.choice(MOROCCAN_FEMALE_FIRST_NAMES)
        
    employees.append({
        "matricule": f"M{1001+i}", "nom": nom, "prenom": prenom,
        "direction": direction, "departement": departement, "profile": profile
    })

# --- GÉNÉRATION DES ENREGISTREMENTS DE POINTAGE ---
all_records = []
days_range = (END_DATE - START_DATE).days + 1
long_leave_employee_matricule = np.random.choice([e['matricule'] for e in employees])
long_leave_start = date(2024, 7, 1)
long_leave_end = date(2024, 8, 23)

print("Génération des données en cours...")
for emp in employees:
    for day_num in range(days_range):
        current_date = START_DATE + timedelta(days=day_num)
        if current_date.weekday() >= 5 or current_date in MOROCCAN_HOLIDAYS:
            continue
        record = {
            "MATRICULE": emp['matricule'], "NOM": emp['nom'], "PRENOM": emp['prenom'],
            "Date": current_date.strftime("%d/%m/%Y"), 
            "Departement": emp['departement'], # Sera maintenant "Marketing", etc.
            "Direction": emp['direction'],     # Sera maintenant "Corporate", etc.
            "Entrée": "", "Sortie": "",
            "Temps de présence réel": "", "Temps de présence théorique": format_timedelta(TEMPS_THEORIQUE_TIMEDELTA),
            "Entrée tardive": "", "Sortie anticipée": "", "Absence Justifiée (par heure)": 0.0,
            "Absence non justifiée": 0.0, "Anomalie(badgeage impair)": "", "Jour TT Planifié": ""
        }
        # ... Le reste du script est inchangé et correct ...
        if emp['matricule'] == long_leave_employee_matricule and long_leave_start <= current_date <= long_leave_end:
            record["Absence Justifiée (par heure)"] = 8.0
            all_records.append(record)
            continue
        if emp['profile'] == 'teletravailleur' and np.random.rand() < 0.7:
            record["Jour TT Planifié"] = "Oui"
            all_records.append(record)
            continue
        prob_anomalie = 0.1
        if emp['profile'] == 'souvent_en_retard': prob_anomalie += 0.3
        if current_date.weekday() == 0: prob_anomalie += 0.1
        if np.random.rand() < prob_anomalie:
            anomaly_type = np.random.choice(['entree_tardive', 'sortie_anticipee', 'absence_non_justifiee', 'badgeage_impair', 'presence_insuffisante'], p=[0.3, 0.2, 0.1, 0.1, 0.3])
            if anomaly_type == 'absence_non_justifiee':
                record["Absence non justifiée"] = 8.0
                all_records.append(record)
                continue
            heure_entree = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=9)
            heure_sortie = heure_entree + timedelta(hours=9)
            if anomaly_type == 'entree_tardive':
                retard = timedelta(minutes=np.random.randint(15, 70))
                heure_entree += retard
                record["Entrée tardive"] = format_timedelta(retard)
            elif anomaly_type == 'sortie_anticipee':
                anticipation = timedelta(minutes=np.random.randint(15, 90))
                heure_sortie -= anticipation
                record["Sortie anticipée"] = format_timedelta(anticipation)
            elif anomaly_type == 'presence_insuffisante':
                 heure_sortie = heure_entree + timedelta(hours=np.random.randint(5, 8), minutes=np.random.randint(0,59))
            elif anomaly_type == 'badgeage_impair':
                record["Anomalie(badgeage impair)"] = "Oui"
                if np.random.rand() < 0.5: record["Entrée"] = heure_entree.strftime("%H:%M:%S")
                else: record["Sortie"] = heure_sortie.strftime("%H:%M:%S")
                all_records.append(record)
                continue
            record["Entrée"] = heure_entree.strftime("%H:%M:%S")
            record["Sortie"] = heure_sortie.strftime("%H:%M:%S")
            temps_reel_td = heure_sortie - heure_entree - timedelta(hours=1)
            record["Temps de présence réel"] = format_timedelta(temps_reel_td if temps_reel_td > timedelta(0) else timedelta(0))
        else:
            heure_entree = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=9, minutes=np.random.randint(-10, 5))
            heure_sortie = heure_entree + timedelta(hours=9, minutes=np.random.randint(-5, 30))
            record["Entrée"] = heure_entree.strftime("%H:%M:%S")
            record["Sortie"] = heure_sortie.strftime("%H:%M:%S")
            temps_reel_td = heure_sortie - heure_entree - timedelta(hours=1)
            record["Temps de présence réel"] = format_timedelta(temps_reel_td if temps_reel_td > timedelta(0) else timedelta(0))
        all_records.append(record)

df_final = pd.DataFrame(all_records)
df_final.to_csv("pointages_orange_maroc_final.csv", index=False, sep=',')
print(f"\nDataset généré avec succès ! {len(df_final)} lignes créées.")
print(f"Fichier sauvegardé sous : pointages_orange_maroc_final.csv")