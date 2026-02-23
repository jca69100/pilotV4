"""
Module : Colissimo - Gestion des Retours 8R
Version 1.1 - Streamlit - AVEC PERSISTANCE FICHIERS
Basé sur cahier des charges v1.0
"""

import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime, timedelta
import re
from shared import persistence

def export_excel(df):
    """Export DataFrame vers Excel"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Retours Colissimo', index=False)
    return output.getvalue()

def safe_float(value):
    """Conversion sécurisée vers float"""
    try:
        if pd.isna(value):
            return 0.0
        # Si format européen avec virgule
        if isinstance(value, str):
            value = value.replace(',', '.')
        return float(value)
    except:
        return 0.0

def clean_tracking(value):
    """Nettoie un numéro de tracking"""
    try:
        if pd.isna(value) or value == '':
            return ''
        value_str = str(value).strip()
        # Enlever les décimales si présentes
        if '.' in value_str:
            value_str = value_str.split('.')[0]
        return value_str
    except:
        return str(value).strip() if value else ''

def extract_numeric_sequence(tracking):
    """Extrait la séquence numérique d'un tracking (minimum 8 chiffres)"""
    if not tracking:
        return None
    # Chercher une séquence de 8 chiffres ou plus
    match = re.search(r'\d{8,}', str(tracking))
    return match.group(0) if match else None

def read_csv_colissimo(file):
    """Lit le fichier CSV facture Colissimo"""
    try:
        # Essayer encodage latin-1
        df = pd.read_csv(file, sep=';', encoding='latin-1')
        return df
    except:
        try:
            file.seek(0)
            df = pd.read_csv(file, sep=';', encoding='utf-8-sig')
            return df
        except Exception as e:
            st.error(f"Erreur lecture CSV : {e}")
            return None

def read_excel_logisticien(file, sheet_name="Facturation préparation"):
    """Lit un fichier Excel logisticien"""
    try:
        df = pd.read_excel(file, sheet_name=sheet_name)
        return df
    except:
        try:
            df = pd.read_excel(file)
            return df
        except Exception as e:
            st.error(f"Erreur lecture Excel : {e}")
            return None

def fusion_logisticiens(log1, log2, log3):
    """Fusionne les 3 fichiers logisticien"""
    dfs = []
    
    for log_file in [log1, log2, log3]:
        if log_file is not None:
            df = read_excel_logisticien(log_file)
            if df is not None:
                dfs.append(df)
    
    if not dfs:
        return None
    
    # Fusion
    df_fusion = pd.concat(dfs, ignore_index=True)
    
    # Nettoyer les trackings
    if 'Numéro de tracking' in df_fusion.columns:
        df_fusion['Tracking_Clean'] = df_fusion['Numéro de tracking'].apply(clean_tracking)
    
    # Convertir dates
    if 'Date d\'expédition' in df_fusion.columns:
        df_fusion['Date_Expedition'] = pd.to_datetime(df_fusion['Date d\'expédition'], errors='coerce')
    
    return df_fusion

def correspondance_tracking_exact(tracking_retour, df_log):
    """Méthode 1 : Correspondance tracking exacte"""
    tracking_clean = clean_tracking(tracking_retour)
    if not tracking_clean:
        return None
    
    matches = df_log[df_log['Tracking_Clean'] == tracking_clean]
    if len(matches) > 0:
        row = matches.iloc[0]
        return {
            'partenaire': row.get('Nom du partenaire', 'NON IDENTIFIÉ'),
            'commande': str(row.get('Numéro de commande d\'origine', '')),
            'tracking_aller': row.get('Tracking_Clean', ''),
            'methode': 'Tracking exact'
        }
    return None

def correspondance_tracking_partiel(tracking_retour, df_log):
    """Méthode 2 : Correspondance tracking partielle (8+ chiffres)"""
    seq_retour = extract_numeric_sequence(tracking_retour)
    if not seq_retour:
        return None
    
    for _, row in df_log.iterrows():
        tracking_aller = row.get('Tracking_Clean', '')
        seq_aller = extract_numeric_sequence(tracking_aller)
        
        if seq_aller and seq_retour in seq_aller:
            return {
                'partenaire': row.get('Nom du partenaire', 'NON IDENTIFIÉ'),
                'commande': str(row.get('Numéro de commande d\'origine', '')),
                'tracking_aller': tracking_aller,
                'methode': 'Tracking partiel'
            }
    
    return None

