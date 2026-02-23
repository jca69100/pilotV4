"""
Système de persistance automatique AMÉLIORÉ
Sauvegarde et charge les données ET les fichiers uploadés
Version 2.1 - Février 2026
"""

import pickle
import os
from pathlib import Path
from io import BytesIO

# Dossier de sauvegarde
SAVE_DIR = Path(".greenlog_data")

def init_save_dir():
    """Initialise le dossier de sauvegarde"""
    SAVE_DIR.mkdir(exist_ok=True)

# ============================================================================
# FICHIERS LOGISTICIENS PARTAGÉS
# ============================================================================

def save_shared_logisticiens(data):
    """Sauvegarde les fichiers logisticiens partagés
    
    Args:
        data: Dict avec structure {
            'mois_n': {'name': str, 'file': UploadedFile, 'uploaded_at': datetime},
            'mois_n1': {...},
            'mois_n2': {...}
        }
    """
    try:
        init_save_dir()
        
        # Préparer les données pour sauvegarde (convertir files en bytes)
        save_data = {}
        for key, value in data.items():
            if 'file' in value:
                # Lire le contenu du fichier
                file_obj = value['file']
                file_obj.seek(0)  # Retour au début
                file_bytes = file_obj.read()
                
                save_data[key] = {
                    'name': value['name'],
                    'file_bytes': file_bytes,
                    'uploaded_at': value['uploaded_at']
                }
        
        filepath = SAVE_DIR / "shared_logisticiens.pkl"
        with open(filepath, 'wb') as f:
            pickle.dump(save_data, f)
        return True
    except Exception as e:
        print(f"Erreur sauvegarde fichiers partagés : {e}")
        return False

def load_shared_logisticiens():
    """Charge les fichiers logisticiens partagés
    
    Returns:
        Dict avec structure {
            'mois_n': {'name': str, 'file': BytesIO, 'uploaded_at': datetime},
            ...
        }
    """
    try:
        filepath = SAVE_DIR / "shared_logisticiens.pkl"
        if filepath.exists():
            with open(filepath, 'rb') as f:
                save_data = pickle.load(f)
            
            # Reconvertir bytes en file objects
            loaded_data = {}
            for key, value in save_data.items():
                file_obj = BytesIO(value['file_bytes'])
                file_obj.name = value['name']  # Ajouter le nom
                
                loaded_data[key] = {
                    'name': value['name'],
                    'file': file_obj,
                    'uploaded_at': value['uploaded_at']
                }
            
            return loaded_data
    except Exception as e:
        print(f"Erreur chargement fichiers partagés : {e}")
    return {}

# ============================================================================
# FICHIERS UPLOADÉS PAR MODULE
# ============================================================================

def save_module_files(module_name, files_dict):
    """Sauvegarde les fichiers uploadés d'un module
    
    Args:
        module_name: Nom du module (ex: 'retours', 'dpd', 'mondial_relay', 'colissimo')
        files_dict: Dict des fichiers à sauvegarder {
            'csv_retours': UploadedFile,
            'log1': UploadedFile,
            ...
        }
    """
    try:
        init_save_dir()
        
        # Préparer les données (convertir files en bytes)
        save_data = {}
        for key, file_obj in files_dict.items():
            if file_obj is not None:
                file_obj.seek(0)
                save_data[key] = {
                    'name': file_obj.name,
                    'bytes': file_obj.read()
                }
        
        filepath = SAVE_DIR / f"{module_name}_files.pkl"
        with open(filepath, 'wb') as f:
            pickle.dump(save_data, f)
        
        # Déclencher sauvegarde automatique si activée
        try:
            import streamlit as st
            if st.session_state.get('auto_backup_enabled', False):
                from shared.auto_backup import trigger_backup_after_save
                trigger_backup_after_save(module_name, f'Fichiers {module_name} uploadés')
        except:
            pass
        
        return True
    except Exception as e:
        print(f"Erreur sauvegarde fichiers module {module_name} : {e}")
        return False

