# ⚡ ÉVITER LA MISE EN VEILLE - pilot by GREENLOG

## 🎯 Problème : Mise en Veille sur Streamlit Cloud

### Comportement Normal de Streamlit Cloud

```
STREAMLIT COMMUNITY CLOUD (GRATUIT):

Mise en veille si:
├─ Aucun visiteur pendant 5-7 jours
├─ Aucune activité détectée
└─ Resources non utilisées

Conséquences:
├─ App s'arrête
├─ Données temporaires effacées (.greenlog_data/)
└─ Redémarrage lors de la prochaine visite (30-60s)
```

---

## ✅ Solution 1 : Keep-Alive Automatique (INTÉGRÉ)

### **Système Déjà Installé dans l'Application**

**Emplacement** : Sidebar (barre gauche) → Tout en bas

```
┌─────────────────────┐
│ ...                 │
│                     │
│ ─────────────────── │
│                     │
│ ⚡ Maintien de l'App│
│                     │
│ ☑ Keep-Alive       │← Toggle ON/OFF
│                     │
│ ✅ Active depuis    │
│    2h 34min         │
│                     │
│ 🔄 Refresh: 4h      │
│ 📡 Ping: 30min      │
└─────────────────────┘
```

### Comment ça marche ?

```
AVEC KEEP-ALIVE ACTIVÉ:

1. Ping toutes les 30 minutes
   → Simule activité utilisateur
   → Garde connexion active

2. Auto-refresh toutes les 4 heures
   → Recharge la page
   → Réinitialise les timers

3. Application reste active
   → Pas de mise en veille
   → Données conservées
```

### Activation

```
1. Ouvrir pilot by GREENLOG

2. Sidebar (gauche) → Descendre en bas

3. Section "⚡ Maintien de l'App"

4. Activer [☑ Keep-Alive]

5. ✅ Terminé ! L'app restera active
```

### Limitations

```
⚠️ IMPORTANT:

✅ Fonctionne SI:
   • Vous gardez un onglet ouvert
   • Votre ordinateur reste allumé
   • Connexion internet active

❌ NE FONCTIONNE PAS SI:
   • Vous fermez l'onglet
   • Vous éteignez l'ordinateur
   • Connexion internet coupée
```

---

## ✅ Solution 2 : Service de Ping Externe

### **UptimeRobot (Gratuit)**

Service qui visite votre app régulièrement pour la garder active.

**Étapes** :

```
1. Aller sur https://uptimerobot.com

2. Créer un compte gratuit

3. Cliquer "Add New Monitor"

4. Configuration:
   • Monitor Type: HTTP(s)
   • Friendly Name: pilot GREENLOG
   • URL: https://votre-app.streamlit.app
   • Monitoring Interval: 5 minutes

5. Sauvegarder

6. ✅ L'app sera visitée toutes les 5 minutes
```

