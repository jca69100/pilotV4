"""
Module : Bibliothèque de Fichiers
Consultation des analyses sauvegardées automatiquement par période
Version 2.0 - Automatique
"""

import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import calendar
from shared import persistence

def get_month_name(month_num):
    """Retourne le nom du mois en français"""
    months = {
        1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
        5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
        9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
    }
    return months.get(month_num, "Inconnu")

def format_file_size(size_bytes):
    """Formate la taille du fichier de manière lisible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def get_library_stats():
    """Retourne les statistiques de la bibliothèque"""
    library = persistence.load_library()
    if not library:
        return {
            'total_analyses': 0,
            'periods': 0,
            'transporteurs': set()
        }
    
    total_analyses = 0
    transporteurs = set()
    
    for period_key, period_data in library.items():
        for transporteur, analyses in period_data.items():
            total_analyses += len(analyses)
            transporteurs.add(transporteur)
    
    return {
        'total_analyses': total_analyses,
        'periods': len(library),
        'transporteurs': transporteurs
    }

def get_analyses_by_period(period_year, period_month):
    """Récupère toutes les analyses d'une période"""
    library = persistence.load_library()
    if not library:
        return {}
    
    period_key = f"{period_year}_{period_month:02d}"
    return library.get(period_key, {})

def delete_period(period_year, period_month):
    """Supprime tous les fichiers d'une période"""
    library = persistence.load_library()
    if not library:
        return False
    
    period_key = f"{period_year}_{period_month:02d}"
    
    if period_key in library:
        del library[period_key]
        persistence.save_library(library)
        return True
    
    return False

