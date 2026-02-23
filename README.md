# 📦 Gestion des Retours GREENLOG et Transporteurs - V1
## Application Streamlit avec Persistance Automatique

---

## 🎯 À PROPOS

**Application professionnelle pour la gestion des retours et l'analyse des transporteurs**

✅ Interface aux couleurs de GREENLOG  
✅ **6 modules de gestion intégrés**  
✅ Persistance automatique des données  
✅ Fichiers logisticiens partagés entre modules  
✅ Analyse complète multi-transporteurs  

---

## 🚀 INSTALLATION SUR STREAMLIT CLOUD

### Étape 1 : Uploadez sur GitHub

1. Créez un nouveau repository sur GitHub
2. Uploadez **TOUS** les fichiers de ce dossier :
   - `app.py`
   - `logo_greenlog.jpg` ⭐
   - `requirements.txt`
   - `.gitignore`
   - `modules/` (tout le dossier avec 6 modules)
   - `shared/` (tout le dossier)

### Étape 2 : Déployez sur Streamlit Cloud

1. Allez sur https://share.streamlit.io
2. Cliquez "New app"
3. Sélectionnez votre repository
4. **Main file path** : `app.py` ⭐ IMPORTANT
5. Cliquez "Deploy"

✅ C'est tout !

---

## 💻 INSTALLATION EN LOCAL

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Lancer l'application
streamlit run app.py
```

---

## 📚 MODULES DISPONIBLES (6 modules)

### 1. 🔄 Retours Produits
- Analyse des retours clients par partenaire
- Export Excel détaillé
- Statistiques par partenaire

### 2. 📊 DPD
- Analyse factures DPD
- Calcul automatique des taxes
- Répartition par partenaire

### 3. 🌐 Mondial Relay
- Gestion retours TOOPOST
- Taxe fuel automatique
- Correspondance automatique

### 4. 📮 Colissimo
- Retours 8R avec correspondance automatique
- 3 méthodes de traitement
- Export formaté

### 5. 📦 Chronopost
- Analyse factures avec grilles tarifaires France et Europe
- Détection automatique de 7 types de surplus
- 4 onglets de visualisation (Synthèse, Surplus, Détail, Retours)
- Calcul des écarts poids/prix
- Export Excel ciblé sur écarts défavorables

### 6. 🚚 Colis Privé (NOUVEAU)
- **Croisement automatique** fichiers logisticien + fichier CSV Colis Privé
- **Détection des majorations** de service
- **Statistiques détaillées** : Top 10 majorations, répartition par partenaire
- **3 onglets** : Vue d'ensemble, Majorations détectées, Détail complet
- **Export Excel formaté** avec majorations en rouge
- **Utilise les fichiers logisticiens partagés** (pas de re-upload)
- **Persistance automatique** des données

---

## 💾 FICHIERS LOGISTICIENS PARTAGÉS

**Concept clé de l'application :**

```
Page d'Accueil
    ↓
Upload 3 fichiers logisticiens UNE FOIS
    ↓
Disponibles automatiquement dans TOUS les modules
    ↓
(DPD, Mondial Relay, Colissimo, Chronopost, Colis Privé)
    ↓
Économie de temps + Cohérence des données
```

### Avantages

1. **Upload unique** : Pas besoin de ré-uploader dans chaque module
2. **Cohérence** : Mêmes données utilisées partout
3. **Gain de temps** : Workflow optimisé
4. **Persistance** : Fichiers sauvegardés automatiquement

---

## 🎯 WORKFLOW TYPIQUE

### Jour 1 : Configuration initiale

```
1. Ouvrir l'application
2. Page d'accueil → Upload 3 fichiers logisticiens
   ✅ Sauvegarde automatique
3. Module Chronopost → Upload factures
   ✅ Analyse → Résultats → Export
   ✅ Sauvegarde automatique
4. Module Colis Privé → Upload CSV
   ✅ Croisement automatique avec fichiers partagés
   ✅ Détection majorations → Export
   ✅ Sauvegarde automatique