**Avantages** :
- ✅ Fonctionne 24/7
- ✅ Même si vous fermez votre ordinateur
- ✅ Gratuit (jusqu'à 50 moniteurs)
- ✅ Emails si l'app est down

---

## ✅ Solution 3 : Cron-Job.org (Gratuit)

Service similaire qui ping votre app.

**Étapes** :

```
1. Aller sur https://cron-job.org

2. Créer un compte gratuit

3. Create cronjob:
   • Title: pilot GREENLOG Keep-Alive
   • URL: https://votre-app.streamlit.app
   • Schedule: Every 5 minutes
   
4. Sauvegarder

5. ✅ Ping automatique toutes les 5 minutes
```

---

## ✅ Solution 4 : GitHub Actions (Avancé)

Si votre app est sur GitHub, vous pouvez créer une action qui la visite.

**Créer** `.github/workflows/keep-alive.yml` :

```yaml
name: Keep App Alive

on:
  schedule:
    # Toutes les 4 heures
    - cron: '0 */4 * * *'
  workflow_dispatch:

jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
      - name: Ping App
        run: |
          curl -I https://votre-app.streamlit.app
          echo "App pinged successfully"
```

---

## ✅ Solution 5 : Upgrade vers Plan Payant

### **Streamlit Cloud Plans**

```
COMMUNITY (Gratuit):
├─ Mise en veille après inactivité
├─ Resources limitées
└─ OK pour usage occasionnel

TEAM ($20/mois):
├─ Pas de mise en veille automatique
├─ Resources garanties
├─ Support prioritaire
└─ Idéal pour production

ENTERPRISE (Sur mesure):
├─ Infrastructure dédiée
├─ SLA garanti
└─ Support premium
```

**Pour upgrader** :
1. Streamlit Cloud Dashboard
2. Settings → Billing
3. Choisir plan Team/Enterprise

---

## 🎯 Solution Recommandée (Combinée)

### **Configuration Optimale**

```
1. Keep-Alive Intégré (dans l'app)
   Sidebar → [☑ Keep-Alive]
   → Garde active pendant que vous travaillez

2. + UptimeRobot (externe)
   → Garde active 24/7
   → Même quand vous n'êtes pas là

3. + Sauvegardes Automatiques
   Sidebar → [☑] 🤖 Auto
   → Protection si mise en veille quand même

= PROTECTION MAXIMALE
```

---

## 📋 Workflow Complet

### **Setup Initial (Une fois)**

```
1. Dans pilot by GREENLOG:
   ├─ Sidebar → [☑ Keep-Alive] (activer)
   └─ Sidebar → [☑] 🤖 Auto (sauvegardes)

2. Sur UptimeRobot.com:
   ├─ Créer moniteur
   ├─ URL: https://votre-app.streamlit.app
   └─ Interval: 5 minutes

3. ✅ Configuration terminée
```

### **Utilisation Quotidienne**

```
1. Ouvrir pilot by GREENLOG
   → Keep-Alive actif automatiquement

2. Travailler normalement
   → App reste active

3. Télécharger sauvegardes auto
   → Quand notifications apparaissent

4. Avant de fermer:
   → Sidebar → [Sauvegarder maintenant]
   → [📥 Télécharger]

5. Fermer l'onglet
   → UptimeRobot garde l'app active
```

---

## ⚠️ Important à Savoir

### **Ce Qui Garde l'App Active**

```
✅ OUI:
├─ Keep-Alive intégré (onglet ouvert)
├─ UptimeRobot/Cron-Job (externe)
├─ Visites régulières d'utilisateurs
└─ Plan Team/Enterprise

❌ NON:
├─ Juste ouvrir l'app une fois
├─ Espérer que ça reste actif
└─ Compter sur Streamlit gratuit
```

### **Données vs Application**

```
APPLICATION ACTIVE:
├─ Processus Python tourne
├─ Connexions maintenues
└─ Pas de redémarrage

DONNÉES CONSERVÉES:
├─ Dossier .greenlog_data/ existe
├─ MAIS effacé au Reboot
└─ D'où importance des sauvegardes
```

---

## 🆘 Si l'App Se Met Quand Même en Veille

### **Que Faire**

```
1. Visiter l'app
   → Redémarre automatiquement (30-60s)

2. Vérifier Keep-Alive
   → Sidebar → [☑ Keep-Alive] activé?

3. Vérifier UptimeRobot
   → Moniteur actif?
   → Ping récent?

4. Restaurer données
   → Bas de page → Sauvegarde & Restauration
   → Upload dernier ZIP
   → [Restaurer]
   → F5

5. ✅ Tout est de retour
```

---

## 📊 Comparaison des Solutions

| Solution | Coût | Efficacité | Setup | Autonome |
|----------|------|------------|-------|----------|
| Keep-Alive Intégré | Gratuit | ⭐⭐⭐ | 1 clic | ❌ Non |
| UptimeRobot | Gratuit | ⭐⭐⭐⭐⭐ | 5 min | ✅ Oui |
| Cron-Job.org | Gratuit | ⭐⭐⭐⭐⭐ | 5 min | ✅ Oui |
| GitHub Actions | Gratuit | ⭐⭐⭐⭐ | 15 min | ✅ Oui |
| Plan Team | $20/mois | ⭐⭐⭐⭐⭐ | 2 min | ✅ Oui |

**Recommandation** :
```
Keep-Alive Intégré + UptimeRobot = Meilleure combinaison gratuite
```

---

## ✅ Checklist de Configuration

```
□ Keep-Alive activé dans l'app (Sidebar)
□ Sauvegardes auto activées (Sidebar)
□ UptimeRobot configuré (5 min interval)
□ Email notifications UptimeRobot activées
□ Première sauvegarde téléchargée
□ Dossier sauvegardes créé sur ordinateur
□ URL Streamlit notée quelque part

= PROTECTION COMPLÈTE ACTIVÉE ✅
```

---

## 🎉 Résumé

**Pour éviter la mise en veille** :

1. **Activez Keep-Alive** (Sidebar)
   - ✅ Déjà intégré dans l'app
   - ✅ 1 clic pour activer

2. **Configurez UptimeRobot**
   - ✅ Gratuit
   - ✅ 5 minutes de setup
   - ✅ Fonctionne 24/7

3. **Activez Sauvegardes Auto**
   - ✅ Protection supplémentaire
   - ✅ Au cas où

**Avec ces 3 étapes, votre app restera active en permanence !** ⚡