def load_module_files(module_name):
    """Charge les fichiers uploadés d'un module
    
    Args:
        module_name: Nom du module
        
    Returns:
        Dict des fichiers {
            'csv_retours': BytesIO,
            'log1': BytesIO,
            ...
        } ou None
    """
    try:
        filepath = SAVE_DIR / f"{module_name}_files.pkl"
        if filepath.exists():
            with open(filepath, 'rb') as f:
                save_data = pickle.load(f)
            
            # Reconvertir bytes en file objects
            loaded_files = {}
            for key, data in save_data.items():
                file_obj = BytesIO(data['bytes'])
                file_obj.name = data['name']
                loaded_files[key] = file_obj
            
            return loaded_files
    except Exception as e:
        print(f"Erreur chargement fichiers module {module_name} : {e}")
    return None

# ============================================================================
# DONNÉES TRAITÉES PAR MODULE
# ============================================================================

def save_module_data(module_name, data):
    """Sauvegarde les données traitées d'un module"""
    try:
        init_save_dir()
        filepath = SAVE_DIR / f"{module_name}_data.pkl"
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        
        # Déclencher sauvegarde automatique si activée
        try:
            import streamlit as st
            if st.session_state.get('auto_backup_enabled', False):
                from shared.auto_backup import trigger_backup_after_save
                trigger_backup_after_save(module_name, f'Données {module_name} modifiées')
        except:
            # Silencieusement ignorer si pas dans contexte Streamlit
            pass
        
        return True
    except Exception as e:
        print(f"Erreur sauvegarde données module {module_name} : {e}")
        return False

def load_module_data(module_name):
    """Charge les données traitées d'un module"""
    try:
        filepath = SAVE_DIR / f"{module_name}_data.pkl"
        if filepath.exists():
            with open(filepath, 'rb') as f:
                return pickle.load(f)
    except Exception as e:
        print(f"Erreur chargement données module {module_name} : {e}")
    return None

# ============================================================================
# SUPPRESSION
# ============================================================================

def delete_module_data(module_name):
    """Supprime TOUTES les sauvegardes d'un module (fichiers + données)"""
    try:
        if SAVE_DIR.exists():
            # Supprimer les fichiers uploadés
            file_path = SAVE_DIR / f"{module_name}_files.pkl"
            if file_path.exists():
                file_path.unlink()
            
            # Supprimer les données traitées
            data_path = SAVE_DIR / f"{module_name}_data.pkl"
            if data_path.exists():
                data_path.unlink()
        
        return True
    except Exception as e:
        print(f"Erreur suppression module {module_name} : {e}")
        return False

def delete_all_saved_data():
    """
    Supprime toutes les sauvegardes SAUF :
    - Bibliothèque des analyses (library.pkl)
    - Bibliothèque logisticiens (logisticiens_library.pkl)
    - Indemnisations (géré séparément)
    """
    try:
        if SAVE_DIR.exists():
            # Fichiers à préserver
            preserve_files = {
                'library.pkl',              # Bibliothèque analyses
                'logisticiens_library.pkl'  # Bibliothèque logisticiens
            }
            
            for file in SAVE_DIR.glob("*.pkl"):
                if file.name not in preserve_files:
                    file.unlink()
                    print(f"🗑️ Supprimé: {file.name}")
                else:
                    print(f"✅ Préservé: {file.name}")
        return True
    except Exception as e:
        print(f"Erreur suppression totale : {e}")
        return False

# ============================================================================
# INFORMATIONS
# ============================================================================

def get_saved_files_info():
    """Retourne les infos sur les fichiers sauvegardés"""
    info = {
        'has_shared': (SAVE_DIR / "shared_logisticiens.pkl").exists(),
        'has_retours_files': (SAVE_DIR / "retours_files.pkl").exists(),
        'has_retours_data': (SAVE_DIR / "retours_data.pkl").exists(),
        'has_dpd_files': (SAVE_DIR / "dpd_files.pkl").exists(),
        'has_dpd_data': (SAVE_DIR / "dpd_data.pkl").exists(),
        'has_mondial_relay_files': (SAVE_DIR / "mondial_relay_files.pkl").exists(),
        'has_mondial_relay_data': (SAVE_DIR / "mondial_relay_data.pkl").exists(),
        'has_colissimo_files': (SAVE_DIR / "colissimo_files.pkl").exists(),
        'has_colissimo_data': (SAVE_DIR / "colissimo_data.pkl").exists(),
    }
    return info