def correspondance_cp_date(cp_retour, date_retour, df_log):
    """Méthode 3 : Correspondance par code postal + date"""
    try:
        if pd.isna(cp_retour) or pd.isna(date_retour):
            return None
        
        cp_str = str(int(cp_retour)) if isinstance(cp_retour, float) else str(cp_retour)
        date_retour_dt = pd.to_datetime(date_retour, errors='coerce')
        
        if pd.isna(date_retour_dt):
            return None
        
        # Chercher dans le logisticien
        matches = df_log[
            (df_log['Code postal destination'].astype(str).str.strip() == cp_str) &
            (df_log['Date_Expedition'] < date_retour_dt)
        ]
        
        if len(matches) > 0:
            # Prendre la plus récente
            matches_sorted = matches.sort_values('Date_Expedition', ascending=False)
            row = matches_sorted.iloc[0]
            
            return {
                'partenaire': row.get('Nom du partenaire', 'NON IDENTIFIÉ'),
                'commande': str(row.get('Numéro de commande d\'origine', '')),
                'tracking_aller': row.get('Tracking_Clean', ''),
                'methode': 'CP + Date'
            }
    except:
        pass
    
    return None

def traiter_retours_colissimo(df_facture, df_log):
    """Traite les retours Colissimo"""
    
    # 1. Filtrer sur code produit 8R
    df_retours = df_facture[df_facture['Code produit'] == '8R'].copy()
    
    if len(df_retours) == 0:
        return None, None
    
    # 2. Enrichir chaque retour
    resultats = []
    
    for _, row in df_retours.iterrows():
        tracking_retour = clean_tracking(row.get('Tracking', ''))
        date_retour = row.get('Date PCH', '')
        cp_retour = row.get('Code Postal', '')
        
        # Montants
        prix_ht = safe_float(row.get('Prix', 0))
        majoration = safe_float(row.get('Majoration service', 0))
        total_ttc = safe_float(row.get('Total', 0))
        
        # Tentative de correspondance (3 méthodes dans l'ordre)
        correspondance = None
        
        # Méthode 1 : Tracking exact
        correspondance = correspondance_tracking_exact(tracking_retour, df_log)
        
        # Méthode 2 : Tracking partiel
        if not correspondance:
            correspondance = correspondance_tracking_partiel(tracking_retour, df_log)
        
        # Méthode 3 : CP + Date
        if not correspondance:
            correspondance = correspondance_cp_date(cp_retour, date_retour, df_log)
        
        # Résultat
        if correspondance:
            partenaire = correspondance['partenaire']
            commande = correspondance['commande']
            tracking_aller = correspondance['tracking_aller']
            methode = correspondance['methode']
        else:
            partenaire = 'NON IDENTIFIÉ'
            commande = ''
            tracking_aller = ''
            methode = 'Aucune'
        
        resultats.append({
            'Nom Partenaire': partenaire,
            'N° Commande': commande,
            'Tracking Aller': tracking_aller,
            'Tracking Retour': tracking_retour,
            'Date Retour': date_retour,
            'Code Postal': cp_retour,
            'Prix HT (€)': round(prix_ht, 2),
            'Majoration (€)': round(majoration, 2),
            'Total TTC (€)': round(total_ttc, 2),
            'Méthode Correspondance': methode
        })
    
    df_detail = pd.DataFrame(resultats)
    
    # 3. Statistiques
    stats = {
        'nb_retours': len(df_detail),
        'nb_identifies': (df_detail['Nom Partenaire'] != 'NON IDENTIFIÉ').sum(),
        'nb_non_identifies': (df_detail['Nom Partenaire'] == 'NON IDENTIFIÉ').sum(),
        'montant_total': df_detail['Total TTC (€)'].sum(),
        'nb_partenaires': df_detail[df_detail['Nom Partenaire'] != 'NON IDENTIFIÉ']['Nom Partenaire'].nunique()
    }
    
    return df_detail, stats

