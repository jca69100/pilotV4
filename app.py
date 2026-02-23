import streamlit as st
import pandas as pd
import pickle
from datetime import datetime
from shared import persistence
from shared.auto_backup import AutoBackup
from modules.keep_alive import add_keep_alive_settings
import base64
from pathlib import Path

# Fonction pour charger le logo en base64
def get_logo_base64():
    """Charge le logo GREENLOG en base64 pour l'affichage"""
    logo_path = Path(__file__).parent / "logo_greenlog.jpg"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def get_carrier_logo_base64(carrier_name):
    """Charge un logo de transporteur en base64"""
    logo_mapping = {
        'dpd': 'dpd.svg',
        'mondial_relay': 'mondial_relay.svg',
        'colissimo': 'colissimo.webp',
        'chronopost': 'chronopost.png',
        'colis_prive': 'colis_prive.png',
        'dhl': 'dhl.png'
    }
    
    logo_file = logo_mapping.get(carrier_name)
    if not logo_file:
        return None
    
    logo_path = Path(__file__).parent / "logos" / logo_file
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            content = f.read()
            # Détecter le type MIME
            if logo_file.endswith('.svg'):
                mime_type = 'image/svg+xml'
            elif logo_file.endswith('.webp'):
                mime_type = 'image/webp'
            else:
                mime_type = 'image/png'
            return base64.b64encode(content).decode(), mime_type
    return None

# Configuration
st.set_page_config(
    page_title="pilot by GREENLOG - Plateforme Multi-Transporteurs",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"  # Sidebar fermée par défaut
)

# CSS personnalisé avec couleurs Greenlog
st.markdown("""
<style>
    /* Import Google Fonts pour pilot */
    @import url('https://fonts.googleapis.com/css2?family=Pacifico&family=Montserrat:wght@400;600;800&display=swap');
    
    /* Couleurs Greenlog */
    :root {
        --greenlog-navy: #2D3E50;
        --greenlog-green: #6BBFA3;
        --greenlog-light: #E8F5F1;
    }
    
    .main {
        background-color: #f8fafb;
    }
    
    /* Bandeau GREENLOG amélioré */
    .greenlog-banner {
        background: linear-gradient(135deg, var(--greenlog-navy) 0%, #3d5a7a 100%);
        padding: 25px 30px;
        border-radius: 15px;
        box-shadow: 0 8px 24px rgba(45, 62, 80, 0.3);
        margin-bottom: 30px;
        border: 3px solid var(--greenlog-green);
    }
    
    /* Style pour "pilot" */
    .pilot-brand {
        font-family: 'Pacifico', cursive;
        color: var(--greenlog-green) !important;
        font-size: 48px !important;
        font-weight: 400 !important;
        margin: 0 !important;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
        letter-spacing: 2px;
        display: inline-block;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from {
            text-shadow: 3px 3px 6px rgba(0,0,0,0.3), 0 0 10px rgba(107, 191, 163, 0.4);
        }
        to {
            text-shadow: 3px 3px 6px rgba(0,0,0,0.3), 0 0 20px rgba(107, 191, 163, 0.6);
        }
    }
    
    /* Style pour "by GREENLOG" */
    .by-greenlog {
        font-family: 'Montserrat', sans-serif;
        color: white !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        margin: 5px 0 0 0 !important;
        letter-spacing: 3px;
        text-transform: uppercase;
    }
    
    /* Style pour le logo */
    .greenlog-logo {
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        background: white;
        padding: 10px;
    }
    
    .greenlog-title {
        color: white !important;
        font-size: 32px !important;
        font-weight: 800 !important;
        margin: 0 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .greenlog-subtitle {
        color: var(--greenlog-green) !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        margin: 5px 0 0 0 !important;
    }
    
    .greenlog-logo {
        filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.3));
    }
    
    /* Boutons modules avec couleurs Greenlog */
    .stButton>button {
        width: 100%;
        height: 120px;
        font-size: 18px;
        font-weight: 600;
        border-radius: 12px;
        border: 2px solid var(--greenlog-green);
        background: white;
        color: var(--greenlog-navy);
        transition: all 0.3s;
    }
    .stButton>button:hover {
        border-color: var(--greenlog-navy);
        background: var(--greenlog-light);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(107, 191, 163, 0.3);
    }
    
    /* Métriques */
    [data-testid="stMetricValue"] {
        color: var(--greenlog-navy);
    }
    
    /* En-têtes */
    h1, h2, h3 {
        color: var(--greenlog-navy) !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border: 2px solid var(--greenlog-green);
        color: var(--greenlog-navy);
        border-radius: 8px 8px 0 0;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--greenlog-green);
        color: white;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: var(--greenlog-light);
        border-left: 4px solid var(--greenlog-green);
    }
</style>
""", unsafe_allow_html=True)

