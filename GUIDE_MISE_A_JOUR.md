# 🔄 GUIDE DE MISE À JOUR - pilot by GREENLOG

## ⚠️ IMPORTANT : STREAMLIT CLOUD ET VOS DONNÉES

### 🚨 Comprendre le stockage sur Streamlit Cloud

**CRITICAL** : Sur Streamlit Cloud, le dossier `.greenlog_data` est **TEMPORAIRE**.

```
✅ VOS DONNÉES RESTENT :
- Pendant que l'app tourne
- Lors des rechargements de page (F5)
- Entre les sessions de navigation

❌ VOS DONNÉES SONT EFFACÉES :
- Lors d'un "Reboot app" (Menu ⋮)
- Lors d'un redéploiement
- Lors d'une mise à jour du code
- Si l'app est inactive trop longtemps
```

### 📋 Règle d'or

**TOUJOURS faire une sauvegarde AVANT un Reboot ou une mise à jour !**

---

## 📋 Vue d'ensemble

### Qu'est-ce qui est sauvegardé ?

Toutes vos données sont automatiquement sauvegardées dans le dossier `data/` :
- ✅ Bibliothèque des analyses (tous les modules)
- ✅ Fichiers logisticiens partagés
- ✅ Indemnisations (toutes les déclarations)
- ✅ Données temporaires des modules
- ✅ Configuration et préférences

### Deux types de mise à jour

1. **Mise à jour simple** (Reboot) → ✅ Données conservées automatiquement
2. **Mise à jour complète** (Redéploiement) → ⚠️ Nécessite sauvegarde/restauration

---

## 🔄 MÉTHODE UNIQUE : Sauvegarde avant TOUT changement

⚠️ **ATTENTION** : Il n'y a qu'UNE SEULE méthode sûre sur Streamlit Cloud !

### Workflow complet (OBLIGATOIRE)

**Étape 1 : AVANT tout changement - Créer la sauvegarde**

1. **Ouvrez l'application**
   ```
   https://votre-app.streamlit.app
   ```

2. **Allez dans le module de sauvegarde**
   - Page d'accueil
   - Bas de page : **"💾 Sauvegarde & Restauration"**
   - Cliquez sur **"🚀 Ouvrir Module"**

3. **Créez la sauvegarde**
   - Onglet "💾 Sauvegarder"
   - Cliquez sur **"Créer la sauvegarde"**
   - Vérifiez le nombre de fichiers (ex: "5 fichier(s) inclus")
   - Cliquez sur **"Télécharger la sauvegarde"**
   - ✅ Fichier téléchargé : `pilot_GREENLOG_backup_YYYYMMDD_HHMMSS.zip`

4. **Conservez le fichier**
   - Stockez-le dans un endroit sûr (Bureau, Documents, Cloud)
   - Notez le nom du fichier (avec la date)

**Étape 2 : Reboot OU Mise à jour**

#### Option A : Simple Reboot
```
1. Sur Streamlit Cloud : Menu "⋮" → "Reboot app"
2. Attendez le redémarrage (1-2 minutes)
```

#### Option B : Mise à jour complète
```
1. Uploadez nouvelle version sur GitHub
2. Streamlit Cloud redéploie automatiquement
3. Attendez fin du déploiement
```

**Étape 3 : APRÈS le changement - Restaurer les données**

1. **Ouvrez l'application**
   ```
   https://votre-app.streamlit.app
   ```

2. **Allez dans Sauvegarde & Restauration**
   - Bas de page : **"💾 Sauvegarde & Restauration"**
   - **"🚀 Ouvrir Module"**

3. **Restaurez vos données**
   - Onglet **"📥 Restaurer"**
   - Cliquez sur **"📁 Sélectionnez votre fichier de sauvegarde"**
   - Sélectionnez votre fichier ZIP
   - Cliquez sur **"🔄 Restaurer les données"**
   - Attendez : "✅ Restauration réussie ! X fichier(s) restauré(s)"

4. **Rechargez la page**
   - Appuyez sur **F5** (ou cliquez sur "Recharger la page")
   - ✅ Toutes vos données sont de retour !

