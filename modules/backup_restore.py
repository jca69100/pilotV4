"""
Module : Sauvegarde et Restauration des Données
Permet d'exporter et importer toutes les données de l'application
pour faciliter les mises à jour sans perte de données
"""

import streamlit as st
import pickle
import zipfile
from io import BytesIO
from datetime import datetime
from pathlib import Path
import json

def export_all_data():
    """
    Exporte TOUTES les données de l'application dans un fichier ZIP
    Inclut : bibliothèque, indemnisations, fichiers logisticiens, tous les modules
    
    Returns:
        tuple: (BytesIO: zip_buffer, int: files_count, list: files_details)
    """
    zip_buffer = BytesIO()
    files_details = []
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Dossier des données
        data_dir = Path(".greenlog_data")
        
        files_added = 0
        total_size = 0
        
        if not data_dir.exists():
            # Aucune donnée
            zip_file.writestr('README.txt', 'Aucune donnée à sauvegarder - dossier .greenlog_data vide')
        else:
            # Lister TOUS les fichiers .pkl
            all_pkl_files = sorted(data_dir.glob("*.pkl"))
            
            if not all_pkl_files:
                zip_file.writestr('README.txt', 'Aucun fichier .pkl trouvé dans .greenlog_data')
            
            # Sauvegarder CHAQUE fichier .pkl trouvé
            for pkl_file in all_pkl_files:
                try:
                    # Lire le fichier
                    with open(pkl_file, 'rb') as f:
                        data = f.read()
                    
                    file_size = len(data)
                    
                    # Ajouter au ZIP avec le chemin complet
                    zip_path = f"data/{pkl_file.name}"
                    zip_file.writestr(zip_path, data)
                    
                    files_added += 1
                    total_size += file_size
                    
                    # Identifier le type de données
                    file_type = "Autre"
                    if 'indemnisation' in pkl_file.name.lower():
                        file_type = "💶 Indemnisations"
                    elif 'library' in pkl_file.name.lower() and 'logisticien' not in pkl_file.name.lower():
                        file_type = "📚 Bibliothèque Analyses"
                    elif 'logisticien' in pkl_file.name.lower():
                        file_type = "📋 Fichiers Logisticiens"
                    elif pkl_file.name.endswith('_files.pkl'):
                        module = pkl_file.name.replace('_files.pkl', '')
                        file_type = f"📁 Fichiers {module.upper()}"
                    elif pkl_file.name.endswith('_data.pkl'):
                        module = pkl_file.name.replace('_data.pkl', '')
                        file_type = f"📊 Données {module.upper()}"
                    
                    files_details.append({
                        'name': pkl_file.name,
                        'type': file_type,
                        'size': file_size,
                        'size_kb': round(file_size / 1024, 2)
                    })
                    
                except Exception as e:
                    error_msg = f"Erreur sauvegarde {pkl_file.name}: {str(e)}"
                    zip_file.writestr(f"errors/{pkl_file.name}.txt", error_msg)
                    files_details.append({
                        'name': pkl_file.name,
                        'type': '❌ ERREUR',
                        'size': 0,
                        'size_kb': 0,
                        'error': str(e)
                    })
        
        # Ajouter métadonnées complètes
        metadata = {
            'export_date': datetime.now().isoformat(),
            'version': 'pilot by GREENLOG v1.0',
            'files_count': files_added,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'data_directory': str(data_dir),
            'files_details': files_details,
            'categories': {
                'indemnisations': len([f for f in files_details if 'indemnisation' in f['name'].lower()]),
                'bibliotheque': len([f for f in files_details if 'library' in f['name'].lower() and 'logisticien' not in f['name'].lower()]),
                'logisticiens': len([f for f in files_details if 'logisticien' in f['name'].lower()]),
                'modules_data': len([f for f in files_details if f['name'].endswith('_data.pkl')]),
                'modules_files': len([f for f in files_details if f['name'].endswith('_files.pkl')])
            }
        }
        
        zip_file.writestr('metadata.json', json.dumps(metadata, indent=2, ensure_ascii=False))
        
        # Ajouter un README explicatif
        readme = f"""
SAUVEGARDE PILOT BY GREENLOG
=============================

Date de création: {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}
Nombre de fichiers: {files_added}
Taille totale: {round(total_size / (1024 * 1024), 2)} MB

CONTENU:
--------
{chr(10).join([f"- {f['type']}: {f['name']} ({f['size_kb']} KB)" for f in files_details])}

RESTAURATION:
-------------
1. Ouvrir pilot by GREENLOG
2. Aller dans "Sauvegarde & Restauration"
3. Onglet "Restaurer"
4. Upload de ce fichier ZIP
5. Cliquer "Restaurer les données"
6. Recharger la page (F5)
"""
        zip_file.writestr('README.txt', readme)
    
    zip_buffer.seek(0)
    return zip_buffer, files_added, files_details

