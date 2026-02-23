"""
Module : Retours Produits
Analyse des retours par client
Version 2.1 - AVEC PERSISTANCE DES FICHIERS UPLOADÉS
"""

import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import pickle
from shared import persistence

def export_excel(df, sheet_name):
    """Export DataFrame vers Excel"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    return output.getvalue()

def save_session():
    """Sauvegarde la session du module"""
    if st.session_state.get('retours_data_loaded', False):
        session_data = {
            'df_original': st.session_state.retours_df_original,
            'synthese': st.session_state.retours_synthese,
            'detail': st.session_state.retours_detail,
            'stats': st.session_state.retours_stats,
            'filename': st.session_state.retours_filename,
            'timestamp': datetime.now()
        }
        return pickle.dumps(session_data)
    return None

def load_session(session_file):
    """Charge une session sauvegardée"""
    try:
        data = pickle.load(session_file)
        st.session_state.retours_df_original = data['df_original']
        st.session_state.retours_synthese = data['synthese']
        st.session_state.retours_detail = data['detail']
        st.session_state.retours_stats = data['stats']
        st.session_state.retours_filename = data['filename']
        st.session_state.retours_timestamp = data['timestamp']
        st.session_state.retours_data_loaded = True
        return True
    except:
        return False

def run():
    """Point d'entrée du module"""
    
    # Initialisation
    if 'retours_data_loaded' not in st.session_state:
        st.session_state.retours_data_loaded = False
    if 'retours_files_loaded' not in st.session_state:
        st.session_state.retours_files_loaded = False
    
    # 💾 CHARGEMENT AUTOMATIQUE au premier accès
    if not st.session_state.retours_files_loaded:
        # Charger les fichiers uploadés
        saved_files = persistence.load_module_files('retours')
        if saved_files and 'csv_retours' in saved_files:
            st.session_state.retours_csv_file = saved_files['csv_retours']
            st.session_state.retours_files_loaded = True
        
        # Charger les données traitées
        saved_data = persistence.load_module_data('retours')
        if saved_data:
            st.session_state.retours_df_original = saved_data['df_original']
            st.session_state.retours_synthese = saved_data['synthese']
            st.session_state.retours_detail = saved_data['detail']
            st.session_state.retours_stats = saved_data['stats']
            st.session_state.retours_filename = saved_data['filename']
            st.session_state.retours_timestamp = saved_data['timestamp']
            st.session_state.retours_data_loaded = True
    
    # En-tête module
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("🔄 Module Retours Produits")
        st.markdown("Analyse des retours par client")
    with col2:
        if st.session_state.retours_data_loaded or st.session_state.retours_files_loaded:
            if st.button("🗑️ Réinitialiser", type="secondary", key="retours_reset"):
                # Supprimer TOUTES les sauvegardes du module
                persistence.delete_module_data('retours')
                
                # Effacer les données du module
                for key in list(st.session_state.keys()):
                    if key.startswith('retours_'):
                        del st.session_state[key]
                
                st.success("✅ Module réinitialisé - toutes les sauvegardes supprimées")
                st.rerun()
    
    st.markdown("---")
    
    # Instructions
    with st.expander("📖 Instructions"):
        st.markdown("""
        ### Colonnes CSV requises
        `id`, `state`, `resellers.name`, `orders.id`, `createdAt`, `returnOrderItems.quantity`
        
        ### Fonctionnalités
        - ✅ Filtrage automatique (state='returned')
        - ✅ Synthèse par client
        - ✅ Détail des retours
        - ✅ Export Excel
        - ✅ **Sauvegarde automatique des fichiers uploadés**
        - ✅ Rechargement automatique au démarrage
        """)
    
    st.markdown("### 📁 Import des données")
    
    # Gestion des données
    if st.session_state.retours_data_loaded:
        # Données chargées
        col1, col2 = st.columns([3, 1])
        with col1:
            st.success(f"✅ **{st.session_state.retours_filename}** ({len(st.session_state.retours_df_original)} lignes)")
            st.caption("💾 Fichier sauvegardé - rechargé automatiquement")
        with col2:
            # Export session
            if st.button("📥 Export Session", key="retours_export_session"):
                session_bytes = save_session()
                if session_bytes:
                    st.download_button(
                        "💾 Télécharger",
                        session_bytes,
                        f"retours_session_{datetime.now().strftime('%Y%m%d_%H%M')}.pkl",
                        "application/octet-stream",
                        key="dl_retours_session"
                    )
    
    else:
        # Vérifier si fichier déjà chargé en mémoire
        if st.session_state.retours_files_loaded:
            st.info(f"📄 Fichier chargé : **{st.session_state.retours_csv_file.name}**")
            st.caption("💾 Chargé depuis la sauvegarde automatique")
            
            # Bouton pour retraiter
            if st.button("🔄 Traiter le fichier", type="primary", use_container_width=True):
                csv_file = st.session_state.retours_csv_file
                csv_file.seek(0)  # Retour au début
                
                try:
                    df = pd.read_csv(csv_file)
                    required = ['id', 'state', 'resellers.name', 'orders.id', 'createdAt', 'returnOrderItems.quantity']
                    
                    if not all(col in df.columns for col in required):
                        st.error("❌ Colonnes manquantes")
                        st.stop()
                    
                    df_ret = df[df['state'] == 'returned'].copy()
                    if len(df_ret) == 0:
                        st.warning("⚠️ Aucun retour trouvé")
                        st.stop()
                    
                    # Synthèse
                    synthese = df_ret.groupby('resellers.name').agg({
                        'id': 'nunique',
                        'orders.id': lambda x: ', '.join(str(v) for v in x.unique() if pd.notna(v))
                    }).reset_index()
                    synthese.columns = ['Client', 'Nombre de Retours', 'Numéros de Commandes']
                    synthese = synthese.sort_values('Nombre de Retours', ascending=False)
                    
                    # Détail
                    detail = df_ret.groupby('id').agg({
                        'resellers.name': 'first',
                        'orders.id': 'first',
                        'createdAt': 'first',
                        'returnOrderItems.quantity': 'sum'
                    }).reset_index()
                    detail.columns = ['ID Retour', 'Client', 'N° Commande', 'Date Création', 'Produits Retournés']
                    detail['Date Création'] = pd.to_datetime(detail['Date Création']).dt.strftime('%d/%m/%Y')
                    detail = detail.sort_values('Date Création', ascending=False)
                    
                    # Stats
                    stats = {
                        'total_retours': len(df_ret),
                        'nb_clients': df_ret['resellers.name'].nunique(),
                        'total_produits': int(df_ret['returnOrderItems.quantity'].sum())
                    }
                    
                    # Sauvegarde
                    st.session_state.retours_df_original = df
                    st.session_state.retours_synthese = synthese
                    st.session_state.retours_detail = detail
                    st.session_state.retours_stats = stats
                    st.session_state.retours_filename = csv_file.name
                    st.session_state.retours_timestamp = datetime.now()
                    st.session_state.retours_data_loaded = True
                    
                    # 💾 SAUVEGARDE AUTOMATIQUE DES DONNÉES
                    persistence.save_module_data('retours', {
                        'df_original': df,
                        'synthese': synthese,
                        'detail': detail,
                        'stats': stats,
                        'filename': csv_file.name,
                        'timestamp': datetime.now()
                    })
                    
                    # Sauvegarder dans module_data global
                    st.session_state.module_data['retours'] = {
                        'loaded': True,
                        'timestamp': datetime.now(),
                        'filename': csv_file.name
                    }
                    
                    st.success("✅ Analyse terminée et sauvegardée !")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Erreur : {e}")
        
        else:
            # Import nouveau fichier
            col1, col2 = st.columns(2)
            
            with col1:
                session_file = st.file_uploader("📂 Recharger une session", type=['pkl'], key="retours_session")
                if session_file:
                    if load_session(session_file):
                        st.success("✅ Session rechargée")
                        st.rerun()
                    else:
                        st.error("❌ Erreur de chargement")
            
            with col2:
                csv_file = st.file_uploader("📄 Importer un CSV", type=['csv'], key="retours_csv")
                if csv_file:
                    try:
                        df = pd.read_csv(csv_file)
                        required = ['id', 'state', 'resellers.name', 'orders.id', 'createdAt', 'returnOrderItems.quantity']
                        
                        if not all(col in df.columns for col in required):
                            st.error("❌ Colonnes manquantes")
                            st.stop()
                        
                        df_ret = df[df['state'] == 'returned'].copy()
                        if len(df_ret) == 0:
                            st.warning("⚠️ Aucun retour trouvé")
                            st.stop()
                        
                        # Synthèse
                        synthese = df_ret.groupby('resellers.name').agg({
                            'id': 'nunique',
                            'orders.id': lambda x: ', '.join(str(v) for v in x.unique() if pd.notna(v))
                        }).reset_index()
                        synthese.columns = ['Client', 'Nombre de Retours', 'Numéros de Commandes']
                        synthese = synthese.sort_values('Nombre de Retours', ascending=False)
                        
                        # Détail
                        detail = df_ret.groupby('id').agg({
                            'resellers.name': 'first',
                            'orders.id': 'first',
                            'createdAt': 'first',
                            'returnOrderItems.quantity': 'sum'
                        }).reset_index()
                        detail.columns = ['ID Retour', 'Client', 'N° Commande', 'Date Création', 'Produits Retournés']
                        detail['Date Création'] = pd.to_datetime(detail['Date Création']).dt.strftime('%d/%m/%Y')
                        detail = detail.sort_values('Date Création', ascending=False)
                        
                        # Stats
                        stats = {
                            'total_retours': len(df_ret),
                            'nb_clients': df_ret['resellers.name'].nunique(),
                            'total_produits': int(df_ret['returnOrderItems.quantity'].sum())
                        }
                        
                        # Sauvegarde en session_state
                        st.session_state.retours_df_original = df
                        st.session_state.retours_synthese = synthese
                        st.session_state.retours_detail = detail
                        st.session_state.retours_stats = stats
                        st.session_state.retours_filename = csv_file.name
                        st.session_state.retours_timestamp = datetime.now()
                        st.session_state.retours_data_loaded = True
                        st.session_state.retours_csv_file = csv_file
                        st.session_state.retours_files_loaded = True
                        
                        # 💾 SAUVEGARDE AUTOMATIQUE DES FICHIERS
                        persistence.save_module_files('retours', {
                            'csv_retours': csv_file
                        })
                        
                        # 💾 SAUVEGARDE AUTOMATIQUE DES DONNÉES
                        persistence.save_module_data('retours', {
                            'df_original': df,
                            'synthese': synthese,
                            'detail': detail,
                            'stats': stats,
                            'filename': csv_file.name,
                            'timestamp': datetime.now()
                        })
                        
                        # Sauvegarder dans module_data global
                        st.session_state.module_data['retours'] = {
                            'loaded': True,
                            'timestamp': datetime.now(),
                            'filename': csv_file.name
                        }
                        
                        # 📚 AUTO-ARCHIVAGE DANS LA BIBLIOTHÈQUE
                        success, year, month = persistence.auto_archive_analysis(
                            'Retours',
                            detail,
                            {
                                'df_original': df,
                                'synthese': synthese,
                                'detail': detail,
                                'stats': stats
                            },
                            date_column='Date'
                        )
                        
                        # Message avec info archivage
                        if success:
                            from modules.bibliotheque import get_month_name
                            st.success(f"✅ Fichier sauvegardé et archivé ({get_month_name(month)} {year})")
                        else:
                            st.success("✅ Fichier sauvegardé automatiquement !")
                        
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Erreur : {e}")
    
    # Affichage des résultats
    if st.session_state.retours_data_loaded:
        stats = st.session_state.retours_stats
        
        st.markdown("---")
        st.markdown("### 📊 Statistiques")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Retours", stats['total_retours'])
        with col2:
            st.metric("Clients", stats['nb_clients'])
        with col3:
            st.metric("Produits", stats['total_produits'])
        
        st.markdown("---")
        tab1, tab2 = st.tabs(["📊 Synthèse", "📋 Détail"])
        
        with tab1:
            st.markdown("### Synthèse par Client")
            search = st.text_input("🔍 Rechercher", key="retours_search_syn")
            
            synthese = st.session_state.retours_synthese
            if search:
                synthese = synthese[synthese['Client'].str.contains(search, case=False, na=False)]
            
            st.dataframe(synthese, use_container_width=True, hide_index=True)
            
            if st.button("📥 Exporter", key="retours_exp_syn"):
                excel = export_excel(synthese, 'Synthèse')
                st.download_button(
                    "💾 Télécharger",
                    excel,
                    f"synthese_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="retours_dl_syn"
                )
        
        with tab2:
            st.markdown("### Détail des Retours")
            col1, col2 = st.columns(2)
            
            with col1:
                search_det = st.text_input("🔍 Rechercher", key="retours_search_det")
            with col2:
                detail = st.session_state.retours_detail
                clients = ['Tous'] + sorted(detail['Client'].unique().tolist())
                filter_cli = st.selectbox("Client", clients, key="retours_filter")
            
            detail_filt = detail.copy()
            if search_det:
                mask = (
                    detail_filt['ID Retour'].astype(str).str.contains(search_det, case=False, na=False) |
                    detail_filt['Client'].astype(str).str.contains(search_det, case=False, na=False)
                )
                detail_filt = detail_filt[mask]
            if filter_cli != 'Tous':
                detail_filt = detail_filt[detail_filt['Client'] == filter_cli]
            
            st.dataframe(detail_filt, use_container_width=True, hide_index=True)
            st.info(f"📊 {len(detail_filt)}/{len(detail)} retours")
            
            if st.button("📥 Exporter", key="retours_exp_det"):
                excel = export_excel(detail_filt, 'Détail')
                st.download_button(
                    "💾 Télécharger",
                    excel,
                    f"detail_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="retours_dl_det"
                )
    else:
        if not st.session_state.retours_files_loaded:
            st.info("👆 Importez vos données")