```

### Jour 2 : Consultation

```
1. Ouvrir l'application
2. ✅ Fichiers logisticiens déjà là
3. ✅ Données Chronopost déjà là
4. ✅ Données Colis Privé déjà là
5. Consulter, filtrer, exporter
6. Pas de re-upload nécessaire !
```

---

## 🗑️ RÉINITIALISATION

### Par module
Chaque module a un bouton "🗑️ Réinitialiser" qui :
- Supprime les fichiers uploadés du module
- Supprime les résultats d'analyse
- Conserve les fichiers logisticiens partagés

### Globale
La page d'accueil a un bouton "🗑️ Tout Réinitialiser" qui :
- Supprime TOUS les fichiers (y compris partagés)
- Supprime TOUTES les données de TOUS les modules
- Repart à zéro

---

## 📊 MODULE COLIS PRIVÉ - DÉTAILS

### Fichiers requis

1. **Fichiers Logisticien** (Excel) - 3 fichiers partagés depuis page d'accueil
   - Contient : Numéro de tracking, Partenaire, Commandes, Dates, Poids

2. **Fichier Colis Privé** (CSV)
   - Contient : Tracking, Poids facturé, Majoration service, Code Postal
   - Séparateur : point-virgule (;)
   - Encodage : UTF-8

### Fonctionnalités

**📊 Vue d'ensemble**
- Top 10 des majorations les plus élevées
- Répartition par partenaire
- Statistiques globales

**⚠️ Majorations détectées**
- Liste complète des lignes avec majorations
- Filtres par partenaire et montant minimum
- Total après filtres

**📋 Détail complet**
- Toutes les lignes du croisement
- Option : afficher uniquement majorations
- Filtrage par partenaire

**📥 Export Excel**
- Mise en forme automatique
- En-têtes en bleu marine GREENLOG
- **Majorations en rouge** pour visibilité immédiate
- Colonnes ajustées automatiquement

### Statistiques affichées

- Total lignes croisées
- Nombre de lignes avec majorations
- Total des majorations (€)
- Pourcentage de majorations

---

## 🎨 INTERFACE GREENLOG

### Couleurs
- 🔵 Bleu Marine (#2D3E50) : Textes, titres
- 🟢 Vert Menthe (#6BBFA3) : Boutons, accents
- ⚪ Vert Clair (#E8F5F1) : Arrière-plans

### Bandeau principal
- Grand bandeau avec logo GREENLOG intégré
- Dégradé bleu marine
- Bordure verte 3px
- Effet 3D avec ombres

---

## 📦 CONTENU DU PACKAGE

```
greenlog_retours_transporteurs_v1/
├── app.py                    # Application principale avec bandeau GREENLOG
├── logo_greenlog.jpg         # Logo officiel GREENLOG
├── requirements.txt          # Dépendances Python
├── .gitignore               # Fichiers à ignorer
├── README.md                # Ce fichier
├── modules/
│   ├── __init__.py
│   ├── retours.py           # Module Retours Produits
│   ├── dpd.py               # Module DPD
│   ├── mondial_relay.py     # Module Mondial Relay
│   ├── colissimo.py         # Module Colissimo
│   ├── chronopost.py        # Module Chronopost (tarifs corrigés)
│   └── colis_prive.py       # Module Colis Privé (NOUVEAU)
└── shared/
    ├── __init__.py
    └── persistence.py       # Système de persistance automatique
```

---

## 🔧 DÉPANNAGE

### Module Colis Privé ne s'affiche pas
1. Vérifier que `colis_prive.py` est dans `modules/`
2. Vérifier que le routing est dans `app.py`
3. Redémarrer l'application

### Majorations non détectées
1. Vérifier le format du fichier CSV (séparateur `;`)
2. Vérifier l'encodage (UTF-8)
3. Vérifier les noms de colonnes : `Tracking`, `Majoration service`

### Fichiers partagés non disponibles
1. D'abord uploader sur page d'accueil
2. Puis aller dans Module Colis Privé
3. Les fichiers doivent apparaître en vert

---

## 📞 SUPPORT

Pour tout problème :
1. Vérifier que TOUS les fichiers sont uploadés sur GitHub (y compris logo)
2. Vérifier `requirements.txt` contient bien `streamlit pandas openpyxl`
3. Redéployer sur Streamlit Cloud

---

**Version** : V1  
**Application** : Gestion des Retours GREENLOG et Transporteurs  
**Date** : Février 2026  
**Modules** : 6 (Retours, DPD, Mondial Relay, Colissimo, Chronopost, Colis Privé)  
**Status** : Production Ready 🚀
