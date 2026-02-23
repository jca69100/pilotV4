"""
Module : Analyse DPD par Partenaire
Version 2.1 - Streamlit - AVEC PERSISTANCE FICHIERS
Basé sur cahier des charges v1.5
"""

import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime
import pickle
from shared import persistence

def export_excel(dataframes_dict):
    """Export multiple DataFrames vers Excel avec plusieurs feuilles"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df in dataframes_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    return output.getvalue()

def convert_excel_date(value):
    """Convertit une date Excel numérique en string DD/MM/YYYY"""
    try:
        if pd.isna(value):
            return ""
        if isinstance(value, (int, float)):
            # Date Excel : nombre de jours depuis 1900-01-01
            base_date = datetime(1899, 12, 30)
            date = base_date + pd.Timedelta(days=int(value))
            return date.strftime('%d/%m/%Y')
        elif isinstance(value, str):
            # Déjà une chaîne
            return value
        else:
            # datetime
            return value.strftime('%d/%m/%Y')
    except:
        return str(value)

def safe_float(value):
    """Conversion sécurisée vers float"""
    try:
        if pd.isna(value):
            return 0.0
        return float(value)
    except:
        return 0.0

def clean_tracking_number(value):
    """Nettoie un numéro de tracking/DPD ID en enlevant les décimales"""
    try:
        if pd.isna(value) or value == '':
            return ''
        # Si c'est un nombre (int ou float), convertir en int puis string
        if isinstance(value, (int, float)):
            return str(int(value))
        # Si c'est déjà une string, la retourner telle quelle
        return str(value).strip()
    except:
        return str(value).strip() if value else ''

def read_excel_file(file, sheet_name=None):
    """Lecture d'un fichier Excel"""
    try:
        if sheet_name:
            df = pd.read_excel(file, sheet_name=sheet_name)
        else:
            # Lire la première feuille
            df = pd.read_excel(file)
        return df
    except Exception as e:
        st.error(f"Erreur lecture fichier : {e}")
        return None

def fusion_logisticiens(log_n, log_n1, log_n2):
    """Fusionne les 3 fichiers logisticien"""
    dfs = []
    
    for log_file in [log_n, log_n1, log_n2]:
        if log_file is not None:
            df = read_excel_file(log_file, sheet_name="Facturation préparation")
            if df is not None:
                # Nettoyer les numéros de tracking (enlever les décimales)
                if 'Numéro de tracking' in df.columns:
                    df['Numéro de tracking'] = df['Numéro de tracking'].apply(clean_tracking_number)
                dfs.append(df)
    
    if not dfs:
        return None
    
    # Fusion
    df_fusion = pd.concat(dfs, ignore_index=True)
    
    # Filtrer sur DPD
    if 'Transporteur' in df_fusion.columns:
        df_fusion = df_fusion[df_fusion['Transporteur'].str.upper() == 'DPD'].copy()
    
    return df_fusion

def fusion_dpd(dpd_predict, dpd_classic):
    """Fusionne les 2 fichiers DPD"""
    dfs = []
    
    for dpd_file in [dpd_predict, dpd_classic]:
        if dpd_file is not None:
            df = read_excel_file(dpd_file)
            if df is not None:
                # Nettoyer les DPD ID (enlever les décimales)
                if 'DPD ID' in df.columns:
                    df['DPD ID'] = df['DPD ID'].apply(clean_tracking_number)
                dfs.append(df)
    
    if not dfs:
        return None
    
    # Fusion
    df_fusion = pd.concat(dfs, ignore_index=True)
    return df_fusion

