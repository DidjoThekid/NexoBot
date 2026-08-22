# 🤖 NexoBot

Bot Discord multifonction créé en Python, structuré en **Cogs**, avec configuration **par serveur** stockée en base **PostgreSQL** (prêt pour Railway).

## ✨ Fonctionnalités

- **Modération** : `kick`, `ban`, `unban`, `mute`/`unmute` (timeout), `clear`, `warn`/`warnings`/`clearwarns`
- **Automod** : filtre de mots interdits + anti-spam automatique (`!automod on`)
- **Tickets** : système de tickets par boutons (`!setupticket`)
- **Logs** : suppressions/éditions de messages, arrivées/départs/bans de membres
- **Bienvenue** : message d'accueil personnalisable
- **Configuration par serveur** : chaque serveur a ses propres réglages (`!settings`)
- **Commandes utiles** : `ping`, `userinfo`, `serverinfo`, `avatar`

## 🚂 Déploiement sur Railway (recommandé)

1. Connecte ton repo GitHub à un nouveau projet Railway.
2. Dans le projet, clique **"+ New" → "Database" → "Add PostgreSQL"**.
3. Railway injecte automatiquement `DATABASE_URL` dans les variables d'environnement de ton service bot — rien à copier-coller.
4. Ajoute la variable `DISCORD_TOKEN` dans l'onglet **Variables** du service bot.
5. Railway détecte le `Procfile` et lance `python main.py` automatiquement à chaque push.

⚠️ Le système de fichiers de Railway est éphémère : **ne compte jamais sur un fichier local** (JSON, SQLite) pour stocker des données qui doivent survivre à un redéploiement — c'est pour ça que la config et les warnings passent par PostgreSQL.

## 💻 Lancer en local

```bash
git clone https://github.com/DidjoThekid/NexoBot.git
cd NexoBot
pip install -r requirements.txt
```

1. Copie `.env.example` en `.env` et renseigne :
   ```
   DISCORD_TOKEN=ton_token_ici
   DATABASE_URL=postgresql://user:password@localhost:5432/nexobot
   ```
   (installe PostgreSQL en local, ou utilise un service gratuit comme Neon/Supabase pour tester sans rien installer)
2. Active les **Privileged Gateway Intents** sur le [Developer Portal](https://discord.com/developers/applications) :
   - Server Members Intent
   - Message Content Intent
3. Lance le bot :
   ```bash
   python main.py
   ```
   Les tables sont créées automatiquement au premier démarrage.

## ⚙️ Configuration par serveur (dans Discord)

| Commande | Rôle |
|---|---|
| `!setprefix !` | Change le préfixe du bot |
| `!setlogchannel #salon` | Salon où sont envoyés les logs |
| `!setwelcomechannel #salon` | Salon de bienvenue |
| `!setwelcomemessage <texte>` | Message d'accueil (variables : `{mention}` `{member}` `{server}` `{count}`) |
| `!setticketcategory <catégorie>` | Catégorie où sont créés les tickets |
| `!setsupportrole @role` | Rôle ajouté automatiquement aux tickets |
| `!settings` | Affiche la config actuelle du serveur |
| `!automod on` / `off` | Active/désactive le filtre auto |
| `!addbannedword <mot>` | Ajoute un mot à la liste noire |
| `!removebannedword <mot>` | Retire un mot de la liste noire |
| `!bannedwords` | Envoie la liste en MP |

## 🎫 Mettre en place les tickets

Dans le salon souhaité, tape `!setupticket` (nécessite "Gérer le serveur"). Le bouton reste actif même après un redémarrage du bot.

## 🛡️ Sécurité

Ne commit jamais `.env` — il est dans `.gitignore`. Sur Railway, `DISCORD_TOKEN` et `DATABASE_URL` restent dans les Variables d'environnement, jamais dans le code. Si ton token a fuité, régénère-le immédiatement depuis le Developer Portal.

