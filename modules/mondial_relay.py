"""
Module : Mondial Relay - Gestion des Retours
Version 2.2 - Streamlit - AVEC PERSISTANCE FICHIERS
Calcul avec Majoration de Service (au lieu de Taxe Fuel manuelle)
"""

import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime
import re
from shared import persistence

def export_excel(dataframes_dict):
    """Export multiple DataFrames vers Excel avec plusieurs feuilles"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df in dataframes_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    return output.getvalue()

def convert_european_to_float(value):
    """Convertit un montant européen (virgule) en float"""
    try:
        if pd.isna(value) or value == '':
            return 0.0
        # Si c'est déjà un nombre
        if isinstance(value, (int, float)):
            return float(value)
        # Si c'est une string
        value_str = str(value).strip()
        # Remplacer virgule par point
        value_str = value_str.replace(',', '.')
        # Enlever les espaces
        value_str = value_str.replace(' ', '')
        return float(value_str)
    except:
        return 0.0

def clean_numero_colis(value):
    """Nettoie un numéro de colis"""
    try:
        if pd.isna(value) or value == '':
            return ''
        if isinstance(value, (int, float)):
            return str(int(value))
        return str(value).strip()
    except:
        return str(value).strip() if value else ''

def read_csv_retours(file):
    """Lit le fichier CSV des retours Mondial Relay"""
    try:
        # Lecture avec détection de l'encodage
        df = pd.read_csv(file, sep=';', encoding='utf-8-sig')
        return df
    except:
        try:
            file.seek(0)
            df = pd.read_csv(file, sep=';', encoding='latin-1')
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

def traiter_retours_mondial_relay(df_retours, list_df_log):
    """
    Traite les retours Mondial Relay
    
    Args:
        df_retours: DataFrame des retours CSV
        list_df_log: Liste de DataFrames logisticien (peut en avoir 1, 2, 3 ou plus)
    """
    
    # 1. Filtrer sur TOOPOST
    df_retours_filtered = df_retours[
        df_retours['Nom'].str.upper() == 'TOOPOST'
    ].copy()
    
    if len(df_retours_filtered) == 0:
        return None, None, None
    
    # 2. Supprimer les doublons sur Référence client
    df_retours_filtered = df_retours_filtered.drop_duplicates(
        subset=['Reférence client'], 
        keep='first'
    )
    
    # 2b. Nettoyer les noms de colonnes (enlever espaces début/fin)
    df_retours_filtered.columns = df_retours_filtered.columns.str.strip()
    
    # 3. Convertir les montants (virgule → point)
    df_retours_filtered['Montant_Base'] = df_retours_filtered['Prix'].apply(
        convert_european_to_float
    )
    
    # 3b. Lire la Majoration de service depuis le CSV
    # Chercher la colonne de manière flexible
    majoration_col = None
    
    # Liste des noms possibles pour la colonne majoration
    possible_names = [
        'Majoration de service',
        'majoration de service',
        'Majoration',
        'majoration',
        'Majoration service',
        'majoration service'
    ]
    
    for col_name in df_retours_filtered.columns:
        col_clean = col_name.strip().lower()
        for possible in possible_names:
            if possible.lower() in col_clean or col_clean in possible.lower():
                majoration_col = col_name
                break
        if majoration_col:
            break
    
    if majoration_col:
        df_retours_filtered['Majoration_Service'] = df_retours_filtered[majoration_col].apply(
            convert_european_to_float
        )
        st.success(f"✅ Colonne de majoration détectée : '{majoration_col}'")
    else:
        st.warning("⚠️ Colonne 'Majoration de service' non trouvée - Utilisation de 0€")
        st.info(f"💡 Colonnes disponibles dans le CSV : {', '.join(df_retours_filtered.columns.tolist())}")
        df_retours_filtered['Majoration_Service'] = 0.0
    
    # 4. Nettoyer les numéros de colis
    df_retours_filtered['Ref_Client_Clean'] = df_retours_filtered['Reférence client'].apply(
        clean_numero_colis
    )
    
    # 5. Fusion de TOUS les fichiers logisticien
    dfs_log = []
    for idx, df_log in enumerate(list_df_log, 1):
        if df_log is not None:
            # Nettoyer les numéros de colis
            if 'Numéro de colis' in df_log.columns:
                df_log['Numero_Colis_Clean'] = df_log['Numéro de colis'].apply(
                    clean_numero_colis
                )
            # Nettoyer aussi le numéro de tracking
            if 'Numéro de tracking' in df_log.columns:
                df_log['Tracking_Clean'] = df_log['Numéro de tracking'].apply(
                    clean_numero_colis
                )
            # Nettoyer le numéro de commande d'origine
            if "Numéro de commande d'origine" in df_log.columns:
                df_log['Commande_Clean'] = df_log["Numéro de commande d'origine"].apply(
                    clean_numero_colis
                )
            dfs_log.append(df_log)
            st.info(f"✅ Fichier logisticien {idx} chargé : {len(df_log)} lignes")
    
    if not dfs_log:
        st.error("Aucun fichier logisticien valide")
        return None, None, None
    
    df_logisticien = pd.concat(dfs_log, ignore_index=True)
    st.success(f"📊 Total : {len(df_logisticien)} lignes logisticien chargées depuis {len(dfs_log)} fichier(s)")
    
    # 6. Créer des mappings multiples pour améliorer les correspondances
    mapping_partner = {}
    mapping_commande = {}
    mapping_tracking_aller = {}
    
    for _, row in df_logisticien.iterrows():
        partner = row.get('Nom du partenaire', 'Non attribué')
        commande = str(row.get('Numéro de commande d\'origine', ''))
        tracking = str(row.get('Numéro de tracking', ''))
        
        # Mapping par numéro de colis
        numero_colis = row.get('Numero_Colis_Clean', '')
        if numero_colis:
            mapping_partner[numero_colis] = partner
            mapping_commande[numero_colis] = commande
            mapping_tracking_aller[numero_colis] = tracking
        
        # Mapping par tracking (tentative alternative)
        tracking_clean = row.get('Tracking_Clean', '')
        if tracking_clean:
            mapping_partner[tracking_clean] = partner
            mapping_commande[tracking_clean] = commande
            mapping_tracking_aller[tracking_clean] = tracking
        
        # Mapping par commande (tentative alternative)
        commande_clean = row.get('Commande_Clean', '')
        if commande_clean:
            mapping_partner[commande_clean] = partner
            mapping_commande[commande_clean] = commande
            mapping_tracking_aller[commande_clean] = tracking
    
    # 7. Enrichir les retours avec recherche multiple
    resultats = []
    non_identifies = 0
    
    for _, row in df_retours_filtered.iterrows():
        ref_client = row['Ref_Client_Clean']
        
        # Tentative 1: Par référence client
        partner = mapping_partner.get(ref_client)
        commande = mapping_commande.get(ref_client, '')
        tracking_aller = mapping_tracking_aller.get(ref_client, '')
        
        # Si pas trouvé, essayer avec le tracking retour
        if not partner or partner == 'Non attribué':
            tracking_retour = clean_numero_colis(row.get('Tracking', ''))
            if tracking_retour:
                partner = mapping_partner.get(tracking_retour, partner)
                if partner and partner != 'Non attribué':
                    commande = mapping_commande.get(tracking_retour, commande)
                    tracking_aller = mapping_tracking_aller.get(tracking_retour, tracking_aller)
        
        # Par défaut si toujours pas trouvé
        if not partner:
            partner = 'Non attribué'
            non_identifies += 1
        
        # Montants
        montant_base = row['Montant_Base']
        majoration_service = row['Majoration_Service']
        
        # Montant total = Prix + Majoration de service
        montant_total = montant_base + majoration_service
        
        resultats.append({
            'Partenaire': partner,
            'Tracking Retour': row.get('Tracking', ''),
            'Tracking Aller': tracking_aller,
            'N° Colis': ref_client,
            'N° Commande Origine': commande,
            'Date PCH': row.get('Date PCH', ''),
            'Poids Facturé': row.get('Poids facturé', 0),
            'Montant Base (€)': round(montant_base, 2),
            'Majoration Service (€)': round(majoration_service, 2),
            'Montant Total (€)': round(montant_total, 2),
            'Statut': '✓ Identifié' if partner != 'Non attribué' else '⚠ Non identifié'
        })
    
    df_detail = pd.DataFrame(resultats)
    
    # Afficher les statistiques de correspondance
    total_lignes = len(df_detail)
    lignes_identifiees = len(df_detail[df_detail['Partenaire'] != 'Non attribué'])
    taux_correspondance = (lignes_identifiees / total_lignes * 100) if total_lignes > 0 else 0
    
    st.info(f"""
    📊 **Statistiques de correspondance:**
    - Total de retours TOOPOST : {total_lignes}
    - Retours identifiés : {lignes_identifiees} ({taux_correspondance:.1f}%)
    - Retours non identifiés : {non_identifies} ({100-taux_correspondance:.1f}%)
    """)
    
    if non_identifies > 0:
        st.warning(f"""
        ⚠️ **{non_identifies} retour(s) n'ont pas pu être attribués à un partenaire**
        
        **Causes possibles:**
        - La "Référence client" dans le fichier Mondial Relay ne correspond à aucun "Numéro de colis", 
          "Numéro de tracking" ou "Numéro de commande" dans vos fichiers logisticien
        - Les fichiers logisticien ne contiennent pas ces envois (peut-être d'une période différente)
        
        **Solutions:**
        - Vérifiez que vous avez uploadé les bons fichiers logisticien pour la période concernée
        - Vérifiez le format des références dans le fichier Mondial Relay
        """)
    
    # 8. Synthèse par partenaire
    synthese = df_detail.groupby('Partenaire').agg({
        'N° Colis': 'count',
        'Montant Base (€)': 'sum',
        'Majoration Service (€)': 'sum',
        'Montant Total (€)': 'sum'
    }).reset_index()
    
    synthese.columns = [
        'Partenaire',
        'Nb Retours',
        'Montant Base (€)',
        'Majoration Service (€)',
        'Montant Total (€)'
    ]
    
    # Arrondir
    for col in ['Montant Base (€)', 'Majoration Service (€)', 'Montant Total (€)']:
        synthese[col] = synthese[col].round(2)
    
    # Trier par montant total décroissant
    synthese = synthese.sort_values('Montant Total (€)', ascending=False)
    
    # 9. Statistiques
    stats = {
        'nb_retours': len(df_detail),
        'nb_partenaires': df_detail['Partenaire'].nunique(),
        'montant_base_total': df_detail['Montant Base (€)'].sum(),
        'majoration_service_total': df_detail['Majoration Service (€)'].sum(),
        'montant_total': df_detail['Montant Total (€)'].sum(),
        'nb_identifies': (df_detail['Statut'] == '✓ Identifié').sum(),
        'nb_non_identifies': (df_detail['Statut'] == '⚠ Non identifié').sum()
    }
    
    return synthese, df_detail, stats

def run():
    """Point d'entrée du module Mondial Relay"""
    
    # Initialisation
    if 'mr_data_loaded' not in st.session_state:
        st.session_state.mr_data_loaded = False
    if 'mr_files_loaded' not in st.session_state:
        st.session_state.mr_files_loaded = False
    
    # 💾 CHARGEMENT AUTOMATIQUE
    if not st.session_state.mr_data_loaded:
        saved_data = persistence.load_module_data('mondial_relay')
        if saved_data:
            st.session_state.mr_synthese = saved_data['synthese']
            st.session_state.mr_detail = saved_data['detail']
            st.session_state.mr_stats = saved_data['stats']
            st.session_state.mr_timestamp = saved_data['timestamp']
            st.session_state.mr_data_loaded = True
    
    # En-tête
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("🌍 Module Mondial Relay")
        st.markdown("**Gestion des Retours TOOPOST** (v2.2 - Avec Majoration de Service)")
    with col2:
        if st.session_state.mr_data_loaded:
            if st.button("🗑️ Réinitialiser", type="secondary", key="mr_reset"):
                # Supprimer la sauvegarde
                persistence.delete_module_data('mondial_relay')
                # Effacer les données
                for key in list(st.session_state.keys()):
                    if key.startswith('mr_'):
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
        
        **Retours Mondial Relay (CSV)** :
        - Fichier CSV avec séparateur `;`
        - Filtrage automatique sur `Nom = "TOOPOST"`
        - Conversion automatique virgule → point pour les montants
        - Lecture automatique de la colonne "Majoration de service"
        
        **Logisticiens (1 ou plusieurs fichiers Excel)** :
        - Fichiers logisticiens partagés (chargés sur la page d'accueil) - **TOUS utilisés automatiquement**
        - OU upload direct dans ce module (1 seul fichier)
        - Feuille : "Facturation préparation"
        - Colonnes : Nom du partenaire, Numéro de colis, Numéro de tracking
        
        ### 💡 Fonctionnalités
        - ✅ Suppression automatique des doublons
        - ✅ Correspondance via Numéro de colis
        - ✅ Lecture de la majoration de service depuis le CSV
        - ✅ Calcul automatique : Montant Total = Prix + Majoration de service
        - ✅ Export Excel avec synthèse + détails
        - ✅ Sauvegarde automatique
        """)
    
    st.markdown("### 📁 Import des Fichiers")
    
    # Gestion des données
    if not st.session_state.mr_data_loaded:
        
        # Chargement automatique depuis la bibliothèque logisticiens
        from modules.logisticiens_library import load_logisticien_files_for_analysis, get_all_available_periods
        
        log_files = load_logisticien_files_for_analysis(nb_months=3)
        
        # Upload des fichiers
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Fichier Retours")
            csv_retours = st.file_uploader(
                "📄 CSV Retours Mondial Relay", 
                type=['csv'], 
                key="mr_csv_retours",
                help="Fichier CSV avec séparateur ; et montants avec virgule"
            )
        
        with col2:
            st.markdown("#### Fichiers Logisticiens")
            
            if len(log_files) > 0:
                st.success(f"✅ {len(log_files)} fichier(s) chargé(s) :")
                periods = get_all_available_periods()[:len(log_files)]
                for period in periods:
                    st.caption(f"• {period['filename']}")
                st.info("📋 Depuis Bibliothèque Logisticiens")
            else:
                st.error("❌ Aucun fichier logisticien")
                st.info("➡️ **📋 Logisticiens** pour ajouter")
        
        # Bouton d'analyse
        st.markdown("---")
        
        has_retours = csv_retours is not None
        has_log = len(log_files) > 0
        
        if not has_retours:
            st.info("📤 Uploadez un fichier CSV Retours Mondial Relay pour commencer")
        elif not has_log:
            st.warning("⚠️ Uploadez un fichier logisticien ou chargez-les depuis la page d'accueil")
        
        if has_retours and has_log:
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
            
            if st.button("🚀 Lancer l'Analyse Mondial Relay", type="primary", use_container_width=True, key="mr_analyze"):
                with st.spinner("⏳ Analyse en cours..."):
                    try:
                        # Lecture fichier retours
                        df_retours = read_csv_retours(csv_retours)
                        if df_retours is None:
                            st.error("❌ Erreur lecture CSV retours")
                            st.stop()
                        
                        # Lecture de TOUS les fichiers logisticien
                        list_df_log = []
                        for idx, log_file in enumerate(log_files, 1):
                            if log_file is not None:
                                log_file.seek(0)  # Reset position
                                df_log = read_excel_logisticien(log_file)
                                if df_log is not None:
                                    list_df_log.append(df_log)
                                else:
                                    st.warning(f"⚠️ Erreur lecture fichier logisticien {idx}")
                        
                        if not list_df_log:
                            st.error("❌ Aucun fichier logisticien valide")
                            st.stop()
                        
                        st.info(f"📊 {len(list_df_log)} fichier(s) logisticien chargé(s) pour l'analyse")
                        
                        # Traitement avec TOUS les fichiers
                        synthese, detail, stats = traiter_retours_mondial_relay(
                            df_retours, list_df_log
                        )
                        
                        if synthese is None:
                            st.error("❌ Aucun retour TOOPOST trouvé")
                            st.stop()
                        
                        # Sauvegarde
                        st.session_state.mr_synthese = synthese
                        st.session_state.mr_detail = detail
                        st.session_state.mr_stats = stats
                        st.session_state.mr_timestamp = datetime.now()
                        st.session_state.mr_data_loaded = True
                        
                        # 💾 SAUVEGARDE FICHIERS
                        files_to_save = {'csv_retours': csv_retours}
                        for idx, log_file in enumerate(log_files):
                            if log_file is not None:
                                files_to_save[f'log_{idx}'] = log_file
                        persistence.save_module_files('mondial_relay', files_to_save)
                        st.session_state.mr_files_loaded = True
                        
                        # 💾 SAUVEGARDE AUTOMATIQUE
                        persistence.save_module_data('mondial_relay', {
                            'synthese': synthese,
                            'detail': detail,
                            'stats': stats,
                            'timestamp': datetime.now()
                        })
                        
                        st.session_state.module_data['mondial_relay'] = {
                            'loaded': True,
                            'timestamp': datetime.now(),
                            'nb_retours': stats['nb_retours']
                        }
                        
                        # 📚 AUTO-ARCHIVAGE DANS LA BIBLIOTHÈQUE
                        success, year, month = persistence.auto_archive_analysis(
                            'Mondial_Relay',
                            detail,
                            {
                                'synthese': synthese,
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
            st.warning("⚠️ Chargez le CSV retours et au moins 1 fichier logisticien")
    
    # Affichage des résultats
    if st.session_state.mr_data_loaded:
        
        stats = st.session_state.mr_stats
        synthese = st.session_state.mr_synthese
        detail = st.session_state.mr_detail
        
        # Statistiques
        st.markdown("---")
        st.markdown("### 📊 Statistiques")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Retours", stats['nb_retours'])
        with col2:
            st.metric("Partenaires", stats['nb_partenaires'])
        with col3:
            st.metric(
                "Montant Total", 
                f"{stats['montant_total']:.2f} €",
                help=f"Base: {stats['montant_base_total']:.2f}€ + Majoration: {stats['majoration_service_total']:.2f}€"
            )
        with col4:
            taux_ident = (stats['nb_identifies'] / stats['nb_retours'] * 100) if stats['nb_retours'] > 0 else 0
            st.metric("Identifiés", f"{taux_ident:.0f}%")
        
        # Onglets
        st.markdown("---")
        tab1, tab2 = st.tabs(["📊 Synthèse par Partenaire", "📋 Détail des Retours"])
        
        with tab1:
            st.markdown("### Synthèse par Partenaire")
            
            # Recherche
            search = st.text_input("🔍 Rechercher partenaire", key="mr_search_syn")
            
            synthese_filt = synthese.copy()
            if search:
                synthese_filt = synthese_filt[
                    synthese_filt['Partenaire'].str.contains(search, case=False, na=False)
                ]
            
            # Affichage
            st.dataframe(synthese_filt, use_container_width=True, hide_index=True)
            
            # Ligne de totaux
            st.markdown("**Totaux :**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Retours", synthese_filt['Nb Retours'].sum())
            with col2:
                st.metric("Base", f"{synthese_filt['Montant Base (€)'].sum():.2f} €")
            with col3:
                st.metric("Majoration Service", f"{synthese_filt['Majoration Service (€)'].sum():.2f} €")
            with col4:
                st.metric("Total", f"{synthese_filt['Montant Total (€)'].sum():.2f} €")
            
            # Export
            if st.button("📥 Exporter Synthèse", key="mr_exp_syn"):
                excel = export_excel({'Synthèse': synthese_filt})
                st.download_button(
                    "💾 Télécharger",
                    excel,
                    f"synthese_mondial_relay_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="mr_dl_syn"
                )
        
        with tab2:
            st.markdown("### Détail des Retours")
            
            col1, col2 = st.columns(2)
            with col1:
                search_det = st.text_input("🔍 Rechercher", key="mr_search_det")
            with col2:
                partenaires = ['Tous'] + sorted(detail['Partenaire'].unique().tolist())
                filter_part = st.selectbox("Partenaire", partenaires, key="mr_filter")
            
            detail_filt = detail.copy()
            if search_det:
                mask = (
                    detail_filt['Partenaire'].astype(str).str.contains(search_det, case=False, na=False) |
                    detail_filt['Tracking Retour'].astype(str).str.contains(search_det, case=False, na=False)
                )
                detail_filt = detail_filt[mask]
            if filter_part != 'Tous':
                detail_filt = detail_filt[detail_filt['Partenaire'] == filter_part]
            
            st.dataframe(detail_filt, use_container_width=True, hide_index=True)
            st.info(f"📊 {len(detail_filt):,}/{len(detail):,} retours")
            
            # Ligne de totaux
            st.markdown("**Totaux :**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Base", f"{detail_filt['Montant Base (€)'].sum():.2f} €")
            with col2:
                st.metric("Majoration Service", f"{detail_filt['Majoration Service (€)'].sum():.2f} €")
            with col3:
                st.metric("Total", f"{detail_filt['Montant Total (€)'].sum():.2f} €")
            
            # Export
            if st.button("📥 Exporter Détail", key="mr_exp_det"):
                excel = export_excel({
                    'Synthèse': synthese,
                    'Détail': detail_filt
                })
                st.download_button(
                    "💾 Télécharger",
                    excel,
                    f"detail_mondial_relay_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="mr_dl_det"
                )
    
    else:
        st.info("👆 Importez vos fichiers pour commencer")
