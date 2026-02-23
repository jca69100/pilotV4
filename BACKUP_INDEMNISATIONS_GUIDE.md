# 💾 SYSTÈME DE BACKUP COMPLET - pilot by GREENLOG

## ✅ CE QUI EST SAUVEGARDÉ

Le système de backup sauvegarde **TOUS** les fichiers .pkl du dossier `.greenlog_data`, ce qui inclut :

### 📚 Bibliothèque
- `library.pkl` - Toutes vos analyses sauvegardées (tous modules confondus)

### 📋 Fichiers Logisticiens
- `logisticiens_library.pkl` - Tous les fichiers logisticiens uploadés

### 💶 INDEMNISATIONS
- `indemnisations_data.pkl` - **TOUTES vos indemnisations créées**

### 📊 Données des Modules
Pour CHAQUE module (DPD, Chronopost, Colissimo, Colis Privé, DHL, Mondial Relay, Retours) :
- `{module}_data.pkl` - Données analysées du module
- `{module}_files.pkl` - Fichiers uploadés dans le module

## 🔍 VÉRIFIER QUE LES INDEMNISATIONS SERONT SAUVEGARDÉES

### Méthode 1 : Via l'interface (RECOMMANDÉ)

1. Aller dans **"Sauvegarde & Restauration"** (bas de page d'accueil)
2. Onglet **"Sauvegarder"**
3. Ouvrir **"🔍 Diagnostic - Voir les données actuelles"**
4. Vérifier que `indemnisations_data.pkl` apparaît dans la liste

✅ Si vous voyez `💶 indemnisations_data.pkl` → VOS INDEMNISATIONS SERONT SAUVEGARDÉES

❌ Si vous ne le voyez pas → Vous n'avez pas encore créé d'indemnisations

### Méthode 2 : Après création du backup

1. Créer un backup
2. Regarder le **"Détail de la sauvegarde"** qui s'affiche
3. Chercher la ligne avec **"💶 Indemnisations"**

Si vous voyez :
```
✅ Indemnisations sauvegardées : 1 fichier(s)
  → indemnisations_data.pkl (XX KB)
```

Alors vos indemnisations SONT dans le backup !

## ⚠️ POURQUOI LES INDEMNISATIONS PEUVENT SEMBLER ABSENTES

### Raison 1 : Pas encore créées
Si vous n'avez jamais créé d'indemnisation :
- Le fichier `indemnisations_data.pkl` n'existe pas
- Le backup ne peut pas sauvegarder quelque chose qui n'existe pas

**Solution** : Créez au moins une indemnisation d'abord
1. Module "Indemnisations"
2. Onglet "Ajouter"
3. Remplir le formulaire
4. Sauvegarder
5. → Le fichier `indemnisations_data.pkl` est créé
6. → Les backups suivants l'incluront

### Raison 2 : Toutes supprimées
Si vous avez supprimé toutes vos indemnisations "En attente" :
- Le système supprime automatiquement le fichier
- Plus rien à sauvegarder

**Solution** : Gardez au moins une indemnisation en statut "En attente"

### Raison 3 : Ancien backup
Si vous utilisez un ancien backup créé AVANT de créer des indemnisations :
- Les indemnisations récentes ne sont pas dedans

**Solution** : Créez un NOUVEAU backup après avoir créé vos indemnisations

## 📋 WORKFLOW CORRECT

### Pour avoir indemnisations dans backup :

```
1. Créer des indemnisations
   → Module Indemnisations
   → Ajouter au moins une indemnisation
   → ✅ Fichier indemnisations_data.pkl créé

2. Vérifier qu'elles existent
   → Sauvegarde & Restauration
   → 🔍 Diagnostic
   → ✅ indemnisations_data.pkl visible

3. Créer le backup
   → Bouton "Créer la sauvegarde"
   → ✅ Détail montre "Indemnisations sauvegardées"

4. Télécharger le ZIP
   → Contient indemnisations_data.pkl

5. Après restauration
   → Toutes vos indemnisations sont de retour
```

## 🧪 TEST RAPIDE

### Vérifier que tout fonctionne :

1. **Créer une indemnisation de test**
   ```
   Date: Aujourd'hui
   Tracking: TEST123
   Partenaire: Test
   Transporteur: DPD
   Motif: Test backup
   Montant: 10.00
   ```

2. **Vérifier le diagnostic**
   - Sauvegarde & Restauration
   - Diagnostic
   - → Voir `indemnisations_data.pkl` ✅

3. **Créer un backup**
   - Bouton "Créer la sauvegarde"
   - Ouvrir "Détail de la sauvegarde"
   - → Voir "Indemnisations sauvegardées : 1 fichier(s)" ✅

4. **Supprimer l'indemnisation test**
   - Module Indemnisations
   - Supprimer le test
   - ✅ Vous savez que le backup fonctionne !

## 🛠️ FONCTIONNEMENT TECHNIQUE

### Code du backup :

```python
def export_all_data():
    # Parcourt TOUS les fichiers .pkl
    for pkl_file in data_dir.glob("*.pkl"):
        # Sauvegarde CHAQUE fichier trouvé
        # Inclut automatiquement indemnisations_data.pkl
```

### Pas de filtre, pas d'exclusion

Le backup sauvegarde **AVEUGLEMENT** tous les .pkl trouvés :
- ✅ library.pkl
- ✅ logisticiens_library.pkl
- ✅ indemnisations_data.pkl ← TOUJOURS inclus si présent
- ✅ dpd_data.pkl
- ✅ dpd_files.pkl
- ✅ retours_data.pkl
- ✅ ... et TOUS les autres .pkl

### Garantie

Si `indemnisations_data.pkl` existe dans `.greenlog_data/`, il SERA dans le backup.

C'est mathématiquement certain.

## ❓ SI LE PROBLÈME PERSISTE

### Checklist de diagnostic :

- [ ] J'ai créé au moins une indemnisation
- [ ] Le diagnostic montre `indemnisations_data.pkl`
- [ ] Le backup affiche "Indemnisations sauvegardées"
- [ ] J'ai téléchargé le ZIP après sa création
- [ ] Le ZIP contient data/indemnisations_data.pkl

Si TOUS les points sont ✅ mais les indemnisations ne sont pas restaurées :
→ Le problème est dans la RESTAURATION, pas le backup

## 🔄 TESTER LA RESTAURATION

1. Créer indemnisation test
2. Créer backup
3. Supprimer l'indemnisation
4. Restaurer le backup
5. F5 (recharger la page)
6. → L'indemnisation test doit réapparaître

Si elle réapparaît : ✅ Système fonctionne parfaitement
Si elle ne réapparaît pas : ❌ Problème de restauration

## 📞 SUPPORT

Le système de backup sauvegarde TOUT automatiquement.

Si après avoir :
1. Créé des indemnisations
2. Vérifié le diagnostic
3. Créé un backup
4. Vérifié le détail

Les indemnisations ne sont toujours pas sauvegardées, alors il y a un bug à corriger.

Mais normalement, c'est IMPOSSIBLE car le code sauvegarde TOUS les .pkl sans exception.