def import_all_data(uploaded_file):
    """
    Importe toutes les données depuis un fichier ZIP de sauvegarde
    
    Args:
        uploaded_file: Fichier ZIP uploadé
        
    Returns:
        tuple: (success: bool, message: str, files_count: int)
    """
    try:
        # Créer dossier .greenlog_data s'il n'existe pas
        data_dir = Path(".greenlog_data")
        data_dir.mkdir(exist_ok=True)
        
        files_restored = 0
        
        with zipfile.ZipFile(uploaded_file, 'r') as zip_file:
            # Lire métadonnées
            try:
                metadata_content = zip_file.read('metadata.json')
                metadata = json.loads(metadata_content)
                export_date = metadata.get('export_date', 'Inconnue')
                original_files = metadata.get('files_count', 0)
            except:
                export_date = 'Inconnue'
                original_files = 0
            
            # Restaurer tous les fichiers .pkl
            for file_info in zip_file.namelist():
                if file_info.startswith('data/') and file_info.endswith('.pkl'):
                    # Extraire le nom du fichier
                    filename = Path(file_info).name
                    
                    # Lire le contenu
                    content = zip_file.read(file_info)
                    
                    # Écrire dans le dossier .greenlog_data
                    with open(data_dir / filename, 'wb') as f:
                        f.write(content)
                    
                    files_restored += 1
        
        if files_restored == 0:
            return False, "❌ Aucun fichier de données trouvé dans la sauvegarde", 0
        
        return True, f"✅ Restauration réussie !\n\n{files_restored} fichier(s) restauré(s) depuis la sauvegarde du {export_date}\n\n**Important** : Rechargez la page (F5) pour voir vos données", files_restored
    
    except Exception as e:
        return False, f"❌ Erreur lors de la restauration : {str(e)}", 0

