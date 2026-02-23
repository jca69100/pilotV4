# CHANGELOG - GREENLOG EC

## [2.1.1] - Février 2026

### 🎉 INTÉGRATION MODULE CHRONOPOST

**NOUVEAUTÉ MAJEURE**
- ✨ Nouveau module Chronopost avec analyse complète des factures
- ✨ Détection automatique de 7 types de surplus
- ✨ 4 onglets de visualisation (Synthèse, Surplus, Détail, Retours)
- ✨ Utilise les fichiers logisticiens partagés

### ✨ Nouvelles Fonctionnalités

**Module Chronopost (v1.0)**
- ✅ Upload multi-factures Chronopost (.xlsx)
- ✅ Grilles tarifaires France et Europe intégrées
- ✅ Calcul automatique des prix théoriques
- ✅ Comparaison poids logisticien vs poids Chronopost
- ✅ Détection de 7 types de surplus :
  - Étiquette non conforme (2€)
  - Zones Difficiles d'accès (5€)
  - Supplément Corse (5€)
  - Traitement Retour expéditeur (2€)
  - Retour expéditeur (20€)
  - Supplément manutention (20€)
  - Supplément hors norme (70€)
- ✅ Pré-sélection automatique des surplus prioritaires
- ✅ Export Excel par onglet avec filtres respectés
- ✅ Export détail uniquement écarts défavorables
- ✅ Statistiques période (date min/max)
- ✅ Total à contester (écarts + surplus)
- ✅ Persistance automatique (fichiers + données)
- ✅ Bouton réinitialisation dédié

**Architecture**
- ✅ 5 modules disponibles (4 existants + Chronopost)
- ✅ Fichiers logisticiens partagés entre TOUS les modules
- ✅ Module Chronopost intégré à l'architecture modulaire
- ✅ Persistance complète (fichiers partagés + module Chronopost)

**Interface Page d'Accueil**
- ✅ Mention de Chronopost dans les fichiers partagés
- ✅ Bouton module Chronopost avec icône 📦
- ✅ Description : "Analyse factures avec écarts et surplus"
- ✅ Statistiques : "5 modules disponibles"

### 🔧 Améliorations

**Partage de Fichiers**
- Fichiers logisticiens uploadés une fois sur page d'accueil
- Disponibles automatiquement dans :
  - DPD ✅
  - Mondial Relay ✅
  - Colissimo ✅
  - Chronopost ✅ (nouveau)

**Persistence**
- Sauvegarde automatique des factures Chronopost
- Sauvegarde des résultats d'analyse
- Rechargement automatique au démarrage du module
- Suppression complète avec bouton réinitialisation

### 📋 Compatibilité

- ✅ **V2.1 → V2.1.1** : Compatible à 100%
- ✅ Les données des 4 modules existants fonctionnent normalement
- ✅ Nouveau module Chronopost s'ajoute sans conflit
- ✅ Fichiers logisticiens partagés compatibles

---

## [2.1.0] - Février 2026

### 🎉 PERSISTANCE AUTOMATIQUE DES FICHIERS UPLOADÉS

**NOUVEAUTÉ MAJEURE**
- ✨ Les fichiers uploadés sont maintenant sauvegardés automatiquement
- ✨ Rechargement automatique au démarrage de l'application
- ✨ Plus besoin de re-uploader les fichiers à chaque session

### ✨ Nouvelles Fonctionnalités

**Système de Persistance Amélioré**
- Nouveau : `persistence.save_module_files()` - Sauvegarde des fichiers uploadés
- Nouveau : `persistence.load_module_files()` - Chargement des fichiers uploadés
- Nouveau : `persistence.delete_module_data()` - Suppression complète par module

**Module Retours (v2.1)**
- ✅ Fichier CSV sauvegardé automatiquement
- ✅ Rechargement automatique au démarrage
- ✅ Affichage "Fichier déjà chargé" avec nom du fichier
- ✅ Bouton "Traiter le fichier" pour relancer l'analyse
- ✅ Suppression complète avec "Réinitialiser"

**Module DPD (v2.1)**
- ✅ 5 fichiers sauvegardés automatiquement (3 logisticien + 2 DPD)
- ✅ Rechargement automatique
- ✅ Affichage de la liste des fichiers chargés
- ✅ Bouton "Relancer l'analyse" avec fichiers persistants
- ✅ Suppression complète

**Module Mondial Relay (v2.1)**
- ✅ 2-3 fichiers sauvegardés automatiquement (CSV + logisticiens)
- ✅ Rechargement automatique
- ✅ Suppression complète

**Module Colissimo (v1.1)**
- ✅ 4 fichiers sauvegardés automatiquement (CSV + 3 logisticiens)
- ✅ Rechargement automatique
- ✅ Suppression complète

---

## [2.0.0] - Février 2026

### 🎉 Version Majeure - Architecture Modulaire

**BREAKING CHANGES**
- Refonte complète de l'architecture
- Structure modulaire remplaçant le fichier unique

### ✨ Nouvelles Fonctionnalités

**Architecture**
- Page d'accueil centralisée avec navigation
- Système de modules indépendants
- Partage de fichiers logisticiens entre modules
- État global de l'application (`module_data`)

**Module Retours (v2.0)**
- Import/Export de session
- Sauvegarde persistante des données traitées
- Interface améliorée
- Intégré à l'architecture modulaire

**Module DPD (nouveau)**
- Import 5 fichiers (3 logisticien + 2 DPD)
- Fusion automatique des fichiers
- Lecture automatique des taxes (Fuel + Sûreté)
- Calcul prix total ligne
- 4 onglets : Synthèse, Détail, Suppléments, Retours
- Export Excel multi-feuilles
- Utilise les fichiers logisticiens partagés
- Taux NON ATTRIBUÉ < 5%

**Module Mondial Relay (nouveau)**
- Gestion retours TOOPOST
- Taxe fuel configurable
- Filtrage et dédoublonnage automatique

**Module Colissimo (nouveau)**
- Retours 8R
- 3 méthodes de correspondance

---

## Roadmap

### [2.2.0] - À venir
- Dashboard global multi-modules
- Comparaison de périodes
- Exports consolidés
- Rapports automatiques

### [3.0.0] - Futur
- API REST
- Intégration autres transporteurs
- Analyse prédictive

---

## Notes de Version

### Migration V2.1 → V2.1.1

**Automatique** :
- Les 4 modules existants continuent de fonctionner normalement
- Module Chronopost s'ajoute sans impacter les autres
- Fichiers logisticiens partagés fonctionnent avec tous les modules

**Nouveau** :
- Uploader des factures Chronopost pour utiliser le nouveau module

### Migration V2.0 → V2.1.1

**Compatible** :
- Toutes les données V2.0/V2.1 sont compatibles
- Ajout du module Chronopost sans conflit
- Fichiers uploadés doivent être re-uploadés une fois pour persistance

### Support

- V1.0 : Support arrêté
- V2.0 : Support maintenu (compatible V2.1.1)
- V2.1 : Support maintenu (compatible V2.1.1)
- V2.1.1 : Version actuelle, support complet

---

**Légende**
- ✨ Nouvelle fonctionnalité
- 🔧 Amélioration
- 🐛 Correction de bug
- 📋 Documentation
- ⚠️ Breaking change
- 🎉 Version majeure
