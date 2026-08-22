"""
Couche d'accès à la base de données PostgreSQL pour NexoBot.

Utilise un pool de connexions asyncpg. Sur Railway, la variable d'environnement
DATABASE_URL est injectée automatiquement dès que tu lies un service PostgreSQL
à ton bot — rien à configurer à la main.

L'interface (noms de fonctions, types de retour) est identique à la version
SQLite précédente : aucun autre fichier du projet n'a besoin d'être modifié.
"""

import json
import os

import asyncpg

DATABASE_URL = os.getenv("DATABASE_URL")

DEFAULT_SETTINGS = {
    "prefix": "!",
    "mod_role_id": None,
    "welcome_channel_id": None,
    "log_channel_id": None,
    "ticket_category_id": None,
    "ticket_support_role_id": None,
    "welcome_message": "Bienvenue {mention} sur **{server}** ! Tu es notre {count}e membre 🎉",
    "automod_enabled": False,
}

_pool: asyncpg.Pool | None = None


async def _get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        if not DATABASE_URL:
            raise ValueError(
                "DATABASE_URL manquant. Sur Railway : ajoute un service PostgreSQL "
                "et lie-le à ce service pour que la variable soit injectée automatiquement."
            )
        _pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    return _pool


async def init_db():
    """Crée les tables si elles n'existent pas déjà. À appeler au démarrage du bot."""
    pool = await _get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id BIGINT PRIMARY KEY,
                settings_json TEXT NOT NULL
            )
            """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS warnings (
                id SERIAL PRIMARY KEY,
                guild_id BIGINT NOT NULL,
                user_id BIGINT NOT NULL,
                moderator TEXT NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS banned_words (
                guild_id BIGINT NOT NULL,
                word TEXT NOT NULL,
                PRIMARY KEY (guild_id, word)
            )
            """
        )


async def close_db():
    """À appeler proprement à l'arrêt du bot (optionnel mais propre)."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


# ---------------------------------------------------------------------------
# Settings par serveur
# ---------------------------------------------------------------------------

async def get_settings(guild_id: int) -> dict:
    """Retourne les settings d'un serveur, avec les valeurs par défaut en fallback."""
    pool = await _get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT settings_json FROM guild_settings WHERE guild_id = $1", guild_id
        )

    settings = dict(DEFAULT_SETTINGS)
    if row:
        settings.update(json.loads(row["settings_json"]))
    return settings


async def update_setting(guild_id: int, key: str, value) -> dict:
    """Met à jour une seule clé de settings pour un serveur et retourne les settings à jour."""
    settings = await get_settings(guild_id)
    settings[key] = value

    pool = await _get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO guild_settings (guild_id, settings_json) VALUES ($1, $2)
            ON CONFLICT (guild_id) DO UPDATE SET settings_json = excluded.settings_json
            """,
            guild_id, json.dumps(settings),
        )
    return settings


# ---------------------------------------------------------------------------
# Warnings
# ---------------------------------------------------------------------------

async def add_warning(guild_id: int, user_id: int, moderator: str, reason: str, created_at: str) -> int:
    """Ajoute un avertissement et retourne le nombre total d'avertissements du membre."""
    pool = await _get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO warnings (guild_id, user_id, moderator, reason, created_at) VALUES ($1, $2, $3, $4, $5)",
            guild_id, user_id, moderator, reason, created_at,
        )
        count = await conn.fetchval(
            "SELECT COUNT(*) FROM warnings WHERE guild_id = $1 AND user_id = $2", guild_id, user_id
        )
    return count


async def get_warnings(guild_id: int, user_id: int) -> list[dict]:
    pool = await _get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT moderator, reason, created_at FROM warnings "
            "WHERE guild_id = $1 AND user_id = $2 ORDER BY id ASC",
            guild_id, user_id,
        )
    return [{"moderator": r["moderator"], "reason": r["reason"], "created_at": r["created_at"]} for r in rows]


async def clear_warnings(guild_id: int, user_id: int) -> None:
    pool = await _get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM warnings WHERE guild_id = $1 AND user_id = $2", guild_id, user_id
        )


# ---------------------------------------------------------------------------
# Mots interdits (automod)
# ---------------------------------------------------------------------------

async def add_banned_word(guild_id: int, word: str) -> None:
    pool = await _get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO banned_words (guild_id, word) VALUES ($1, $2) ON CONFLICT DO NOTHING",
            guild_id, word.lower(),
        )


async def remove_banned_word(guild_id: int, word: str) -> None:
    pool = await _get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM banned_words WHERE guild_id = $1 AND word = $2", guild_id, word.lower()
        )


async def get_banned_words(guild_id: int) -> list[str]:
    pool = await _get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT word FROM banned_words WHERE guild_id = $1", guild_id
        )
    return [r["word"] for r in rows]