def run():
    """Point d'entrée du module Bibliothèque"""
    
    # En-tête
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("📚 Bibliothèque d'Analyses")
        st.markdown("**Consultation des analyses sauvegardées automatiquement**")
    with col2:
        if st.button("🏠 Accueil", use_container_width=True, key="bibliotheque_home"):
            st.session_state.current_module = None
            st.rerun()
    
    st.markdown("---")
    
    # Message d'information
    st.info("""
    💡 **Fonctionnement automatique**
    
    Lorsque vous analysez des fichiers dans les modules (DPD, Mondial Relay, Chronopost, etc.), 
    vos analyses sont **automatiquement sauvegardées** ici avec détection de la période.
    
    Consultez ensuite par mois pour retrouver toutes vos analyses groupées.
    """)
    
    # Statistiques globales
    stats = get_library_stats()
    
    if stats['total_analyses'] == 0:
        st.warning("""
        📭 **Bibliothèque vide**
        
        Aucune analyse sauvegardée pour le moment.
        
        **Pour commencer** :
        1. Allez dans un module (DPD, Chronopost, etc.)
        2. Analysez vos fichiers
        3. Les analyses seront automatiquement archivées ici
        
        Vous pourrez ensuite les consulter par période.
        """)
        return
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Analyses archivées", stats['total_analyses'])
    with col2:
        st.metric("Périodes", stats['periods'])
    with col3:
        st.metric("Transporteurs", len(stats['transporteurs']))
    
    st.markdown("---")
    
    # Onglets
    tab1, tab2 = st.tabs(["📋 Consulter par Période", "🗑️ Gérer l'Espace"])
    
    # TAB 1 : CONSULTER
    with tab1:
        st.subheader("📋 Consulter les Analyses par Période")
        
        library = persistence.load_library()
        
        if not library:
            st.info("📚 Aucune analyse archivée")
        else:
            # Sélection de période
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                # Extraire les années disponibles
                years_available = sorted(list(set([
                    int(period_key.split('_')[0]) 
                    for period_key in library.keys()
                ])), reverse=True)
                
                selected_year = st.selectbox(
                    "Année",
                    options=years_available,
                    key="consult_year"
                )
            
            with col2:
                # Extraire les mois disponibles pour l'année sélectionnée
                months_available = sorted([
                    int(period_key.split('_')[1])
                    for period_key in library.keys()
                    if int(period_key.split('_')[0]) == selected_year
                ])
                
                selected_month = st.selectbox(
                    "Mois",
                    options=months_available,
                    format_func=lambda x: get_month_name(x),
                    key="consult_month"
                )
            
            with col3:
                st.markdown("")
                st.markdown("")
                if st.button("🔍 Consulter", type="primary", use_container_width=True):
                    st.session_state.selected_period = (selected_year, selected_month)
            
            # Afficher les analyses de la période sélectionnée
            if 'selected_period' in st.session_state:
                year, month = st.session_state.selected_period
                
                st.markdown("---")
                st.markdown(f"### 📅 {get_month_name(month)} {year}")
                
                period_analyses = get_analyses_by_period(year, month)
                
                if not period_analyses:
                    st.info("Aucune analyse pour cette période")
                else:
                    # Afficher par transporteur
                    for transporteur, analyses in period_analyses.items():
                        
                        # Icône par transporteur
                        icons = {
                            'dpd': '📊',
                            'mondial_relay': '🌐',
                            'chronopost': '📦',
                            'colissimo': '📮',
                            'colis_prive': '🚚',
                            'retours': '🔄',
                            'dhl': '📦'
                        }
                        icon = icons.get(transporteur.lower(), '📄')
                        
                        with st.expander(f"{icon} {transporteur.upper()} ({len(analyses)} analyse(s))", expanded=True):
                            
                            for idx, analyse in enumerate(analyses):
                                st.markdown(f"**Analyse #{idx + 1}**")
                                
                                col1, col2 = st.columns([3, 1])
                                
                                with col1:
                                    st.caption(f"📅 Analysé le : {analyse.get('analyzed_at', 'Date inconnue')}")
                                    st.caption(f"📊 Lignes : {analyse.get('nb_rows', 'N/A')}")
                                    
                                    # Afficher la plage de dates si disponible
                                    if analyse.get('date_range'):
                                        st.caption(f"📆 Période des dates : {analyse['date_range']}")
                                    
                                    if analyse.get('partners'):
                                        st.caption(f"👥 Partenaires : {', '.join(analyse['partners'][:3])}{'...' if len(analyse['partners']) > 3 else ''}")
                                
                                with col2:
                                    # Bouton pour charger l'analyse
                                    if st.button("📂 Charger", key=f"load_{year}_{month}_{transporteur}_{idx}"):
                                        # Charger les données dans le session_state du module correspondant
                                        module_data = analyse.get('data', {})
                                        
                                        # Mapper le nom du transporteur au module
                                        module_mapping = {
                                            'DPD': 'dpd',
                                            'Mondial_Relay': 'mondial_relay',
                                            'Chronopost': 'chronopost',
                                            'Colissimo': 'colissimo',
                                            'Colis_Prive': 'colis_prive',
                                            'Retours': 'retours',
                                            'DHL': 'dhl'
                                        }
                                        
                                        module_name = module_mapping.get(transporteur)
                                        
                                        if module_name and module_data:
                                            # Charger dans le session_state du module
                                            data_key = f"{module_name}_data"
                                            st.session_state[data_key] = module_data
                                            
                                            # Charger aussi dans les variables individuelles que chaque module attend
                                            if module_name == 'retours':
                                                st.session_state.retours_df_original = module_data.get('df_original')
                                                st.session_state.retours_synthese = module_data.get('synthese')
                                                st.session_state.retours_detail = module_data.get('detail')
                                                st.session_state.retours_stats = module_data.get('stats')
                                                st.session_state.retours_filename = module_data.get('filename', 'Chargé depuis bibliothèque')
                                                st.session_state.retours_timestamp = module_data.get('timestamp')
                                                st.session_state.retours_data_loaded = True
                                                
                                                # Convertir colonnes numériques
                                                import pandas as pd
                                                for key in ['df_original', 'synthese', 'detail']:
                                                    if key in module_data and module_data[key] is not None:
                                                        df = module_data[key]
                                                        for col in df.columns:
                                                            if df[col].dtype == 'object':
                                                                try:
                                                                    df[col] = pd.to_numeric(df[col], errors='ignore')
                                                                except:
                                                                    pass
                                            
                                            elif module_name == 'dpd':
                                                st.session_state.dpd_synthese = module_data.get('synthese')
                                                st.session_state.dpd_detail = module_data.get('detail')
                                                st.session_state.dpd_supplements = module_data.get('supplements')
                                                st.session_state.dpd_retours = module_data.get('retours')
                                                st.session_state.dpd_stats = module_data.get('stats')
                                                st.session_state.dpd_data_loaded = True
                                                
                                                # Convertir colonnes numériques
                                                import pandas as pd
                                                for key in ['synthese', 'detail', 'supplements', 'retours']:
                                                    if key in module_data and module_data[key] is not None:
                                                        df = module_data[key]
                                                        for col in df.columns:
                                                            if df[col].dtype == 'object':
                                                                try:
                                                                    df[col] = pd.to_numeric(df[col], errors='ignore')
                                                                except:
                                                                    pass
                                            
                                            elif module_name == 'mondial_relay':
                                                st.session_state.mr_synthese = module_data.get('synthese')
                                                st.session_state.mr_detail = module_data.get('detail')
                                                st.session_state.mr_stats = module_data.get('stats')
                                                st.session_state.mr_data_loaded = True
                                                
                                                # Convertir colonnes numériques
                                                import pandas as pd
                                                for key in ['synthese', 'detail']:
                                                    if key in module_data and module_data[key] is not None:
                                                        df = module_data[key]
                                                        for col in df.columns:
                                                            if df[col].dtype == 'object':
                                                                try:
                                                                    df[col] = pd.to_numeric(df[col], errors='ignore')
                                                                except:
                                                                    pass
                                            
                                            elif module_name == 'chronopost':
                                                st.session_state.chronopost_data = module_data
                                                st.session_state.chronopost_data_loaded = True
                                                
                                                # Convertir les colonnes numériques pour éviter erreurs
                                                if 'df' in module_data and module_data['df'] is not None:
                                                    import pandas as pd
                                                    df = module_data['df']
                                                    numeric_cols = ['Poids Log. (kg)', 'Poids Chrono (kg)', 
                                                                   'Prix Théorique (€)', 'Prix Facturé (€)', 'Écart (€)']
                                                    for col in numeric_cols:
                                                        if col in df.columns:
                                                            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                                                    module_data['df'] = df
                                                
                                                if 'df_surplus' in module_data and module_data['df_surplus'] is not None:
                                                    import pandas as pd
                                                    df_surplus = module_data['df_surplus']
                                                    surplus_numeric_cols = ['Poids (kg)', 'Montant (€)']
                                                    for col in surplus_numeric_cols:
                                                        if col in df_surplus.columns:
                                                            df_surplus[col] = pd.to_numeric(df_surplus[col], errors='coerce').fillna(0)
                                                    module_data['df_surplus'] = df_surplus
                                            
                                            elif module_name == 'colissimo':
                                                st.session_state.colissimo_detail = module_data.get('detail')
                                                st.session_state.colissimo_stats = module_data.get('stats')
                                                st.session_state.colissimo_data_loaded = True
                                                
                                                # Convertir colonnes numériques
                                                import pandas as pd
                                                if 'detail' in module_data and module_data['detail'] is not None:
                                                    df = module_data['detail']
                                                    for col in df.columns:
                                                        if df[col].dtype == 'object':
                                                            try:
                                                                df[col] = pd.to_numeric(df[col], errors='ignore')
                                                            except:
                                                                pass
                                            
                                            elif module_name == 'colis_prive':
                                                st.session_state.colis_prive_data = module_data
                                                st.session_state.colis_prive_data_loaded = True
                                                
                                                # Convertir colonnes numériques
                                                import pandas as pd
                                                if 'df' in module_data and module_data['df'] is not None:
                                                    df = module_data['df']
                                                    for col in df.columns:
                                                        if df[col].dtype == 'object':
                                                            try:
                                                                df[col] = pd.to_numeric(df[col], errors='ignore')
                                                            except:
                                                                pass
                                            
                                            elif module_name == 'dhl':
                                                st.session_state.dhl_data = module_data
                                                st.session_state.dhl_data_loaded = True
                                                
                                                # Convertir colonnes numériques
                                                import pandas as pd
                                                if 'df' in module_data and module_data['df'] is not None:
                                                    df = module_data['df']
                                                    numeric_cols = ['Tarif_Base_HT', 'XC1_Montant_HT', 'XC2_Montant_HT',
                                                                   'XC3_Montant_HT', 'XC4_Montant_HT', 'Total_TTC']
                                                    for col in numeric_cols:
                                                        if col in df.columns:
                                                            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                                                
                                                if 'synthese_colonnes' in module_data and module_data['synthese_colonnes'] is not None:
                                                    synthese_df = module_data['synthese_colonnes']
                                                    for col in synthese_df.columns:
                                                        if synthese_df[col].dtype == 'object':
                                                            try:
                                                                synthese_df[col] = pd.to_numeric(synthese_df[col], errors='ignore')
                                                            except:
                                                                pass
                                            
                                            # Marquer comme chargé depuis bibliothèque
                                            st.session_state[f"{module_name}_from_library"] = True
                                            
                                            # Message et redirection
                                            st.success(f"✅ Analyse chargée ! Redirection vers {transporteur}...")
                                            st.session_state.current_module = module_name
                                            st.rerun()
                                        else:
                                            st.error("❌ Impossible de charger cette analyse")
                                
                                st.markdown("---")
    
    # TAB 2 : GÉRER
    with tab2:
        st.subheader("🗑️ Gérer l'Espace de Stockage")
        
        library = persistence.load_library()
        
        if not library:
            st.info("📚 Aucune analyse archivée")
        else:
            st.markdown("""
            ### ⚠️ Suppression de Périodes
            
            Vous pouvez supprimer des périodes entières pour libérer de l'espace.
            """)
            
            # Liste des périodes avec statistiques
            st.markdown("#### 📅 Périodes Archivées")
            
            for period_key in sorted(library.keys(), reverse=True):
                year, month = period_key.split('_')
                year = int(year)
                month = int(month)
                
                period_data = library[period_key]
                
                # Calculer stats de la période
                total_analyses_period = sum(len(analyses) for analyses in period_data.values())
                transporteurs_period = list(period_data.keys())
                
                with st.expander(f"📅 {get_month_name(month)} {year} - {total_analyses_period} analyse(s) - {len(transporteurs_period)} transporteur(s)"):
                    
                    # Afficher détails par transporteur
                    for transporteur, analyses in period_data.items():
                        st.markdown(f"**{transporteur.upper()}** ({len(analyses)} analyse(s))")
                    
                    st.markdown("---")
                    
                    # Bouton pour supprimer toute la période
                    if st.button(f"🗑️ Supprimer la période {get_month_name(month)} {year}", 
                               type="secondary", 
                               key=f"del_period_{period_key}"):
                        if delete_period(year, month):
                            st.success(f"✅ Période {get_month_name(month)} {year} supprimée")
                            st.rerun()
            
            # Bouton de suppression totale
            st.markdown("---")
            st.markdown("#### ⚠️ Danger Zone")
            
            if st.button("🗑️ SUPPRIMER TOUTE LA BIBLIOTHÈQUE", type="secondary"):
                persistence.delete_library()
                st.success("✅ Bibliothèque complètement vidée")
                st.rerun()
