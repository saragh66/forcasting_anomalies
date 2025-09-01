# ==============================================================================
# FICHIER : core/forms.py (Version mise à jour avec la case à cocher)
# ==============================================================================
from django import forms

# Les en-têtes requis ne changent pas
REQUIRED_HEADERS = [
    "MATRICULE", "NOM", "PRENOM", "Date", "Entrée", "Sortie",
    "Temps de présence réel", "Temps de présence théorique",
    "Entrée tardive", "Sortie anticipée",
    "Absence Justifiée (par heure)", "Absence non justifiée",
    "Anomalie(badgeage impair)", "Jour TT Planifié",
    "Departement", "Direction"
]

class CSVUploadForm(forms.Form):
    file = forms.FileField(
        label="Sélectionnez votre rapport de présence (CSV)",
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    # La case à cocher a été supprimée, ce champ n'existe plus.

    def clean_file(self):
        f = self.cleaned_data.get("file")
        if not f:
            raise forms.ValidationError("Aucun fichier sélectionné.")
        
        try:
            # lecture rapide des en-têtes pour validation
            head = f.read(4096).decode('utf-8-sig', errors="ignore").splitlines()[0]
            f.seek(0) # Très important de rembobiner le fichier après lecture
            
            missing_headers = [h for h in REQUIRED_HEADERS if h not in head]
            if missing_headers:
                raise forms.ValidationError(f"Colonne(s) manquante(s) dans le CSV : {', '.join(missing_headers)}")
        
        except Exception:
            raise forms.ValidationError("Impossible de lire le fichier. Assurez-vous qu'il est au format CSV et encodé en UTF-8.")
            
        return f
# Formulaire pour filtrer l'historique des emails/anomalies (inchangé)
class HistoriqueFilterForm(forms.Form):
    start_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'})
    )
    matricule = forms.CharField(
        max_length=50, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'M12345'})
    )