def run():
    """Point d'entrée du module Colissimo"""
    
    # Initialisation
    if 'colissimo_data_loaded' not in st.session_state:
        st.session_state.colissimo_data_loaded = False
    if 'colissimo_files_loaded' not in st.session_state:
        st.session_state.colissimo_files_loaded = False
    
    # 💾 CHARGEMENT AUTOMATIQUE
    if not st.session_state.colissimo_data_loaded:
        saved_data = persistence.load_module_data('colissimo')
        if saved_data:
            st.session_state.colissimo_detail = saved_data['detail']
            st.session_state.colissimo_stats = saved_data['stats']
            st.session_state.colissimo_timestamp = saved_data['timestamp']
            st.session_state.colissimo_data_loaded = True
    
    # En-tête
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("📮 Module Colissimo")
        st.markdown("**Gestion des Retours 8R** (v1.0)")
    with col2:
        if st.session_state.colissimo_data_loaded:
            if st.button("🗑️ Réinitialiser", type="secondary", key="colissimo_reset"):
                # Supprimer la sauvegarde
                persistence.delete_module_data('colissimo')
                # Effacer les données
                for key in list(st.session_state.keys()):
                    if key.startswith('colissimo_'):
                        del st.session_state[key]
                # Effacer fichiers partagés
                if 'shared_logisticiens' in st.session_state:
                    st.session_state.shared_logisticiens = {}
                st.success("✅ Module réinitialisé - toutes les sauvegardes supprimées")
                st.rerun()
    
    st.markdown("---")
    
    # Instructions
    with st.expander("📖 Instructions d'utilisation"):
        st.markdown("""
        ### 📋 Fichiers Requis
        
        **Facture Colissimo (CSV)** :
        - Séparateur : `;`
        - Filtrage automatique sur code produit `8R`
        - Colonnes : Tracking, Date PCH, Code Postal, Prix, Total
        
        **Logisticiens (3 fichiers Excel)** :
        - Fichiers logisticiens partagés (chargés sur la page d'accueil)
        - OU upload direct dans ce module (Mois 1, 2, 3)
        - Feuille : "Facturation préparation"
        - Colonnes : Nom du partenaire, Numéro de tracking, Date d'expédition, Code postal
        
        ### 🔍 Méthodes de Correspondance
        
        **Priorité 1** : Tracking exact  
        Correspondance directe du numéro de tracking
        
        **Priorité 2** : Tracking partiel  
        Recherche d'une séquence numérique commune (8+ chiffres)
        
        **Priorité 3** : Code postal + Date  
        Même code postal avec expédition antérieure au retour (la plus récente)
        """)
    
    st.markdown("### 📁 Import des Fichiers")
    
    # Gestion des données
    if not st.session_state.colissimo_data_loaded:
        
        # Chargement automatique depuis la bibliothèque logisticiens
        from modules.logisticiens_library import load_logisticien_files_for_analysis, get_all_available_periods
        
        log_files = load_logisticien_files_for_analysis(nb_months=3)
        
        # Upload des fichiers
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Facture Colissimo")
            csv_facture = st.file_uploader(
                "📄 CSV Facture Colissimo", 
                type=['csv'], 
                key="colissimo_csv",
                help="Fichier CSV avec séparateur ; contenant les retours 8R"
            )
        
        with col2:
            st.markdown("#### Fichiers Logisticiens")
            
            if len(log_files) >= 3:
                log1, log2, log3 = log_files[0], log_files[1], log_files[2]
                
                periods = get_all_available_periods()[:3]
                st.success(f"✅ {periods[0]['filename']}")
                st.success(f"✅ {periods[1]['filename']}")
                st.success(f"✅ {periods[2]['filename']}")
                
                st.info("📋 Chargés depuis Bibliothèque")
            elif len(log_files) > 0:
                st.warning(f"⚠️ {len(log_files)} fichier(s) seulement")
                st.info("Ajoutez-en dans **📋 Logisticiens**")
                log1 = log_files[0] if len(log_files) > 0 else None
                log2 = log_files[1] if len(log_files) > 1 else None
                log3 = log_files[2] if len(log_files) > 2 else None
            else:
                st.error("❌ Aucun fichier disponible")
                st.info("➡️ **📋 Logisticiens** pour ajouter")
                log1 = None
                log2 = None
                log3 = None
        
        # Bouton d'analyse
        st.markdown("---")
        
        has_facture = csv_facture is not None
        has_log = log1 is not None and log2 is not None and log3 is not None
        
        if has_facture and has_log:
            # Style CSS pour bouton vert
            st.markdown("""
                <style>
                div.stButton > button[kind="primary"] {
                    background-color: #10b981;
                    color: white;
                    font-weight: 700;
                    font-size: 18px;
                    padding: 20px;
                    border: none;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(16, 185, 129, 0.3);
                    transition: all 0.3s;
                }
                div.stButton > button[kind="primary"]:hover {
                    background-color: #059669;
                    box-shadow: 0 6px 12px rgba(16, 185, 129, 0.4);
                    transform: translateY(-2px);
                }
                </style>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 Lancer l'Analyse Colissimo", type="primary", use_container_width=True, key="colissimo_analyze"):
                with st.spinner("⏳ Analyse en cours..."):
                    try:
                        # Lecture fichiers
                        df_facture = read_csv_colissimo(csv_facture)
                        if df_facture is None:
                            st.error("❌ Erreur lecture CSV facture")
                            st.stop()
                        
                        df_log = fusion_logisticiens(log1, log2, log3)
                        if df_log is None:
                            st.error("❌ Erreur lecture fichiers logisticien")
                            st.stop()
                        
                        # Traitement
                        detail, stats = traiter_retours_colissimo(df_facture, df_log)
                        
                        if detail is None:
                            st.error("❌ Aucun retour 8R trouvé dans la facture")
                            st.stop()
                        
                        # Sauvegarde
                        st.session_state.colissimo_detail = detail
                        st.session_state.colissimo_stats = stats
                        st.session_state.colissimo_timestamp = datetime.now()
                        st.session_state.colissimo_data_loaded = True
                        
                        # 💾 SAUVEGARDE FICHIERS
                        files_to_save = {
                            'csv_facture': csv_facture,
                            'log1': log1,
                            'log2': log2,
                            'log3': log3
                        }
                        persistence.save_module_files('colissimo', files_to_save)
                        st.session_state.colissimo_files_loaded = True
                        
                        # 💾 SAUVEGARDE AUTOMATIQUE
                        persistence.save_module_data('colissimo', {
                            'detail': detail,
                            'stats': stats,
                            'timestamp': datetime.now()
                        })
                        
                        st.session_state.module_data['colissimo'] = {
                            'loaded': True,
                            'timestamp': datetime.now(),
                            'nb_retours': stats['nb_retours']
                        }
                        
                        # 📚 AUTO-ARCHIVAGE DANS LA BIBLIOTHÈQUE
                        success, year, month = persistence.auto_archive_analysis(
                            'Colissimo',
                            detail,
                            {
                                'detail': detail,
                                'stats': stats
                            }
                        )
                        
                        # Message avec info archivage
                        if success:
                            from modules.bibliotheque import get_month_name
                            st.success(f"✅ Analyse terminée et archivée ({get_month_name(month)} {year})")
                        else:
                            st.success("✅ Analyse terminée et sauvegardée !")
                        
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Erreur : {e}")
                        st.exception(e)
        else:
            st.warning("⚠️ Chargez la facture CSV et les 3 fichiers logisticien")
    
    # Affichage des résultats
    if st.session_state.colissimo_data_loaded:
        
        stats = st.session_state.colissimo_stats
        detail = st.session_state.colissimo_detail
        
        # Statistiques
        st.markdown("---")
        st.markdown("### 📊 Statistiques")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Retours", stats['nb_retours'])
        with col2:
            st.metric("Identifiés", stats['nb_identifies'])
        with col3:
            st.metric("Non identifiés", stats['nb_non_identifies'])
        with col4:
            st.metric("Montant Total", f"{stats['montant_total']:.2f} €")
        
        # Taux d'identification
        taux_ident = (stats['nb_identifies'] / stats['nb_retours'] * 100) if stats['nb_retours'] > 0 else 0
        if taux_ident >= 80:
            st.success(f"✅ Taux d'identification : **{taux_ident:.1f}%** - Excellent !")
        elif taux_ident >= 50:
            st.info(f"ℹ️ Taux d'identification : **{taux_ident:.1f}%** - Correct")
        else:
            st.warning(f"⚠️ Taux d'identification : **{taux_ident:.1f}%** - Amélioration possible")
        
        # Tableau détaillé
        st.markdown("---")
        st.markdown("### 📋 Détail des Retours")
        
        col1, col2 = st.columns(2)
        with col1:
            search = st.text_input("🔍 Rechercher", key="colissimo_search")
        with col2:
            partenaires = ['Tous'] + sorted(detail['Nom Partenaire'].unique().tolist())
            filter_part = st.selectbox("Partenaire", partenaires, key="colissimo_filter")
        
        detail_filt = detail.copy()
        if search:
            mask = (
                detail_filt['Nom Partenaire'].astype(str).str.contains(search, case=False, na=False) |
                detail_filt['Tracking Retour'].astype(str).str.contains(search, case=False, na=False)
            )
            detail_filt = detail_filt[mask]
        if filter_part != 'Tous':
            detail_filt = detail_filt[detail_filt['Nom Partenaire'] == filter_part]
        
        # Colorer les lignes selon l'identification
        def highlight_identification(row):
            if row['Nom Partenaire'] == 'NON IDENTIFIÉ':
                return ['background-color: #fee2e2'] * len(row)
            else:
                return ['background-color: #d1fae5'] * len(row)
        
        st.dataframe(
            detail_filt.style.apply(highlight_identification, axis=1),
            use_container_width=True,
            hide_index=True
        )
        
        st.info(f"📊 {len(detail_filt):,}/{len(detail):,} retours affichés")
        
        # Totaux
        st.markdown("**Totaux :**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Prix HT", f"{detail_filt['Prix HT (€)'].sum():.2f} €")
        with col2:
            st.metric("Majoration", f"{detail_filt['Majoration (€)'].sum():.2f} €")
        with col3:
            st.metric("Total TTC", f"{detail_filt['Total TTC (€)'].sum():.2f} €")
        
        # Export
        st.markdown("---")
        if st.button("📥 Exporter en Excel", key="colissimo_export"):
            excel = export_excel(detail_filt)
            st.download_button(
                "💾 Télécharger",
                excel,
                f"retours_colissimo_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="colissimo_dl"
            )
    
    else:
        st.info("👆 Importez vos fichiers pour commencer")
