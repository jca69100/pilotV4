"""
Module : Bibliothèque Logisticiens
Gestion cumulative des fichiers logisticiens par mois
Version 1.0
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from shared import persistence

def get_month_name(month_num):
    """Retourne le nom du mois en français"""
    months = {
        1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
        5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
        9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
    }
    return months.get(month_num, "Inconnu")

def detect_period_from_logisticien(file):
    """
    Détecte la période (mois/année) d'un fichier logisticien
    en analysant les dates d'expédition
    """
    try:
        import pandas as pd
        from collections import Counter
        
        # Lire le fichier
        df = pd.read_excel(file, sheet_name='Facturation préparation')
        
        # Chercher colonne date
        date_col = None
        for col in df.columns:
            if 'date' in col.lower() and 'expédition' in col.lower():
                date_col = col
                break
        
        if not date_col:
            return None, None
        
        # Convertir en datetime
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        dates_valid = df[date_col].dropna()
        
        if len(dates_valid) == 0:
            return None, None
        
        # Prendre le mois le plus récent avec le plus de données
        max_date = dates_valid.max()
        cutoff = max_date - pd.DateOffset(months=2)
        dates_recent = dates_valid[dates_valid >= cutoff]
        
        year_months = [(d.year, d.month) for d in dates_recent]
        counter = Counter(year_months)
        
        if counter:
            (year, month), count = counter.most_common(1)[0]
            return year, month
        
        return None, None
        
    except Exception as e:
        print(f"Erreur détection période: {e}")
        return None, None

def save_logisticien_file(file, year, month):
    """Sauvegarde un fichier logisticien avec sa période"""
    try:
        # Lire le contenu
        file.seek(0)
        file_content = file.read()
        file.seek(0)
        
        # Charger la bibliothèque
        library = persistence.load_logisticiens_library()
        if library is None:
            library = {}
        
        # Clé de période
        period_key = f"{year}_{month:02d}"
        
        # Sauvegarder
        library[period_key] = {
            'filename': file.name,
            'content': file_content,
            'size': len(file_content),
            'uploaded_at': datetime.now().isoformat(),
            'year': year,
            'month': month
        }
        
        # Persister
        persistence.save_logisticiens_library(library)
        
        return True
        
    except Exception as e:
        print(f"Erreur sauvegarde fichier: {e}")
        return False

def get_all_available_periods():
    """Retourne toutes les périodes disponibles"""
    library = persistence.load_logisticiens_library()
    if not library:
        return []
    
    periods = []
    for period_key, data in library.items():
        periods.append({
            'key': period_key,
            'year': data['year'],
            'month': data['month'],
            'filename': data['filename'],
            'uploaded_at': data['uploaded_at']
        })
    
    # Trier par date décroissante
    periods.sort(key=lambda x: (x['year'], x['month']), reverse=True)
    
    return periods

def load_logisticien_files_for_analysis(nb_months=3):
    """
    Charge automatiquement les N derniers mois de fichiers logisticiens
    pour l'analyse
    
    Returns:
        list: Liste de fichiers chargés (BytesIO avec name)
    """
    library = persistence.load_logisticiens_library()
    if not library:
        return []
    
    # Récupérer toutes les périodes
    periods = get_all_available_periods()
    
    # Prendre les N plus récentes
    selected_periods = periods[:nb_months]
    
    files = []
    for period in selected_periods:
        period_key = period['key']
        if period_key in library:
            from io import BytesIO
            
            # Créer un fichier BytesIO
            file_content = library[period_key]['content']
            file_obj = BytesIO(file_content)
            file_obj.name = library[period_key]['filename']
            
            files.append(file_obj)
    
    return files

def delete_period_logisticien(year, month):
    """Supprime un fichier logisticien"""
    library = persistence.load_logisticiens_library()
    if not library:
        return False
    
    period_key = f"{year}_{month:02d}"
    
    if period_key in library:
        del library[period_key]
        persistence.save_logisticiens_library(library)
        return True
    
    return False

def run():
    """Interface de gestion des fichiers logisticiens"""
    
    # En-tête
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("📋 Bibliothèque Logisticiens")
        st.markdown("**Gestion cumulative des fichiers logisticiens par mois**")
    with col2:
        if st.button("🏠 Accueil", use_container_width=True, key="loglib_home"):
            st.session_state.current_module = None
            st.rerun()
    
    st.markdown("---")
    
    # Info
    st.info("""
    💡 **Système Cumulatif Automatique**
    
    **Comment ça marche** :
    1. Uploadez vos fichiers logisticiens mois par mois
    2. Chaque fichier est sauvegardé avec sa période (détection auto)
    3. Lors des analyses transporteurs, **tous les fichiers disponibles** sont chargés automatiquement
    
    **Avantage** : Plus besoin de re-uploader les anciens fichiers !
    """)
    
    # Onglets
    tab1, tab2 = st.tabs(["➕ Ajouter Fichiers", "📋 Fichiers Disponibles"])
    
    # TAB 1 : AJOUTER
    with tab1:
        st.subheader("➕ Ajouter des Fichiers Logisticiens")
        
        st.markdown("""
        ### 📤 Upload
        
        Uploadez vos fichiers logisticiens. La période (mois/année) sera **détectée automatiquement** 
        depuis les dates d'expédition.
        """)
        
        uploaded_files = st.file_uploader(
            "Sélectionnez un ou plusieurs fichiers logisticiens",
            type=['xlsx', 'xls'],
            accept_multiple_files=True,
            help="Fichiers Excel avec feuille 'Facturation préparation'"
        )
        
        if uploaded_files:
            if st.button("💾 Sauvegarder les Fichiers", type="primary", use_container_width=True):
                results = []
                
                with st.spinner("Analyse et sauvegarde en cours..."):
                    for file in uploaded_files:
                        # Détecter période
                        year, month = detect_period_from_logisticien(file)
                        
                        if year and month:
                            # Sauvegarder
                            if save_logisticien_file(file, year, month):
                                results.append({
                                    'file': file.name,
                                    'period': f"{get_month_name(month)} {year}",
                                    'status': 'success'
                                })
                            else:
                                results.append({
                                    'file': file.name,
                                    'period': 'Erreur sauvegarde',
                                    'status': 'error'
                                })
                        else:
                            results.append({
                                'file': file.name,
                                'period': 'Période non détectée',
                                'status': 'error'
                            })
                
                # Afficher résultats
                for result in results:
                    if result['status'] == 'success':
                        st.success(f"✅ {result['file']} → {result['period']}")
                    else:
                        st.error(f"❌ {result['file']} → {result['period']}")
                
                if any(r['status'] == 'success' for r in results):
                    st.rerun()
    
    # TAB 2 : CONSULTER
    with tab2:
        st.subheader("📋 Fichiers Logisticiens Disponibles")
        
        periods = get_all_available_periods()
        
        if not periods:
            st.info("📭 Aucun fichier logisticien sauvegardé")
        else:
            st.success(f"✅ **{len(periods)} fichier(s) disponible(s)**")
            
            st.markdown("""
            Ces fichiers seront **automatiquement chargés** lors des analyses transporteurs.
            """)
            
            # Affichage des fichiers
            for period in periods:
                col1, col2, col3, col4 = st.columns([2, 2, 3, 1])
                
                with col1:
                    st.markdown(f"**{get_month_name(period['month'])} {period['year']}**")
                
                with col2:
                    st.caption(period['filename'])
                
                with col3:
                    upload_date = datetime.fromisoformat(period['uploaded_at'])
                    st.caption(f"Ajouté le {upload_date.strftime('%d/%m/%Y à %H:%M')}")
                
                with col4:
                    if st.button("🗑️", key=f"del_{period['key']}", help="Supprimer"):
                        if delete_period_logisticien(period['year'], period['month']):
                            st.success("✅ Supprimé")
                            st.rerun()
                
                st.markdown("---")
            
            # Info utilisation
            st.markdown("### 💡 Utilisation dans les Modules")
            
            st.markdown("""
            Lorsque vous analysez dans un module transporteur (DPD, Mondial Relay, etc.), 
            le système charge automatiquement les **3 derniers mois** disponibles :
            """)
            
            if len(periods) >= 3:
                st.success(f"""
                **Fichiers chargés automatiquement** :
                1. {get_month_name(periods[0]['month'])} {periods[0]['year']}
                2. {get_month_name(periods[1]['month'])} {periods[1]['year']}
                3. {get_month_name(periods[2]['month'])} {periods[2]['year']}
                """)
            else:
                files_list = "\n".join([
                    f"{i+1}. {get_month_name(p['month'])} {p['year']}"
                    for i, p in enumerate(periods)
                ])
                st.info(f"""
                **Fichiers chargés automatiquement** :
                {files_list}
                
                💡 Ajoutez plus de fichiers pour avoir 3 mois de données
                """)
