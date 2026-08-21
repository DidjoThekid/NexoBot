# 🤖 NexoBot

Bot Discord multifonction créé en Python, structuré en **Cogs**.

## ✨ Fonctionnalités

- **Modération** : `kick`, `ban`, `unban`, `mute`/`unmute` (timeout), `clear`, `warn`/`warnings`/`clearwarns`
- **Tickets** : système de tickets par boutons (`!setupticket`)
- **Logs** : suppressions/éditions de messages, arrivées/départs/bans de membres
- **Bienvenue** : message d'accueil personnalisable pour les nouveaux membres
- **Commandes utiles** : `ping`, `userinfo`, `serverinfo`, `avatar`

## 📦 Installation

```bash
git clone https://github.com/DidjoThekid/NexoBot.git
cd NexoBot
pip install -r requirements.txt
```

## ⚙️ Configuration

1. Copie `.env.example` en `.env` et renseigne ton token Discord :
   ```
   DISCORD_TOKEN=ton_token_ici
   ```
2. Édite `config.json` pour renseigner les IDs de ton serveur :
   ```json
   {
     "prefix": "!",
     "mod_role_id": 123456789012345678,
     "welcome_channel_id": 123456789012345678,
     "log_channel_id": 123456789012345678,
     "ticket_category_id": 123456789012345678,
     "ticket_support_role_id": 123456789012345678,
     "welcome_message": "Bienvenue {mention} sur **{server}** ! Tu es notre {count}e membre 🎉"
   }
   ```
3. Sur le [Developer Portal](https://discord.com/developers/applications), active les **Privileged Gateway Intents** :
   - Server Members Intent
   - Message Content Intent

## 🚀 Lancer le bot

```bash
python main.py
```

## 🎫 Mettre en place les tickets

Dans le salon souhaité, tape `!setupticket` (nécessite la permission "Gérer le serveur"). Un bouton "Ouvrir un ticket" apparaîtra.

## 🛡️ Sécurité

Ne commit jamais ton fichier `.env` — il est déjà ignoré par `.gitignore`. Si ton token a fuité, régénère-le immédiatement depuis le Developer Portal.
