"""
Système Keep-Alive pour éviter la mise en veille
Garde l'application active sur Streamlit Cloud
"""

import streamlit as st
from datetime import datetime
import time

def add_keep_alive_script():
    """
    Ajoute un script JavaScript pour garder l'application active
    Rafraîchit automatiquement la page toutes les 4 heures
    """
    
    # Script JavaScript pour auto-refresh
    keep_alive_js = """
    <script>
    // Keep-Alive pour pilot by GREENLOG
    
    // Rafraîchir la page toutes les 4 heures (14400000 ms)
    // Cela évite la mise en veille de Streamlit Cloud
    const REFRESH_INTERVAL = 14400000; // 4 heures
    
    // Ping toutes les 30 minutes pour garder la connexion active
    const PING_INTERVAL = 1800000; // 30 minutes
    
    // Fonction pour envoyer un ping
    function sendPing() {
        // Simule une interaction utilisateur
        const event = new Event('mousemove');
        document.dispatchEvent(event);
        
        console.log('[Keep-Alive] Ping envoyé:', new Date().toLocaleTimeString());
    }
    
    // Fonction pour rafraîchir la page
    function refreshPage() {
        console.log('[Keep-Alive] Auto-refresh de la page');
        window.location.reload();
    }
    
    // Démarrer les intervalles
    setInterval(sendPing, PING_INTERVAL);
    setInterval(refreshPage, REFRESH_INTERVAL);
    
    console.log('[Keep-Alive] Système activé - Ping: 30min, Refresh: 4h');
    </script>
    """
    
    st.markdown(keep_alive_js, unsafe_allow_html=True)


def show_keep_alive_status():
    """
    Affiche le statut du système keep-alive
    """
    
    if 'keep_alive_enabled' not in st.session_state:
        st.session_state.keep_alive_enabled = True
    
    if 'keep_alive_start' not in st.session_state:
        st.session_state.keep_alive_start = datetime.now()
    
    # Calculer uptime
    uptime = datetime.now() - st.session_state.keep_alive_start
    hours = int(uptime.total_seconds() // 3600)
    minutes = int((uptime.total_seconds() % 3600) // 60)
    
    return f"⏱️ Active depuis {hours}h {minutes}min"


def add_keep_alive_settings():
    """
    Ajoute les paramètres keep-alive dans la sidebar
    """
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚡ Maintien de l'App")
    
    keep_alive = st.sidebar.toggle(
        "Keep-Alive",
        value=st.session_state.get('keep_alive_enabled', True),
        help="Garde l'application active (auto-refresh toutes les 4h)"
    )
    
    st.session_state.keep_alive_enabled = keep_alive
    
    if keep_alive:
        status = show_keep_alive_status()
        st.sidebar.caption(f"✅ {status}")
        st.sidebar.caption("🔄 Refresh: 4h | 📡 Ping: 30min")
        
        # Ajouter le script JS
        add_keep_alive_script()
    else:
        st.sidebar.caption("⚠️ App peut se mettre en veille")
