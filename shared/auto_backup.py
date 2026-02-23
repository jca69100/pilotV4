"""
Système de Sauvegarde Automatique
Crée des sauvegardes automatiques après chaque action importante
"""

import streamlit as st
from datetime import datetime
from pathlib import Path
import zipfile
from io import BytesIO
import json

class AutoBackup:
    """Gestionnaire de sauvegardes automatiques"""
    
    @staticmethod
    def should_auto_backup():
        """
        Détermine si une sauvegarde automatique doit être créée
        
        Critères :
        - Nouvelle analyse archivée
        - Nouveau fichier logisticien
        - Nouvelle indemnisation
        - Pas de sauvegarde depuis > 24h
        """
        # Vérifier la dernière sauvegarde
        last_backup = st.session_state.get('last_auto_backup', None)
        
        if last_backup is None:
            return True
        
        # Vérifier si > 24h depuis dernière sauvegarde
        from datetime import timedelta
        if datetime.now() - last_backup > timedelta(hours=24):
            return True
        
        return False
    
    @staticmethod
    def create_auto_backup():
        """
        Crée une sauvegarde automatique
        
        Returns:
            tuple: (BytesIO: backup_zip, int: files_count, str: filename)
        """
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            data_dir = Path(".greenlog_data")
            files_added = 0
            
            if data_dir.exists():
                for pkl_file in data_dir.glob("*.pkl"):
                    try:
                        with open(pkl_file, 'rb') as f:
                            data = f.read()
                        
                        zip_file.writestr(f"data/{pkl_file.name}", data)
                        files_added += 1
                    except Exception:
                        pass
            
            # Métadonnées
            metadata = {
                'export_date': datetime.now().isoformat(),
                'version': 'pilot by GREENLOG v1.0',
                'files_count': files_added,
                'backup_type': 'automatic',
                'data_directory': '.greenlog_data'
            }
            
            zip_file.writestr('metadata.json', json.dumps(metadata, indent=2))
        
        zip_buffer.seek(0)
        filename = f"pilot_AUTO_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        
        # Mettre à jour le timestamp
        st.session_state.last_auto_backup = datetime.now()
        
        return zip_buffer, files_added, filename
    
    @staticmethod
    def trigger_auto_backup(reason="Modification importante détectée"):
        """
        Déclenche une sauvegarde automatique et affiche la notification
        
        Args:
            reason: Raison de la sauvegarde
        """
        # Vérifier si les sauvegardes automatiques sont activées
        if not st.session_state.get('auto_backup_enabled', False):
            return False
        
        try:
            backup_zip, files_count, filename = AutoBackup.create_auto_backup()
            
            if files_count > 0:
                # Stocker la sauvegarde dans session_state pour téléchargement
                st.session_state.pending_auto_backup = {
                    'zip': backup_zip,
                    'filename': filename,
                    'files_count': files_count,
                    'reason': reason,
                    'timestamp': datetime.now()
                }
                
                return True
            
        except Exception as e:
            # Silencieusement ignorer les erreurs de sauvegarde auto
            return False
        
        return False
    
    @staticmethod
    def show_auto_backup_notification():
        """
        Affiche la notification de sauvegarde automatique si disponible
        """
        if 'pending_auto_backup' in st.session_state:
            backup_info = st.session_state.pending_auto_backup
            
            # Créer une notification persistante en haut de page
            st.toast("💾 Sauvegarde automatique créée !", icon="✅")
            
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.info(f"""
                    💾 **Sauvegarde automatique disponible**
                    
                    {backup_info['reason']} - {backup_info['files_count']} fichier(s)
                    """)
                
                with col2:
                    st.download_button(
                        label="📥 Télécharger",
                        data=backup_info['zip'],
                        file_name=backup_info['filename'],
                        mime="application/zip",
                        key=f"auto_backup_{backup_info['timestamp'].timestamp()}"
                    )
                
                with col3:
                    if st.button("✕ Ignorer", key="dismiss_auto_backup"):
                        del st.session_state.pending_auto_backup
                        st.rerun()
    
    @staticmethod
    def cleanup_old_session_backups():
        """Nettoie les anciennes sauvegardes en session"""
        # Garde seulement la dernière
        keys_to_remove = [k for k in st.session_state.keys() 
                         if k.startswith('auto_backup_') and k != 'pending_auto_backup']
        for key in keys_to_remove:
            del st.session_state[key]


def trigger_backup_after_save(module_name, action_description):
    """
    Fonction helper pour déclencher une sauvegarde après une action importante
    
    Args:
        module_name: Nom du module (ex: 'dpd', 'indemnisations')
        action_description: Description de l'action (ex: 'Nouvelle analyse DPD')
    
    Usage:
        from shared.auto_backup import trigger_backup_after_save
        
        # Après avoir sauvegardé des données importantes
        trigger_backup_after_save('dpd', 'Analyse DPD archivée')
    """
    reason = f"{action_description} - {module_name}"
    AutoBackup.trigger_auto_backup(reason)