# ============================================================================
# BIBLIOTHÈQUE DE FICHIERS
# ============================================================================

def save_library(library_data):
    """
    Sauvegarde la bibliothèque de fichiers
    
    Args:
        library_data: Dict avec structure {
            'YYYY_MM': {
                'file_type': [
                    {
                        'filename': str,
                        'content': bytes,
                        'size': int,
                        'uploaded_at': str (ISO format),
                        'description': str,
                        'period_year': int,
                        'period_month': int
                    }
                ]
            }
        }
    """
    try:
        init_save_dir()
        filepath = SAVE_DIR / "library.pkl"
        with open(filepath, 'wb') as f:
            pickle.dump(library_data, f)
        
        # Déclencher sauvegarde automatique si activée
        try:
            import streamlit as st
            if st.session_state.get('auto_backup_enabled', False):
                from shared.auto_backup import trigger_backup_after_save
                trigger_backup_after_save('bibliotheque', 'Analyse archivée dans bibliothèque')
        except:
            pass
        
        return True
    except Exception as e:
        print(f"Erreur sauvegarde bibliothèque: {e}")
        return False

def load_library():
    """
    Charge la bibliothèque de fichiers
    
    Returns:
        Dict ou None si pas de sauvegarde
    """
    try:
        filepath = SAVE_DIR / "library.pkl"
        if filepath.exists():
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        return None
    except Exception as e:
        print(f"Erreur chargement bibliothèque: {e}")
        return None

def delete_library():
    """Supprime la bibliothèque complète"""
    try:
        filepath = SAVE_DIR / "library.pkl"
        if filepath.exists():
            filepath.unlink()
        return True
    except Exception as e:
        print(f"Erreur suppression bibliothèque: {e}")
        return False

# ============================================================================
# BIBLIOTHÈQUE LOGISTICIENS (Cumulative)
# ============================================================================

def save_logisticiens_library(library_data):
    """
    Sauvegarde la bibliothèque de fichiers logisticiens
    
    Args:
        library_data: Dict avec structure {
            'YYYY_MM': {
                'filename': str,
                'content': bytes,
                'size': int,
                'uploaded_at': str (ISO),
                'year': int,
                'month': int
            }
        }
    """
    try:
        init_save_dir()
        filepath = SAVE_DIR / "logisticiens_library.pkl"
        with open(filepath, 'wb') as f:
            pickle.dump(library_data, f)
        
        # Déclencher sauvegarde automatique si activée
        try:
            import streamlit as st
            if st.session_state.get('auto_backup_enabled', False):
                from shared.auto_backup import trigger_backup_after_save
                trigger_backup_after_save('logisticiens', 'Fichier logisticien ajouté')
        except:
            pass
        
        return True
    except Exception as e:
        print(f"Erreur sauvegarde bibliothèque logisticiens: {e}")
        return False

def load_logisticiens_library():
    """
    Charge la bibliothèque de fichiers logisticiens
    
    Returns:
        Dict ou None
    """
    try:
        filepath = SAVE_DIR / "logisticiens_library.pkl"
        if filepath.exists():
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        return None
    except Exception as e:
        print(f"Erreur chargement bibliothèque logisticiens: {e}")
        return None

def delete_logisticiens_library():
    """Supprime la bibliothèque logisticiens"""
    try:
        filepath = SAVE_DIR / "logisticiens_library.pkl"
        if filepath.exists():
            filepath.unlink()
        return True
    except Exception as e:
        print(f"Erreur suppression bibliothèque logisticiens: {e}")
        return False

