"""
Couche d'accès à la base de données PostgreSQL pour NexoBot.

Utilise un pool de connexions asyncpg. Sur Railway, la variable d'environnement
DATABASE_URL est injectée automatiquement dès que tu lies un service PostgreSQL
à ton bot — rien à configurer à la main.
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
    "ticket_review_channel_id": None,
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