def croisement_donnees(df_logisticien, df_dpd):
    """Croise les données logisticien et DPD"""
    
    # Création des mappings depuis logisticien
    mapping_partner = {}
    mapping_commande = {}
    
    if df_logisticien is not None:
        for _, row in df_logisticien.iterrows():
            # Nettoyer le numéro de tracking (sans décimales)
            tracking = clean_tracking_number(row.get('Numéro de tracking', ''))
            if tracking:
                mapping_partner[tracking] = row.get('Nom du partenaire', 'NON ATTRIBUÉ')
                mapping_commande[tracking] = str(row.get('Numéro de commande d\'origine', ''))
    
    # Debug: afficher quelques mappings pour vérifier
    if mapping_partner:
        st.sidebar.write("🔍 Debug Mapping (premiers 5):")
        for i, (k, v) in enumerate(list(mapping_partner.items())[:5]):
            st.sidebar.write(f"  {k} → {v}")
    
    # Enrichissement des données DPD
    results = []
    
    for _, row in df_dpd.iterrows():
        # Nettoyer le DPD ID (sans décimales)
        dpd_id = clean_tracking_number(row.get('DPD ID', ''))
        
        # Attribution partenaire et commande
        partner = mapping_partner.get(dpd_id, 'NON ATTRIBUÉ')
        commande = mapping_commande.get(dpd_id, '')
        
        # Lecture des valeurs
        prix_transport = safe_float(row.get('Prix transport', 0))
        supplement_ile = safe_float(row.get('Supplément île et montagne', 0))
        nb_retours = safe_float(row.get('Nombre Retour expédition', 0))
        cout_retours = safe_float(row.get('Fact. Retour expédition', 0))
        
        # Lecture automatique des taxes (v1.5)
        taxe_fuel = safe_float(row.get('Indexation gasoil', 0))
        participation_surete = safe_float(row.get('Participation Sureté', 0))
        contribution_logistique = safe_float(row.get('Contribution Logistique Responsable', 0))
        
        # Calcul taxe sûreté totale
        taxe_surete = participation_surete + contribution_logistique
        
        # Calculs
        montant_base = supplement_ile + cout_retours
        total_avec_taxes = montant_base + taxe_fuel + taxe_surete
        prix_total_ligne = prix_transport + supplement_ile + cout_retours + taxe_fuel + taxe_surete
        
        # Ligne enrichie
        results.append({
            'Partenaire': partner,
            'N° Commande': commande,
            'DPD ID': dpd_id,
            'N° Colis': row.get('N° Colis', ''),
            'Date expédition': convert_excel_date(row.get('Date expédition', '')),
            'Nom destinataire': row.get('Nom destinataire', ''),
            'Ville destinataire': row.get('Ville destinataire', ''),
            'CP destinataire': row.get('CP destinataire', ''),
            'Pays destinataire': row.get('Code pays destinataire', ''),
            'Prix transport': prix_transport,
            'Supplément île': supplement_ile,
            'Nb retours': nb_retours,
            'Coût retours': cout_retours,
            'Taxe Fuel': taxe_fuel,
            'Taxe Sûreté': taxe_surete,
            'Total avec taxes': total_avec_taxes,
            'Prix total ligne': prix_total_ligne
        })
    
    return pd.DataFrame(results)

def calculer_synthese(df_detail):
    """Calcule la synthèse par partenaire"""
    
    synthese = df_detail.groupby('Partenaire').agg({
        'DPD ID': 'count',
        'Prix transport': 'sum',
        'Supplément île': 'sum',
        'Nb retours': 'sum',
        'Coût retours': 'sum',
        'Taxe Fuel': 'sum',
        'Taxe Sûreté': 'sum',
        'Total avec taxes': 'sum',
        'Prix total ligne': 'sum'
    }).reset_index()
    
    synthese.columns = [
        'Partenaire',
        'Nb Expéditions',
        'Prix Transport',
        'Suppléments Île',
        'Nb Retours',
        'Coût Retours',
        'Taxe Fuel',
        'Taxe Sûreté',
        'Total avec Taxes',
        'Prix Total Ligne'
    ]
    
    # Tri par prix total ligne décroissant
    synthese = synthese.sort_values('Prix Total Ligne', ascending=False)
    
    return synthese

def extraire_supplements(df_detail):
    """Extrait les lignes avec suppléments île"""
    df_supp = df_detail[df_detail['Supplément île'] > 0].copy()
    return df_supp[[
        'Partenaire', 'N° Commande', 'DPD ID', 'Date expédition',
        'Ville destinataire', 'CP destinataire', 'Pays destinataire',
        'Supplément île', 'Taxe Fuel', 'Taxe Sûreté', 'Prix total ligne'
    ]].sort_values('Prix total ligne', ascending=False)