def _save_to_library(transporteur, df, data_dict, period_year, period_month, 
                     date_min, date_max, match_rate="N/A"):
    """
    Helper pour sauvegarder dans la bibliothèque
    """
    from datetime import datetime
    
    # Charger la bibliothèque
    library = load_library()
    if library is None:
        library = {}
    
    # Créer la clé de période
    period_key = f"{period_year}_{period_month:02d}"
    
    if period_key not in library:
        library[period_key] = {}
    
    if transporteur not in library[period_key]:
        library[period_key][transporteur] = []
    
    # Extraire les partenaires si disponible
    partners = []
    partner_cols = [col for col in df.columns if 'partenaire' in col.lower()]
    if partner_cols:
        partners = df[partner_cols[0]].dropna().unique().tolist()[:10]
    
    # Créer l'entrée d'analyse
    analysis_entry = {
        'analyzed_at': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'nb_rows': len(df),
        'partners': partners,
        'data': data_dict,
        'period_year': period_year,
        'period_month': period_month,
        'date_range': f"{date_min.strftime('%d/%m/%Y')} - {date_max.strftime('%d/%m/%Y')}",
        'match_rate': match_rate
    }
    
    # Ajouter à la bibliothèque (max 3 analyses par période/transporteur)
    library[period_key][transporteur].insert(0, analysis_entry)
    if len(library[period_key][transporteur]) > 3:
        library[period_key][transporteur] = library[period_key][transporteur][:3]
    
    # Sauvegarder
    save_library(library)
    
    print(f"✅ Archivé dans: {period_key}")
    print("="*60)
    
    return (True, period_year, period_month)