**Étape 4 : Vérification**

Vérifiez que tout est en ordre :

1. **📚 Sauvegarde des Analyses**
   - Vos analyses archivées sont présentes

2. **💶 Indemnisations**
   - Vos déclarations sont là

3. **📋 Import Fichier Logisticien**
   - Vos fichiers partagés sont disponibles

---

## 🔄 MÉTHODE 1 : Mise à jour simple (RECOMMANDÉ)

⚠️ **CETTE MÉTHODE N'EST PLUS RECOMMANDÉE** ⚠️

Le "Reboot" sur Streamlit Cloud **EFFACE** le dossier `.greenlog_data` où sont stockées vos données.

**NE FAITES PAS** :
```
❌ Reboot sans sauvegarde = PERTE DE DONNÉES
```

**FAITES TOUJOURS** :
```
✅ Sauvegarde → Reboot → Restauration
```

---

## 💾 MÉTHODE 2 : Mise à jour complète avec sauvegarde

Cette méthode est maintenant **OBLIGATOIRE** pour toute modification.

1. **Ouvrez l'application**
   ```
   https://votre-app.streamlit.app
   ```

2. **Allez dans le module de sauvegarde**
   - Page d'accueil
   - Section "🛠️ Outils de Gestion"
   - Cliquez sur **"💾 Sauvegarde & Restauration"**

3. **Créez la sauvegarde**
   - Onglet "💾 Sauvegarder"
   - Cliquez sur **"Créer la sauvegarde"**
   - Cliquez sur **"Télécharger la sauvegarde"**
   - ✅ Fichier téléchargé : `pilot_GREENLOG_backup_YYYYMMDD_HHMMSS.zip`

4. **Conservez le fichier**
   - Stockez-le dans un endroit sûr (Bureau, Documents, Cloud)
   - Notez le nom du fichier (avec la date)
   - **NE PAS FERMER** l'application encore

### Étape 2 : Mise à jour de l'application

#### Option A : Via GitHub (si vous utilisez GitHub)

1. **Uploadez la nouvelle version**
   ```bash
   # Dans votre dépôt GitHub
   git add .
   git commit -m "Mise à jour de l'application"
   git push origin main
   ```

2. **Sur Streamlit Cloud**
   - L'application se met à jour automatiquement
   - Attendez le déploiement complet (2-5 minutes)

#### Option B : Via Streamlit Cloud directement

1. **Sur Streamlit Cloud**
   - Menu "⋮" → "Settings"
   - Onglet "Main file"
   - Uploadez les nouveaux fichiers
   - Sauvegardez

### Étape 3 : APRÈS la mise à jour - Restaurer les données

1. **Ouvrez l'application mise à jour**
   ```
   https://votre-app.streamlit.app
   ```

2. **Allez dans Sauvegarde & Restauration**
   - Page d'accueil
   - **"💾 Sauvegarde & Restauration"**

3. **Restaurez vos données**
   - Onglet **"📥 Restaurer"**
   - Cliquez sur **"📁 Sélectionnez votre fichier de sauvegarde"**
   - Sélectionnez votre fichier ZIP
   - Cliquez sur **"🔄 Restaurer les données"**
   - Attendez la confirmation : "✅ Restauration réussie !"

4. **Rechargez la page**
   - Appuyez sur **F5** (ou cliquez sur "Recharger la page")
   - ✅ Toutes vos données sont de retour !

### Étape 4 : Vérification

Vérifiez que tout est en ordre :

1. **📚 Sauvegarde des Analyses**
   - Vos analyses archivées sont présentes

2. **💶 Indemnisations**
   - Vos déclarations sont là

3. **📋 Import Fichier Logisticien**
   - Vos fichiers partagés sont disponibles

---

## 📝 Checklist de mise à jour

Utilisez cette checklist pour ne rien oublier :

### AVANT la mise à jour

- [ ] J'ai créé une sauvegarde complète
- [ ] J'ai téléchargé le fichier ZIP
- [ ] J'ai vérifié que le fichier est complet (>1 KB)
- [ ] J'ai noté le nom du fichier
- [ ] J'ai stocké le fichier dans un endroit sûr