def extraire_retours(df_detail):
    """Extrait les lignes avec retours"""
    df_ret = df_detail[df_detail['Nb retours'] > 0].copy()
    return df_ret[[
        'Partenaire', 'N° Commande', 'DPD ID', 'Date expédition',
        'Nb retours', 'Coût retours', 'Taxe Fuel', 'Taxe Sûreté', 'Prix total ligne'
    ]].sort_values('Prix total ligne', ascending=False)

# Suite dans la partie 2...

def save_session():
    """Sauvegarde la session du module DPD"""
    if st.session_state.get('dpd_data_loaded', False):
        session_data = {
            'synthese': st.session_state.dpd_synthese,
            'detail': st.session_state.dpd_detail,
            'supplements': st.session_state.dpd_supplements,
            'retours': st.session_state.dpd_retours,
            'stats': st.session_state.dpd_stats,
            'timestamp': datetime.now()
        }
        return pickle.dumps(session_data)
    return None

def load_session(session_file):
    """Charge une session sauvegardée"""
    try:
        data = pickle.load(session_file)
        st.session_state.dpd_synthese = data['synthese']
        st.session_state.dpd_detail = data['detail']
        st.session_state.dpd_supplements = data['supplements']
        st.session_state.dpd_retours = data['retours']
        st.session_state.dpd_stats = data['stats']
        st.session_state.dpd_timestamp = data['timestamp']
        st.session_state.dpd_data_loaded = True
        return True
    except:
        return False