def auto_archive_analysis(transporteur, df, data_dict, date_column='Date'):
    """
    Archive automatiquement une analyse avec détection de période
    BASÉE SUR LE MATCHING TRACKING + DATE COMMANDE LOGISTICIEN
    
    Logique universelle pour tous les transporteurs:
    1. Cherche colonne tracking dans la facture
    2. Match avec fichiers logisticiens
    3. Récupère dates de commande
    4. Détermine période selon ces dates
    
    Args:
        transporteur: Nom du transporteur (DPD, CHRONOPOST, etc.)
        df: DataFrame analysé
        data_dict: Dictionnaire de données à sauvegarder
        date_column: Nom de la colonne date (non utilisé avec nouvelle logique)
    
    Returns:
        tuple: (success: bool, period_year: int, period_month: int)
    """
    try:
        import pandas as pd
        from datetime import datetime
        from collections import Counter
        
        print("="*60)
        print(f"📊 AUTO-ARCHIVAGE {transporteur.upper()}")
        print("="*60)
        
        # ============================================================
        # ÉTAPE 0 : VÉRIFIER SI DATE COMMANDE DÉJÀ PRÉSENTE
        # ============================================================
        
        # Si le DataFrame contient déjà 'Date de la commande',
        # on peut sauter le matching et utiliser directement
        if 'Date de la commande' in df.columns:
            print("✅ Colonne 'Date de la commande' déjà présente dans le DataFrame")
            print(f"🔄 Utilisation directe sans matching")
            
            dates_commande = pd.to_datetime(df['Date de la commande'], errors='coerce').dropna()
            
            if len(dates_commande) == 0:
                print("⚠️ Aucune date de commande valide")
                print("🔄 Fallback: utilisation date facture")
                return _fallback_date_detection(df, data_dict, transporteur, date_column)
            
            # Analyser les 3 derniers mois
            max_date = dates_commande.max()
            cutoff_date = max_date - pd.DateOffset(months=3)
            dates_recent = dates_commande[dates_commande >= cutoff_date]
            
            print(f"📅 Date commande la plus récente: {max_date.strftime('%d/%m/%Y')}")
            print(f"📅 Analyse sur 3 derniers mois: {len(dates_recent)} dates")
            
            # Compter par mois
            year_months = [(d.year, d.month) for d in dates_recent]
            counter = Counter(year_months)
            
            if counter:
                most_common_period, count = counter.most_common(1)[0]
                period_year, period_month = most_common_period
                percentage = (count / len(dates_recent)) * 100
                print(f"✅ PÉRIODE DÉTECTÉE: {period_month:02d}/{period_year}")
                print(f"   • {count} commandes dans ce mois ({percentage:.1f}%)")
            else:
                period_year = max_date.year
                period_month = max_date.month
                print(f"✅ PÉRIODE (fallback date max): {period_month:02d}/{period_year}")
            
            # Sauvegarder dans bibliothèque
            return _save_to_library(transporteur, df, data_dict, period_year, period_month, 
                                   dates_commande.min(), dates_commande.max(), match_rate="100%")
        
        # ============================================================
        # ÉTAPE 1 : IDENTIFIER LA COLONNE TRACKING
        # ============================================================
        
        # Colonnes possibles de tracking selon le transporteur
        tracking_cols_priority = [
            'Tracking',
            'DPD ID',
            'N° tracking',
            'Numéro de tracking',
            'tracking',
            'Track'
        ]
        
        tracking_col = None
        for col in tracking_cols_priority:
            if col in df.columns:
                tracking_col = col
                break
        
        if not tracking_col:
            # Chercher toute colonne avec "track"
            for col in df.columns:
                if 'track' in col.lower():
                    tracking_col = col
                    break
        
        if not tracking_col:
            print(f"⚠️ Aucune colonne tracking trouvée")
            print(f"📋 Colonnes disponibles: {df.columns.tolist()}")
            print(f"🔄 Fallback: utilisation date facture")
            return _fallback_date_detection(df, data_dict, transporteur, date_column)
        
        print(f"✅ Colonne tracking identifiée: '{tracking_col}'")
        
        # ============================================================
        # ÉTAPE 2 : CHARGER FICHIERS LOGISTICIENS
        # ============================================================
        
        from modules.logisticiens_library import load_logisticien_files_for_analysis
        
        log_files = load_logisticien_files_for_analysis(nb_months=6)  # 6 mois pour être sûr
        
        if len(log_files) == 0:
            print(f"⚠️ Aucun fichier logisticien dans la bibliothèque")
            print(f"🔄 Fallback: utilisation date facture")
            return _fallback_date_detection(df, data_dict, transporteur, date_column)
        
        print(f"✅ {len(log_files)} fichier(s) logisticien chargés")
        
        # ============================================================
        # ÉTAPE 3 : FUSIONNER FICHIERS LOGISTICIENS
        # ============================================================
        
        all_log_data = []
        for log_file in log_files:
            try:
                log_file.seek(0)
                df_log_temp = pd.read_excel(log_file, sheet_name='Facturation préparation')
                all_log_data.append(df_log_temp)
            except Exception as e:
                print(f"⚠️ Erreur lecture fichier: {str(e)}")
        
        if not all_log_data:
            print(f"⚠️ Impossible de lire les fichiers logisticiens")
            print(f"🔄 Fallback: utilisation date facture")
            return _fallback_date_detection(df, data_dict, transporteur, date_column)
        
        df_log = pd.concat(all_log_data, ignore_index=True)
        print(f"✅ Fichiers logisticiens fusionnés: {len(df_log)} lignes")
        
        # ============================================================
        # ÉTAPE 4 : MATCHING TRACKING → DATE COMMANDE
        # ============================================================
        
        # Nettoyer les trackings (enlever espaces, mettre en string)
        df['_tracking_clean'] = df[tracking_col].astype(str).str.strip().str.replace('.0', '', regex=False)
        df_log['_tracking_clean'] = df_log['Numéro de tracking'].astype(str).str.strip().str.replace('.0', '', regex=False)
        
        # Merger pour récupérer les dates de commande
        df_merged = df.merge(
            df_log[['_tracking_clean', 'Date de la commande']],
            on='_tracking_clean',
            how='left'
        )
        
        # Statistiques matching
        nb_total = len(df)
        nb_matched = df_merged['Date de la commande'].notna().sum()
        match_rate = (nb_matched / nb_total * 100) if nb_total > 0 else 0
        
        print(f"📊 Matching: {nb_matched}/{nb_total} trackings trouvés ({match_rate:.1f}%)")
        
        if nb_matched == 0:
            print(f"⚠️ Aucun tracking matché")
            print(f"🔄 Fallback: utilisation date facture")
            return _fallback_date_detection(df, data_dict, transporteur, date_column)
        
        # ============================================================
        # ÉTAPE 5 : DÉTECTION PÉRIODE SELON DATES COMMANDE
        # ============================================================
        
        # Convertir en datetime
        df_merged['Date de la commande'] = pd.to_datetime(df_merged['Date de la commande'], errors='coerce')
        
        # Filtrer dates valides
        dates_commande = df_merged['Date de la commande'].dropna()
        
        if len(dates_commande) == 0:
            print(f"⚠️ Aucune date de commande valide")
            print(f"🔄 Fallback: utilisation date facture")
            return _fallback_date_detection(df, data_dict, transporteur, date_column)
        
        # Analyser les 3 derniers mois
        max_date = dates_commande.max()
        cutoff_date = max_date - pd.DateOffset(months=3)
        dates_recent = dates_commande[dates_commande >= cutoff_date]
        
        print(f"📅 Date commande la plus récente: {max_date.strftime('%d/%m/%Y')}")
        print(f"📅 Analyse sur 3 derniers mois: {len(dates_recent)} dates")
        
        # Compter par mois
        year_months = [(d.year, d.month) for d in dates_recent]
        counter = Counter(year_months)
        
        # Prendre le mois avec le plus d'occurrences
        if counter:
            most_common_period, count = counter.most_common(1)[0]
            period_year, period_month = most_common_period
            
            percentage = (count / len(dates_recent)) * 100
            print(f"✅ PÉRIODE DÉTECTÉE: {period_month:02d}/{period_year}")
            print(f"   • {count} commandes dans ce mois ({percentage:.1f}%)")
        else:
            period_year = max_date.year
            period_month = max_date.month
            print(f"✅ PÉRIODE (fallback date max): {period_month:02d}/{period_year}")
        
        # ============================================================
        # ÉTAPE 6 : SAUVEGARDE DANS BIBLIOTHÈQUE
        # ============================================================
        
        return _save_to_library(transporteur, df, data_dict, period_year, period_month,
                               dates_commande.min(), dates_commande.max(), 
                               match_rate=f"{match_rate:.1f}%")
        
    except Exception as e:
        print(f"❌ Erreur auto-archivage: {str(e)}")
        import traceback
        traceback.print_exc()
        return (False, None, None)