def run():
    """Interface du module Sauvegarde/Restauration"""
    
    st.title("💾 Sauvegarde et Restauration des Données")
    
    # Section Sauvegarde Automatique
    st.markdown("### 🤖 Sauvegarde Automatique")
    
    auto_backup_enabled = st.toggle(
        "Activer les sauvegardes automatiques",
        value=st.session_state.get('auto_backup_enabled', True),  # Activé par défaut
        help="Crée automatiquement une sauvegarde après chaque modification importante"
    )
    
    st.session_state.auto_backup_enabled = auto_backup_enabled
    
    if auto_backup_enabled:
        st.success("""
        ✅ **Sauvegardes automatiques activées**
        
        Une sauvegarde sera créée automatiquement :
        - Après chaque nouvelle analyse archivée
        - Après ajout de fichiers logisticiens
        - Après ajout d'indemnisations
        - Toutes les 24 heures minimum
        
        Vous recevrez une notification en haut de page avec un bouton pour télécharger la sauvegarde.
        """)
    else:
        st.info("""
        ℹ️ **Sauvegardes automatiques désactivées**
        
        Vous devez créer manuellement vos sauvegardes ci-dessous.
        """)
    
    st.markdown("---")
    
    st.warning("""
    ⚠️ **IMPORTANT - Streamlit Cloud** ⚠️
    
    Sur Streamlit Cloud, les données sont stockées de manière **temporaire** dans le dossier `.greenlog_data`.
    
    **Ce qui conserve vos données** :
    - ✅ Navigation dans l'application
    - ✅ Rechargement de la page (F5)
    - ✅ Pendant que l'application tourne
    
    **Ce qui EFFACE vos données** :
    - ❌ **Reboot de l'application** (Menu ⋮ → Reboot app)
    - ❌ **Redéploiement** complet
    - ❌ **Mise à jour** du code
    
    💡 **Solution** : TOUJOURS faire une sauvegarde AVANT un Reboot ou une mise à jour !
    """)
    
    st.markdown("""
    ### 📋 À quoi sert ce module ?
    
    Ce module vous permet de **sauvegarder toutes vos données** avant une mise à jour de l'application,
    et de les **restaurer** après la mise à jour.
    
    **Pourquoi c'est important ?**
    - 🔒 Vos données sont protégées
    - 🔄 Vous pouvez mettre à jour l'application sans risque
    - 📦 Toutes vos données en un seul fichier
    """)
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2 = st.tabs(["💾 Sauvegarder", "📥 Restaurer"])
    
    with tab1:
        st.subheader("💾 Sauvegarder toutes les données")
        
        st.markdown("""
        ### 📦 Que contient la sauvegarde ?
        
        La sauvegarde inclut **TOUTES** vos données :
        - ✅ Bibliothèque des analyses (tous les modules)
        - ✅ Fichiers logisticiens partagés
        - ✅ Indemnisations (toutes les déclarations)
        - ✅ Données temporaires des modules
        - ✅ Configuration et préférences
        
        ### 🔄 Quand faire une sauvegarde ?
        
        **AVANT chaque mise à jour de l'application !**
        
        1. Cliquez sur **"Télécharger la sauvegarde"** ci-dessous
        2. Conservez le fichier ZIP sur votre ordinateur
        3. Faites la mise à jour de l'application
        4. Restaurez vos données avec l'onglet "Restaurer"
        """)
        
        st.markdown("---")
        
        # Section de diagnostic
        with st.expander("🔍 Diagnostic - Voir les données actuelles"):
            st.markdown("**Fichiers actuellement présents dans `.greenlog_data` :**")
            
            data_dir = Path(".greenlog_data")
            if not data_dir.exists():
                st.warning("⚠️ Le dossier `.greenlog_data` n'existe pas encore")
                st.info("Utilisez d'abord les modules pour créer des données")
            else:
                all_pkl = sorted(data_dir.glob("*.pkl"))
                if not all_pkl:
                    st.warning("⚠️ Aucun fichier .pkl trouvé")
                else:
                    st.success(f"✅ {len(all_pkl)} fichier(s) trouvé(s)")
                    
                    for pkl_file in all_pkl:
                        size_kb = pkl_file.stat().st_size / 1024
                        
                        # Identifier le type
                        if 'indemnisation' in pkl_file.name.lower():
                            icon = "💶"
                            label = "Indemnisations"
                        elif 'library' in pkl_file.name and 'logisticien' not in pkl_file.name:
                            icon = "📚"
                            label = "Bibliothèque"
                        elif 'logisticien' in pkl_file.name:
                            icon = "📋"
                            label = "Logisticiens"
                        elif '_data.pkl' in pkl_file.name:
                            icon = "📊"
                            label = "Données module"
                        elif '_files.pkl' in pkl_file.name:
                            icon = "📁"
                            label = "Fichiers module"
                        else:
                            icon = "📄"
                            label = "Autre"
                        
                        st.write(f"{icon} `{pkl_file.name}` - {size_kb:.2f} KB - {label}")
                    
                    # Vérification spécifique indemnisations
                    has_indemnisations = any('indemnisation' in f.name.lower() for f in all_pkl)
                    if has_indemnisations:
                        st.success("✅ **Indemnisations présentes - elles SERONT sauvegardées**")
                    else:
                        st.info("ℹ️ Pas d'indemnisations - créez-en d'abord dans le module Indemnisations")
        
        st.markdown("---")
        
        # Bouton de sauvegarde
        if st.button("💾 Créer la sauvegarde", type="primary", use_container_width=True):
            with st.spinner("Création de la sauvegarde..."):
                try:
                    # Exporter toutes les données
                    backup_zip, files_count, files_list = export_all_data()
                    
                    if files_count == 0:
                        st.warning("⚠️ Aucune donnée à sauvegarder. La bibliothèque est vide.")
                        st.info("""
                        💡 **Conseil** : Pour avoir des données à sauvegarder :
                        - Utilisez d'abord les modules d'analyse
                        - Importez des fichiers logisticiens
                        - Créez des indemnisations
                        - Puis revenez ici pour faire une sauvegarde
                        """)
                    else:
                        # Nom du fichier
                        backup_filename = f"pilot_GREENLOG_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                        
                        st.success(f"✅ Sauvegarde créée avec succès ! **{files_count} fichier(s)** inclus")
                        
                        # Afficher la liste détaillée des fichiers
                        with st.expander("📋 Détail de la sauvegarde", expanded=True):
                            st.markdown("**Contenu de la sauvegarde :**")
                            
                            # Grouper par catégorie
                            categories = {}
                            for file_info in files_list:
                                cat = file_info['type']
                                if cat not in categories:
                                    categories[cat] = []
                                categories[cat].append(file_info)
                            
                            # Afficher par catégorie
                            for category, files in sorted(categories.items()):
                                st.markdown(f"**{category}**")
                                for f in files:
                                    if 'error' in f:
                                        st.error(f"❌ {f['name']} - Erreur: {f['error']}")
                                    else:
                                        st.write(f"  • `{f['name']}` - {f['size_kb']} KB")
                            
                            # Résumé
                            total_kb = sum([f['size_kb'] for f in files_list if 'error' not in f])
                            st.markdown(f"**Total : {total_kb:.2f} KB ({total_kb/1024:.2f} MB)**")
                            
                            # Vérification spécifique pour indemnisations
                            indemnisations_files = [f for f in files_list if 'indemnisation' in f['name'].lower()]
                            if indemnisations_files:
                                st.success(f"✅ Indemnisations sauvegardées : {len(indemnisations_files)} fichier(s)")
                                for f in indemnisations_files:
                                    st.write(f"  → {f['name']} ({f['size_kb']} KB)")
                            else:
                                st.warning("⚠️ Aucune indemnisation trouvée - normal si vous n'en avez pas encore créé")
                        
                        # Bouton de téléchargement
                        st.download_button(
                            label="📥 Télécharger la sauvegarde",
                            data=backup_zip,
                            file_name=backup_filename,
                            mime="application/zip",
                            use_container_width=True
                        )
                        
                        st.info("💡 **Important** : Conservez ce fichier dans un endroit sûr (ordinateur, cloud, clé USB)")
                    
                except Exception as e:
                    st.error(f"❌ Erreur lors de la création de la sauvegarde : {str(e)}")
                    st.error("**Debug info** : Vérifiez que le dossier `.greenlog_data` existe et contient des fichiers")
    
    with tab2:
        st.subheader("📥 Restaurer les données")
        
        st.markdown("""
        ### 🔄 Comment restaurer vos données ?
        
        **Après une mise à jour de l'application :**
        
        1. Uploadez le fichier ZIP de sauvegarde ci-dessous
        2. Cliquez sur "Restaurer les données"
        3. Attendez la confirmation
        4. **Rechargez la page** (F5) pour voir vos données
        
        ⚠️ **Attention** : La restauration écrasera les données actuelles
        """)
        
        st.markdown("---")
        
        # Upload du fichier
        uploaded_file = st.file_uploader(
            "📁 Sélectionnez votre fichier de sauvegarde (.zip)",
            type=['zip'],
            help="Fichier ZIP créé avec l'onglet 'Sauvegarder'"
        )
        
        if uploaded_file is not None:
            st.success(f"✅ Fichier chargé : {uploaded_file.name}")
            
            # Bouton de restauration
            if st.button("🔄 Restaurer les données", type="primary", use_container_width=True):
                with st.spinner("Restauration en cours..."):
                    success, message, files_count = import_all_data(uploaded_file)
                    
                    if success:
                        st.success(message)
                        st.balloons()
                        
                        st.markdown("---")
                        st.info("🔄 **Dernière étape** : Rechargez la page (appuyez sur F5) pour voir vos données restaurées")
                        
                        if st.button("🔄 Recharger la page maintenant", use_container_width=True):
                            st.rerun()
                    else:
                        st.error(message)
    
    # Section informations
    st.markdown("---")
    
    with st.expander("ℹ️ Informations et bonnes pratiques"):
        st.markdown("""
        ### 📝 Bonnes pratiques
        
        **Sauvegarde régulière :**
        - ✅ Avant chaque mise à jour de l'application
        - ✅ Une fois par semaine pour sécurité
        - ✅ Après chaque gros import de données
        
        **Conservation des sauvegardes :**
        - 💾 Gardez plusieurs sauvegardes (3 dernières minimum)
        - ☁️ Stockez-les dans un cloud (Google Drive, Dropbox, etc.)
        - 💻 Gardez une copie locale sur votre ordinateur
        
        **Format du fichier :**
        - 📦 Format : ZIP compressé
        - 📊 Contenu : Tous les fichiers .pkl de données
        - 📄 Métadonnées : Date d'export, version, nombre de fichiers
        
        ### 🔐 Sécurité
        
        - Les sauvegardes contiennent toutes vos données sensibles
        - Ne partagez pas vos fichiers de sauvegarde
        - Stockez-les dans un endroit sécurisé
        
        ### 🆘 En cas de problème
        
        Si la restauration ne fonctionne pas :
        1. Vérifiez que le fichier ZIP n'est pas corrompu
        2. Essayez avec une sauvegarde plus ancienne
        3. Contactez le support avec le message d'erreur
        """)
    
    # Section guide de mise à jour
    st.markdown("---")
    
    with st.expander("📖 Guide complet de mise à jour"):
        st.markdown("""
        ## 🔄 Guide pas à pas pour mettre à jour l'application
        
        ### Étape 1 : Préparation (AVANT la mise à jour)
        
        1. **Créer une sauvegarde**
           - Allez dans l'onglet "Sauvegarder"
           - Cliquez sur "Créer la sauvegarde"
           - Téléchargez le fichier ZIP
           - Vérifiez que le téléchargement est complet
        
        2. **Conservez le fichier**
           - Notez le nom du fichier (avec la date)
           - Stockez-le dans un endroit sûr
           - Ne fermez pas encore l'application
        
        ### Étape 2 : Mise à jour (sur Streamlit Cloud)
        
        **Option A : Mise à jour simple (RECOMMANDÉ)**
        
        1. Sur Streamlit Cloud, cliquez sur "⋮" (menu)
        2. Sélectionnez "Reboot app"
        3. Attendez le redémarrage (1-2 minutes)
        4. ✅ Vos données sont conservées automatiquement !
        
        **Option B : Mise à jour complète (si nécessaire)**
        
        1. Sur GitHub, uploadez la nouvelle version
        2. Sur Streamlit Cloud, l'app se met à jour automatiquement
        3. Attendez le déploiement complet
        4. Passez à l'étape 3 pour restaurer vos données
        
        ### Étape 3 : Restauration (APRÈS la mise à jour)
        
        **Si Option A (Reboot) :**
        - ✅ Rien à faire ! Vos données sont là
        
        **Si Option B (Mise à jour complète) :**
        
        1. Ouvrez l'application mise à jour
        2. Allez dans "Sauvegarde et Restauration"
        3. Onglet "Restaurer"
        4. Uploadez votre fichier ZIP de sauvegarde
        5. Cliquez sur "Restaurer les données"
        6. Attendez le message de confirmation
        7. Rechargez la page (F5)
        8. ✅ Toutes vos données sont de retour !
        
        ### Étape 4 : Vérification
        
        1. **Vérifiez la bibliothèque**
           - Module "Sauvegarde des Analyses"
           - Vérifiez que vos analyses sont présentes
        
        2. **Vérifiez les indemnisations**
           - Module "Indemnisations"
           - Vérifiez vos déclarations
        
        3. **Vérifiez les fichiers logisticiens**
           - Module "Import Fichier Logisticien"
           - Vérifiez vos fichiers partagés
        
        ### ⚠️ Important
        
        - **Toujours faire une sauvegarde avant mise à jour**
        - Gardez plusieurs sauvegardes (3 dernières)
        - En cas de doute, contactez le support
        - Ne supprimez jamais vos anciennes sauvegardes
        
        ### 🆘 Que faire en cas de problème ?
        
        **Problème 1 : Données perdues après mise à jour**
        - ✅ Solution : Restaurez votre dernière sauvegarde
        
        **Problème 2 : La restauration ne fonctionne pas**
        - ✅ Solution : Essayez une sauvegarde plus ancienne
        - ✅ Solution : Vérifiez que le fichier ZIP n'est pas corrompu
        
        **Problème 3 : L'application ne démarre plus**
        - ✅ Solution : Redéployez la version précédente
        - ✅ Solution : Contactez le support
        """)