def run():
    """Point d'entrée du module DPD"""
    
    # Initialisation
    if 'dpd_data_loaded' not in st.session_state:
        st.session_state.dpd_data_loaded = False
    if 'dpd_files_loaded' not in st.session_state:
        st.session_state.dpd_files_loaded = False
    
    # 💾 CHARGEMENT AUTOMATIQUE au premier accès
    if not st.session_state.dpd_data_loaded:
        saved_data = persistence.load_module_data('dpd')
        if saved_data:
            st.session_state.dpd_synthese = saved_data['synthese']
            st.session_state.dpd_detail = saved_data['detail']
            st.session_state.dpd_supplements = saved_data['supplements']
            st.session_state.dpd_retours = saved_data['retours']
            st.session_state.dpd_stats = saved_data['stats']
            st.session_state.dpd_timestamp = saved_data['timestamp']
            st.session_state.dpd_data_loaded = True
    
    # Chargement automatique des fichiers uploadés
    if not st.session_state.dpd_files_loaded:
        saved_files = persistence.load_module_files('dpd')
        if saved_files:
            if 'log_n' in saved_files:
                st.session_state.dpd_log_n = saved_files['log_n']
            if 'log_n1' in saved_files:
                st.session_state.dpd_log_n1 = saved_files['log_n1']
            if 'log_n2' in saved_files:
                st.session_state.dpd_log_n2 = saved_files['log_n2']
            if 'dpd_predict' in saved_files:
                st.session_state.dpd_predict = saved_files['dpd_predict']
            if 'dpd_classic' in saved_files:
                st.session_state.dpd_classic = saved_files['dpd_classic']
            st.session_state.dpd_files_loaded = True
    
    # En-tête
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("📊 Module Analyse DPD")
        st.markdown("**Analyse par Partenaire avec Taxes Automatiques** (v1.5)")
    with col2:
        if st.session_state.dpd_data_loaded:
            if st.button("🗑️ Réinitialiser", type="secondary", key="dpd_reset"):
                # Supprimer la sauvegarde
                persistence.delete_module_data('dpd')
                # Effacer les données du module DPD
                for key in list(st.session_state.keys()):
                    if key.startswith('dpd_'):
                        del st.session_state[key]
                # Effacer aussi les fichiers partagés
                if 'shared_logisticiens' in st.session_state:
                    st.session_state.shared_logisticiens = {}
                # Effacer module_data
                if 'module_data' in st.session_state and 'dpd' in st.session_state.module_data:
                    del st.session_state.module_data['dpd']
                st.success("✅ Module réinitialisé - toutes les sauvegardes supprimées")
                st.rerun()
    
    st.markdown("---")
    
    # Instructions
    with st.expander("📖 Instructions d'utilisation"):
        st.markdown("""
        ### 📋 Fichiers Requis
        
        **Logisticiens (3 fichiers)** :
        - Mois N, N-1, N-2
        - Feuille : "Facturation préparation"
        - Colonnes : Nom du partenaire, Transporteur, Numéro de tracking, Numéro de commande d'origine
        
        **DPD (2 fichiers)** :
        - DPD Predict + DPD Classic
        - Colonnes : DPD ID, Prix transport, Suppléments, Retours, **Indexation gasoil, Participation Sureté, Contribution Logistique**
        
        ### ⚡ Nouveautés v1.5
        - ✅ **Lecture automatique des taxes** depuis les fichiers DPD
        - ✅ **Taxe Fuel** : colonne "Indexation gasoil"
        - ✅ **Taxe Sûreté** : somme "Participation Sureté" + "Contribution Logistique Responsable"
        - ✅ **Prix total ligne** : calcul complet (transport + suppléments + retours + taxes)
        
        ### 💡 Astuce
        Si vous avez déjà chargé les fichiers logisticiens dans la page d'accueil, ils seront automatiquement utilisés !
        """)
    
    st.markdown("### 📁 Import des Fichiers")
    
    # Gestion des données
    if not st.session_state.dpd_data_loaded:
        
        # Chargement automatique depuis la bibliothèque logisticiens
        from modules.logisticiens_library import load_logisticien_files_for_analysis, get_all_available_periods
        
        log_files = load_logisticien_files_for_analysis(nb_months=3)
        
        # Upload des fichiers
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### Fichiers Logisticiens")
            
            if len(log_files) >= 3:
                log_n, log_n1, log_n2 = log_files[0], log_files[1], log_files[2]
                
                # Afficher les fichiers chargés
                periods = get_all_available_periods()[:3]
                st.success(f"✅ {periods[0]['filename']}")
                st.success(f"✅ {periods[1]['filename']}")
                st.success(f"✅ {periods[2]['filename']}")
                
                st.info("📋 Chargés depuis Bibliothèque")
            elif len(log_files) > 0:
                st.warning(f"⚠️ {len(log_files)} fichier(s) seulement")
                st.info("Ajoutez-en dans **📋 Logisticiens**")
                log_n = log_files[0] if len(log_files) > 0 else None
                log_n1 = log_files[1] if len(log_files) > 1 else None
                log_n2 = log_files[2] if len(log_files) > 2 else None
            else:
                st.error("❌ Aucun fichier disponible")
                st.info("➡️ **📋 Logisticiens** pour ajouter")
                log_n = None
                log_n1 = None
                log_n2 = None
        
        with col2:
            st.markdown("#### Fichiers DPD")
            dpd_predict = st.file_uploader("DPD Predict", type=['xlsx', 'xls'], key="dpd_predict")
            dpd_classic = st.file_uploader("DPD Classic", type=['xlsx', 'xls'], key="dpd_classic")
        
        with col3:
            st.markdown("#### Session")
            session_file = st.file_uploader("📂 Recharger session", type=['pkl'], key="dpd_session")
            if session_file:
                if load_session(session_file):
                    st.success("✅ Session rechargée")
                    st.rerun()
                else:
                    st.error("❌ Erreur")
        
        # Bouton d'analyse
        st.markdown("---")
        
        has_log = log_n is not None and log_n1 is not None and log_n2 is not None
        has_dpd = dpd_predict is not None and dpd_classic is not None
        
        if has_log and has_dpd:
            # Style CSS pour bouton vert personnalisé
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
            
            if st.button("🚀 Lancer l'Analyse DPD", type="primary", use_container_width=True, key="dpd_analyze"):
                with st.spinner("⏳ Analyse en cours..."):
                    try:
                        # Fusion logisticiens
                        df_log = fusion_logisticiens(log_n, log_n1, log_n2)
                        if df_log is None:
                            st.error("❌ Erreur fusion logisticiens")
                            st.stop()
                        
                        # Fusion DPD
                        df_dpd = fusion_dpd(dpd_predict, dpd_classic)
                        if df_dpd is None:
                            st.error("❌ Erreur fusion DPD")
                            st.stop()
                        
                        # Croisement
                        df_detail = croisement_donnees(df_log, df_dpd)
                        
                        # Calculs
                        df_synthese = calculer_synthese(df_detail)
                        df_supplements = extraire_supplements(df_detail)
                        df_retours = extraire_retours(df_detail)
                        
                        # Stats
                        stats = {
                            'nb_expeditions': len(df_detail),
                            'nb_partenaires': df_detail['Partenaire'].nunique(),
                            'prix_total': df_synthese['Prix Total Ligne'].sum(),
                            'nb_supplements': len(df_supplements),
                            'nb_retours': len(df_retours),
                            'taux_non_attribue': (df_detail['Partenaire'] == 'NON ATTRIBUÉ').sum() / len(df_detail) * 100
                        }
                        
                        # Sauvegarde
                        st.session_state.dpd_synthese = df_synthese
                        st.session_state.dpd_detail = df_detail
                        st.session_state.dpd_supplements = df_supplements
                        st.session_state.dpd_retours = df_retours
                        st.session_state.dpd_stats = stats
                        st.session_state.dpd_timestamp = datetime.now()
                        st.session_state.dpd_data_loaded = True
                        
                        # 💾 SAUVEGARDE AUTOMATIQUE DES FICHIERS
                        files_to_save = {}
                        if log_n is not None: files_to_save['log_n'] = log_n
                        if log_n1 is not None: files_to_save['log_n1'] = log_n1
                        if log_n2 is not None: files_to_save['log_n2'] = log_n2
                        if dpd_predict is not None: files_to_save['dpd_predict'] = dpd_predict
                        if dpd_classic is not None: files_to_save['dpd_classic'] = dpd_classic
                        persistence.save_module_files('dpd', files_to_save)
                        st.session_state.dpd_files_loaded = True
                        
                        # 💾 SAUVEGARDE AUTOMATIQUE
                        persistence.save_module_data('dpd', {
                            'synthese': df_synthese,
                            'detail': df_detail,
                            'supplements': df_supplements,
                            'retours': df_retours,
                            'stats': stats,
                            'timestamp': datetime.now()
                        })
                        
                        # Sauvegarder dans module_data global
                        st.session_state.module_data['dpd'] = {
                            'loaded': True,
                            'timestamp': datetime.now(),
                            'nb_expeditions': stats['nb_expeditions']
                        }
                        
                        # 📚 AUTO-ARCHIVAGE DANS LA BIBLIOTHÈQUE
                        success, year, month = persistence.auto_archive_analysis(
                            'DPD',
                            df_detail,
                            {
                                'synthese': df_synthese,
                                'detail': df_detail,
                                'supplements': df_supplements,
                                'retours': df_retours,
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
            st.warning("⚠️ Chargez les 5 fichiers pour lancer l'analyse")
    
    # Affichage des résultats
    if st.session_state.dpd_data_loaded:
        
        stats = st.session_state.dpd_stats
        
        # Export session
        col1, col2 = st.columns([3, 1])
        with col1:
            st.success(f"✅ Analyse chargée - {stats['nb_expeditions']} expéditions")
        with col2:
            if st.button("📥 Sauvegarder"):
                session_bytes = save_session()
                if session_bytes:
                    st.download_button(
                        "💾 Télécharger",
                        session_bytes,
                        f"dpd_session_{datetime.now().strftime('%Y%m%d_%H%M')}.pkl",
                        "application/octet-stream",
                        key="dpd_dl_session"
                    )
        
        # Statistiques
        st.markdown("---")
        st.markdown("### 📊 Statistiques Globales")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Expéditions", f"{stats['nb_expeditions']:,}")
        with col2:
            st.metric("Partenaires", stats['nb_partenaires'])
        with col3:
            st.metric("Prix Total", f"{stats['prix_total']:,.2f} €")
        with col4:
            st.metric("Non attribué", f"{stats['taux_non_attribue']:.1f}%")
        
        # Onglets
        st.markdown("---")
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Synthèse", 
            "📋 Détail", 
            "🏝️ Suppléments Île", 
            "↩️ Retours"
        ])
        
        with tab1:
            st.markdown("### Synthèse par Partenaire")
            
            # Filtre
            search = st.text_input("🔍 Rechercher partenaire", key="dpd_search_syn")
            
            synthese = st.session_state.dpd_synthese
            if search:
                synthese = synthese[synthese['Partenaire'].str.contains(search, case=False, na=False)]
            
            # Formattage pour affichage
            synthese_display = synthese.copy()
            for col in ['Prix Transport', 'Suppléments Île', 'Coût Retours', 'Taxe Fuel', 'Taxe Sûreté', 'Total avec Taxes', 'Prix Total Ligne']:
                synthese_display[col] = synthese_display[col].apply(lambda x: f"{x:.2f} €")
            
            st.dataframe(synthese_display, use_container_width=True, hide_index=True)
            
            # Export
            if st.button("📥 Exporter Synthèse", key="dpd_exp_syn"):
                excel = export_excel({'Synthèse': synthese})
                st.download_button(
                    "💾 Télécharger",
                    excel,
                    f"dpd_synthese_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dpd_dl_syn"
                )
        
        with tab2:
            st.markdown("### Détail des Expéditions")
            
            col1, col2 = st.columns(2)
            with col1:
                search_det = st.text_input("🔍 Rechercher", key="dpd_search_det")
            with col2:
                detail = st.session_state.dpd_detail
                partenaires = ['Tous'] + sorted(detail['Partenaire'].unique().tolist())
                filter_part = st.selectbox("Partenaire", partenaires, key="dpd_filter")
            
            detail_filt = detail.copy()
            if search_det:
                mask = (
                    detail_filt['Partenaire'].astype(str).str.contains(search_det, case=False, na=False) |
                    detail_filt['DPD ID'].astype(str).str.contains(search_det, case=False, na=False)
                )
                detail_filt = detail_filt[mask]
            if filter_part != 'Tous':
                detail_filt = detail_filt[detail_filt['Partenaire'] == filter_part]
            
            st.dataframe(detail_filt, use_container_width=True, hide_index=True)
            st.info(f"📊 {len(detail_filt):,}/{len(detail):,} expéditions")
            
            if st.button("📥 Exporter Détail", key="dpd_exp_det"):
                excel = export_excel({'Détail': detail_filt})
                st.download_button(
                    "💾 Télécharger",
                    excel,
                    f"dpd_detail_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dpd_dl_det"
                )
        
        with tab3:
            st.markdown("### Suppléments Île et Montagne")
            st.info(f"🏝️ {len(st.session_state.dpd_supplements)} expéditions avec suppléments")
            
            supplements = st.session_state.dpd_supplements
            st.dataframe(supplements, use_container_width=True, hide_index=True)
            
            if st.button("📥 Exporter Suppléments", key="dpd_exp_supp"):
                excel = export_excel({'Suppléments': supplements})
                st.download_button(
                    "💾 Télécharger",
                    excel,
                    f"dpd_supplements_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dpd_dl_supp"
                )
        
        with tab4:
            st.markdown("### Retours")
            st.info(f"↩️ {len(st.session_state.dpd_retours)} expéditions avec retours")
            
            retours = st.session_state.dpd_retours
            st.dataframe(retours, use_container_width=True, hide_index=True)
            
            if st.button("📥 Exporter Retours", key="dpd_exp_ret"):
                excel = export_excel({'Retours': retours})
                st.download_button(
                    "💾 Télécharger",
                    excel,
                    f"dpd_retours_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dpd_dl_ret"
                )
    
    else:
        st.info("👆 Chargez les fichiers ou une session pour commencer")

