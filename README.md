# 🤖 NexoBot

**Votre serveur Discord, simplifié.**

NexoBot est un bot Discord polyvalent conçu pour faciliter la gestion de votre serveur grâce à des outils de modération, un système de tickets, des logs automatiques et bien plus encore.

[![Discord](https://img.shields.io/badge/Discord-Bot-7289DA?style=for-the-badge&logo=discord)](https://discord.com/oauth2/authorize?client_id=1511746763831247091&permissions=8&integration_type=0&scope=bot+applications.commands)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![discord.py](https://img.shields.io/badge/discord.py-2.5.0+-red?style=for-the-badge&logo=python)](https://discordpy.readthedocs.io/)

---

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Commandes](#-commandes)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Déploiement sur Railway](#-déploiement-sur-railway)
- [Structure du projet](#-structure-du-projet)
- [Support](#-support)

---

## ✨ Fonctionnalités

### ️ Modération complète
- Kick, ban, unban
- Mute/timeout temporaire
- Suppression de messages en masse
- Système de raisons pour chaque action

###  Système de tickets
- Création de salons de support privés
- Fermeture automatique des tickets
- Gestion simplifiée du support

###  Logs automatiques
- Messages supprimés/modifiés
- Arrivées/départs de membres
- Traçabilité complète

###  Bienvenue personnalisée
- Messages d'accueil automatiques
- Personnalisation du message
- Embeds riches avec mentions

### 🛠️ Commandes utilitaires
- Informations serveur/utilisateur
- Ping et statistiques
- Aide intégrée

---

## 📜 Commandes

**Préfixe par défaut :** `!` (configurable dans `config.json`)

### Modération

| Commande | Syntaxe | Description | Permissions |
|----------|---------|-------------|-------------|
| `!kick` | `!kick @membre [raison]` | Expulse un membre | Expulser des membres |
| `!ban` | `!ban @membre [raison]` | Bannit un membre | Bannir des membres |
| `!unban` | `!unban <nom_ou_id>` | Débannit un membre | Bannir des membres |
| `!clear` | `!clear <nombre>` | Supprime X messages (max 100) | Gérer les messages |
| `!mute` | `!mute @membre <minutes> [raison]` | Rend muet temporairement | Gérer les membres |
| `!unmute` | `!unmute @membre` | Enlève le mute | Gérer les membres |

### Tickets

| Commande | Syntaxe | Description |
|----------|---------|-------------|
| `!ticket` | `!ticket [raison]` | Ouvre un salon de support privé |
| `!close` | `!close` | Ferme le ticket actuel |

### Utilitaires

| Commande | Syntaxe | Description |
|----------|---------|-------------|
| `!ping` | `!ping` | Affiche la latence du bot |
| `!info` | `!info` | Statistiques du bot |
| `!help` | `!help` | Affiche l'aide complète |

---

## 🚀 Installation

### Prérequis

- Python 3.10 ou supérieur
- Un bot Discord créé sur [Discord Developer Portal](https://discord.com/developers/applications)
- Un compte [Railway](https://railway.app/) (pour l'hébergement gratuit)

### 1. Cloner le repository

```bash
git clone https://github.com/DidjoThekid/NexoBot.git
cd NexoBot