def _fallback_date_detection(df, data_dict, transporteur, date_column):
    """
    Fonction fallback si matching tracking impossible
    Utilise la détection par date classique
    """
    try:
        import pandas as pd
        from datetime import datetime
        from collections import Counter
        
        print("🔄 MODE FALLBACK: Détection par date de facture")
        
        # Chercher colonne de date
        if date_column not in df.columns:
            priority_cols = [
                'Date',
                'Date d\'expédition',
                'Date d expédition', 
                'Date d expedition',
                'Date expédition',
                'Date de la commande'
            ]
            
            found_col = None
            for col in priority_cols:
                if col in df.columns:
                    found_col = col
                    break
            
            if not found_col:
                date_cols = [col for col in df.columns if 'date' in col.lower()]
                if not date_cols:
                    print(f"❌ Aucune colonne de date trouvée")
                    return (False, None, None)
                found_col = date_cols[0]
            
            date_column = found_col
        
        print(f"📅 Colonne date: '{date_column}'")
        
        # Convertir en datetime
        if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
            df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
        
        dates_valid = df[date_column].dropna()
        
        if len(dates_valid) == 0:
            print("❌ Aucune date valide")
            return (False, None, None)
        
        # Analyser 3 derniers mois
        max_date = dates_valid.max()
        cutoff_date = max_date - pd.DateOffset(months=3)
        dates_recent = dates_valid[dates_valid >= cutoff_date]
        
        # Compter par mois
        year_months = [(d.year, d.month) for d in dates_recent]
        counter = Counter(year_months)
        
        if counter:
            most_common_period, count = counter.most_common(1)[0]
            period_year, period_month = most_common_period
        else:
            period_year = max_date.year
            period_month = max_date.month
        
        print(f"✅ Période détectée: {period_month:02d}/{period_year}")
        
        # Sauvegarder
        return _save_to_library(transporteur, df, data_dict, period_year, period_month,
                               dates_valid.min(), dates_valid.max(), match_rate="Fallback")
        
    except Exception as e:
        print(f"❌ Erreur fallback: {str(e)}")
        return (False, None, None)
        
        print(f"✅ Analyse archivée : {transporteur} - {period_month}/{period_year}")
        
        return (True, period_year, period_month)
        
    except Exception as e:
        print(f"❌ Erreur auto-archive: {e}")
        import traceback
        traceback.print_exc()
        return (False, None, None)