# Initialisation session_state
if 'current_module' not in st.session_state:
    st.session_state.current_module = None
if 'shared_logisticiens' not in st.session_state:
    st.session_state.shared_logisticiens = {}
if 'module_data' not in st.session_state:
    st.session_state.module_data = {}
if 'auto_loaded' not in st.session_state:
    st.session_state.auto_loaded = False

# 💾 CHARGEMENT AUTOMATIQUE au premier démarrage
if not st.session_state.auto_loaded:
    # Charger les fichiers logisticiens partagés
    saved_shared = persistence.load_shared_logisticiens()
    if saved_shared:
        st.session_state.shared_logisticiens = saved_shared
    
    st.session_state.auto_loaded = True

# En-tête avec bandeau GREENLOG
# Bandeau principal GREENLOG
logo_base64 = get_logo_base64()

if logo_base64:
    logo_html = f'<img src="data:image/jpeg;base64,{logo_base64}" width="120" class="greenlog-logo">'
else:
    logo_html = '<div style="width: 120px; height: 60px; background: var(--greenlog-green); border-radius: 8px;"></div>'

st.markdown(f"""
<div class="greenlog-banner">
    <div style="display: flex; align-items: center; justify-content: center; gap: 30px;">
        <div style="flex: 0 0 auto;">
            {logo_html}
        </div>
        <div style="flex: 1; text-align: center;">
            <div class="pilot-brand">pilot</div>
            <div class="by-greenlog">by GREENLOG</div>
            <div class="greenlog-subtitle" style="margin-top: 10px;">📦 Plateforme d'Analyse Multi-Transporteurs</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Bouton en haut à droite
col_space, col_button = st.columns([6, 1])
with col_button:
    if st.session_state.current_module:
        if st.button("🏠 Accueil", use_container_width=True):
            st.session_state.current_module = None
            st.rerun()

st.markdown("---")

# Afficher notification de sauvegarde automatique si disponible
AutoBackup.show_auto_backup_notification()

# Sidebar pour sauvegarde rapide
with st.sidebar:
    st.markdown("### 💾 Sauvegarde Rapide")
    
    # Toggle pour activer/désactiver les sauvegardes automatiques
    auto_enabled = st.toggle(
        "🤖 Auto",
        value=st.session_state.get('auto_backup_enabled', True),  # Activé par défaut
        help="Sauvegardes automatiques après chaque modification"
    )
    st.session_state.auto_backup_enabled = auto_enabled
    
    # Bouton de sauvegarde manuelle
    if st.button("💾 Sauvegarder maintenant", use_container_width=True):
        with st.spinner("Création..."):
            try:
                from modules.backup_restore import export_all_data
                backup_zip, files_count, files_list = export_all_data()
                
                if files_count == 0:
                    st.warning("⚠️ Aucune donnée à sauvegarder")
                else:
                    filename = f"pilot_GREENLOG_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                    
                    # Vérifier si indemnisations incluses
                    has_indemnisations = any('indemnisation' in f['name'].lower() for f in files_list)
                    
                    if has_indemnisations:
                        st.success(f"✅ {files_count} fichier(s) (dont indemnisations)")
                    else:
                        st.success(f"✅ {files_count} fichier(s)")
                    
                    st.download_button(
                        label="📥 Télécharger",
                        data=backup_zip,
                        file_name=filename,
                        mime="application/zip",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
    
    st.caption("💡 Pensez à sauvegarder avant chaque Reboot !")
    
    # Keep-Alive settings
    add_keep_alive_settings()

# Navigation principale
if st.session_state.current_module is None:
    # Page d'accueil - Sélection de module
    
    st.markdown("---")
    
    # BLOC 1 : OUTILS DE GESTION
    st.markdown("### 🛠️ Outils de Gestion")
    st.markdown("*Modules de support et stockage des données*")
    st.markdown("")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📋 Import Fichier Logisticien", help="Gestion cumulative fichiers logisticiens", use_container_width=True):
            st.session_state.current_module = 'logisticiens_library'
            st.rerun()
        st.caption("Upload une fois, utilise partout")
    
    with col2:
        if st.button("📚 Sauvegarde des Analyses", help="Gestion permanente des fichiers par période", use_container_width=True):
            st.session_state.current_module = 'bibliotheque'
            st.rerun()
        st.caption("Stockage permanent et consultation par période")
    
    st.markdown("")
    
    col1b, col2b = st.columns(2)
    
    with col1b:
        if st.button("🔄 Traitement des Retours", help="Analyse des retours par client", use_container_width=True):
            st.session_state.current_module = 'retours'
            st.rerun()
        st.caption("Analyse des retours par client avec export Excel")
    
    with col2b:
        if st.button("💶 Indemnisations", help="Suivi des indemnisations transporteurs", use_container_width=True):
            st.session_state.current_module = 'indemnisations'
            st.rerun()
        st.caption("Suivi indemnisations par partenaire")
    
    st.markdown("")
    
    col1c, col2c = st.columns(2)
    
    with col1c:
        if st.button("📦 Attendus de Réception", help="Gestion des attendus d'entrepôt", use_container_width=True):
            st.session_state.current_module = 'attendus'
            st.rerun()
        st.caption("Import CSV + saisie manuelle conditionnement")
    
    st.markdown("---")
    
    # BLOC 2 : MODULES TRANSPORTEURS
    st.markdown("### 🚛 Modules Transporteurs")
    st.markdown("*Analyse des factures et croisements par transporteur*")
    st.markdown("")
    
    # Charger tous les logos en base64
    logos = {}
    for carrier in ['dpd', 'mondial_relay', 'colissimo', 'colis_prive', 'chronopost', 'dhl']:
        logo_data = get_carrier_logo_base64(carrier)
        if logo_data:
            logos[carrier] = logo_data
    
    # Injecter CSS global pour tous les boutons-logos
    st.markdown("""
    <style>
    /* Style de base pour tous les boutons transporteurs */
    .stButton > button[data-testid="baseButton-primary"] {
        background-color: white !important;
        border: 2px solid #e0e0e0 !important;
        border-radius: 8px !important;
        min-height: 70px !important;
        padding: 12px !important;
        transition: all 0.3s !important;
        background-size: contain !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
    }
    
    .stButton > button[data-testid="baseButton-primary"]:hover {
        border-color: #6BBFA3 !important;
        box-shadow: 0 2px 8px rgba(107, 191, 163, 0.3) !important;
        transform: translateY(-2px) !important;
        background-color: white !important;
    }
    
    /* Cacher le texte des boutons */
    .stButton > button[data-testid="baseButton-primary"] p {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # DPD
        if 'dpd' in logos:
            logo_b64, mime = logos['dpd']
            st.markdown(f'<style>button[key="btn_dpd"] {{ background-image: url("data:{mime};base64,{logo_b64}") !important; }}</style>', unsafe_allow_html=True)
            if st.button("DPD", key="btn_dpd", type="primary", use_container_width=True):
                st.session_state.current_module = 'dpd'
                st.rerun()
        st.caption("Analyse avec taxes automatiques")
        
        st.markdown("")
        
        # Colis Privé
        if 'colis_prive' in logos:
            logo_b64, mime = logos['colis_prive']
            st.markdown(f'<style>button[key="btn_cp"] {{ background-image: url("data:{mime};base64,{logo_b64}") !important; }}</style>', unsafe_allow_html=True)
            if st.button("Colis Privé", key="btn_cp", type="primary", use_container_width=True):
                st.session_state.current_module = 'colis_prive'
                st.rerun()
        st.caption("Croisement avec détection majorations")
    
    with col2:
        # Mondial Relay
        if 'mondial_relay' in logos:
            logo_b64, mime = logos['mondial_relay']
            st.markdown(f'<style>button[key="btn_mr"] {{ background-image: url("data:{mime};base64,{logo_b64}") !important; }}</style>', unsafe_allow_html=True)
            if st.button("Mondial Relay", key="btn_mr", type="primary", use_container_width=True):
                st.session_state.current_module = 'mondial_relay'
                st.rerun()
        st.caption("Gestion retours TOOPOST avec taxe fuel")
        
        st.markdown("")
        
        # Colissimo
        if 'colissimo' in logos:
            logo_b64, mime = logos['colissimo']
            st.markdown(f'<style>button[key="btn_col"] {{ background-image: url("data:{mime};base64,{logo_b64}") !important; }}</style>', unsafe_allow_html=True)
            if st.button("Colissimo", key="btn_col", type="primary", use_container_width=True):
                st.session_state.current_module = 'colissimo'
                st.rerun()
        st.caption("Gestion retours 8R avec 3 méthodes")
    
    with col3:
        # Chronopost
        if 'chronopost' in logos:
            logo_b64, mime = logos['chronopost']
            st.markdown(f'<style>button[key="btn_chrono"] {{ background-image: url("data:{mime};base64,{logo_b64}") !important; }}</style>', unsafe_allow_html=True)
            if st.button("Chronopost", key="btn_chrono", type="primary", use_container_width=True):
                st.session_state.current_module = 'chronopost'
                st.rerun()
        st.caption("Analyse factures avec écarts et surplus")
        
        st.markdown("")
        
        # DHL
        if 'dhl' in logos:
            logo_b64, mime = logos['dhl']
            st.markdown(f'<style>button[key="btn_dhl"] {{ background-image: url("data:{mime};base64,{logo_b64}") !important; }}</style>', unsafe_allow_html=True)
            if st.button("DHL", key="btn_dhl", type="primary", use_container_width=True):
                st.session_state.current_module = 'dhl'
                st.rerun()
        st.caption("Facturation avec frais supplémentaires")
    
    # Stats
    st.markdown("---")
    st.markdown("### 📊 Statistiques")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Modules disponibles", "10")
    with col2:
        # Compter les fichiers dans la bibliothèque logisticiens
        from modules.logisticiens_library import get_all_available_periods
        nb_files = len(get_all_available_periods())
        st.metric("Fichiers logisticiens", nb_files)
    with col3:
        modules_data = len([k for k in st.session_state.module_data.keys()])
        st.metric("Modules avec données", modules_data)
    
    # Export global multi-transporteurs
    from modules import export_global
    export_global.run_export_interface()
    
    # Zone dangereuse - Réinitialisation
    st.markdown("---")
    with st.expander("⚠️ Zone Dangereuse - Réinitialisation", expanded=False):
        st.warning("""
        **Attention : Réinitialisation partielle**
        
        Cette action supprimera :
        - ❌ Les données en cours (session en mémoire)
        - ❌ Les fichiers uploadés temporaires
        
        Cette action préservera :
        - ✅ **Bibliothèque des analyses** (toutes vos analyses archivées)
        - ✅ **Bibliothèque logisticiens** (tous vos fichiers logisticiens)
        - ✅ **Indemnisations "En attente"** (suivi en cours)
        
        **Recommandation** : Utilisez cette fonction uniquement si vous rencontrez des problèmes techniques.
        """)
        
        col1, col2 = st.columns([2, 1])
        with col2:
            if st.button("🗑️ Réinitialiser Session", type="secondary", use_container_width=True):
                # Sauvegarder les indemnisations "En attente" avant réinitialisation
                indemnisations_en_attente = None
                
                # Charger les indemnisations existantes
                saved_indem = persistence.load_module_data('indemnisations')
                if saved_indem and 'df' in saved_indem:
                    df_indem = saved_indem['df']
                    # Filtrer pour ne garder que les "En attente"
                    if len(df_indem) > 0 and 'Statut' in df_indem.columns:
                        df_en_attente = df_indem[df_indem['Statut'] == 'En attente'].copy()
                        if len(df_en_attente) > 0:
                            indemnisations_en_attente = df_en_attente
                
                # Afficher un message si des indemnisations "En attente" existent
                if indemnisations_en_attente is not None and len(indemnisations_en_attente) > 0:
                    st.info(f"ℹ️ {len(indemnisations_en_attente)} indemnisation(s) 'En attente' préservées")
                
                # Supprimer sauvegardes temporaires SAUF bibliothèques
                persistence.delete_all_saved_data()
                
                # Re-sauvegarder les indemnisations "En attente" si elles existent
                if indemnisations_en_attente is not None and len(indemnisations_en_attente) > 0:
                    persistence.save_module_data('indemnisations', {
                        'df': indemnisations_en_attente
                    })
                
                # Effacer le session_state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                
                st.success("✅ Session réinitialisée (bibliothèques et indemnisations 'En attente' préservées)")
                st.rerun()
    
    # Zone Sauvegarde & Restauration
    st.markdown("---")
    with st.expander("💾 Sauvegarde & Restauration des Données", expanded=False):
        st.info("""
        **Protection de vos données lors des mises à jour**
        
        Ce module vous permet de :
        - 💾 **Sauvegarder** toutes vos données avant une mise à jour
        - 📥 **Restaurer** vos données après une mise à jour
        
        **Contenu de la sauvegarde :**
        - ✅ Bibliothèque des analyses (tous modules)
        - ✅ Fichiers logisticiens partagés
        - ✅ Indemnisations
        - ✅ Toutes vos données
        
        **Utilisation :**
        1. **Avant mise à jour** : Créez une sauvegarde et téléchargez le ZIP
        2. **Après mise à jour** : Restaurez vos données depuis le ZIP
        """)
        
        if st.button("🚀 Ouvrir Sauvegarde & Restauration", type="primary", use_container_width=True):
            st.session_state.current_module = 'backup_restore'
            st.rerun()

# Modules
elif st.session_state.current_module == 'retours':
    from modules import retours
    retours.run()

elif st.session_state.current_module == 'dpd':
    from modules import dpd
    dpd.run()

elif st.session_state.current_module == 'mondial_relay':
    from modules import mondial_relay
    mondial_relay.run()

elif st.session_state.current_module == 'colissimo':
    from modules import colissimo
    colissimo.run()

elif st.session_state.current_module == 'chronopost':
    from modules import chronopost
    chronopost.run()

elif st.session_state.current_module == 'dhl':
    from modules import dhl
    dhl.run()

elif st.session_state.current_module == 'colis_prive':
    from modules import colis_prive
    colis_prive.run()

elif st.session_state.current_module == 'indemnisations':
    from modules import indemnisations
    indemnisations.run()

elif st.session_state.current_module == 'bibliotheque':
    from modules import bibliotheque
    bibliotheque.run()

elif st.session_state.current_module == 'logisticiens_library':
    from modules import logisticiens_library
    logisticiens_library.run()

elif st.session_state.current_module == 'backup_restore':
    from modules import backup_restore
    backup_restore.run()

elif st.session_state.current_module == 'attendus':
    from modules import attendus
    attendus.run()