### PENDANT la mise à jour

- [ ] J'ai uploadé/déployé la nouvelle version
- [ ] J'ai attendu la fin du déploiement
- [ ] L'application redémarre correctement

### APRÈS la mise à jour

- [ ] J'ai restauré mes données
- [ ] J'ai rechargé la page (F5)
- [ ] J'ai vérifié mes analyses archivées
- [ ] J'ai vérifié mes indemnisations
- [ ] J'ai vérifié mes fichiers logisticiens
- [ ] ✅ Tout fonctionne !

---

## 🆘 En cas de problème

### Problème 1 : Données perdues après mise à jour

**Symptômes :**
- Les modules sont vides
- Les analyses ont disparu
- Les indemnisations sont absentes

**Solution :**
1. Allez dans **"💾 Sauvegarde & Restauration"**
2. Restaurez votre dernière sauvegarde
3. Rechargez la page (F5)

---

### Problème 2 : La restauration ne fonctionne pas

**Symptômes :**
- Message d'erreur lors de la restauration
- Le fichier ne s'upload pas

**Solutions :**
1. Vérifiez que le fichier ZIP n'est pas corrompu
2. Essayez avec une sauvegarde plus ancienne
3. Vérifiez la taille du fichier (doit être >1 KB)
4. Essayez avec un autre navigateur

---

### Problème 3 : L'application ne démarre plus

**Symptômes :**
- Erreur au démarrage
- Page blanche
- Message d'erreur Python

**Solutions :**
1. Sur Streamlit Cloud : Menu "⋮" → "Reboot app"
2. Si ça ne fonctionne pas : Redéployez la version précédente
3. Contactez le support avec le message d'erreur

---

## 💡 Bonnes pratiques

### Sauvegardes régulières

- ✅ **Avant chaque mise à jour** (obligatoire)
- ✅ **Une fois par semaine** (recommandé)
- ✅ **Après gros imports** (optionnel)

### Conservation des sauvegardes

- 💾 Gardez au moins **3 sauvegardes** (dernières versions)
- ☁️ Stockez dans un **cloud** (Google Drive, Dropbox)
- 💻 Gardez une **copie locale** sur votre ordinateur
- 🗓️ Organisez par **date** dans un dossier dédié

### Organisation

Créez un dossier `Sauvegardes GREENLOG/` avec :
```
Sauvegardes GREENLOG/
├── 2026/
│   ├── 02/
│   │   ├── pilot_GREENLOG_backup_20260220_153045.zip
│   │   ├── pilot_GREENLOG_backup_20260221_090122.zip
│   │   └── pilot_GREENLOG_backup_20260221_220435.zip
```

---

## 🔐 Sécurité

### Important

- ⚠️ Les sauvegardes contiennent **toutes vos données sensibles**
- 🔒 Ne partagez **jamais** vos fichiers de sauvegarde
- 💾 Stockez-les dans un **endroit sécurisé**
- 🗑️ Supprimez les **très anciennes sauvegardes** (>6 mois)

### Recommandations

- Utilisez un mot de passe fort pour votre cloud
- Activez l'authentification à deux facteurs
- Ne stockez pas les sauvegardes sur des ordinateurs publics

---

## 📞 Support

### Besoin d'aide ?

Si vous rencontrez des difficultés :

1. **Consultez ce guide** attentivement
2. **Vérifiez la checklist** étape par étape
3. **Essayez la Méthode 1** (Reboot) d'abord
4. **Contactez le support** avec :
   - Description du problème
   - Message d'erreur exact
   - Étapes déjà effectuées

---

## ✅ Résumé rapide

**Pour une mise à jour simple :**
1. Menu "⋮" → "Reboot app"
2. ✅ Terminé !

**Pour une mise à jour complète :**
1. Sauvegarde → Télécharger ZIP
2. Mise à jour de l'application
3. Restauration → Upload ZIP
4. Recharger la page (F5)
5. ✅ Terminé !

---

**pilot by GREENLOG** - Version 1.0
*Dernière mise à jour : Février 2026*
