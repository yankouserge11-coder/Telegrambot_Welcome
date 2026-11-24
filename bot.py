import logging
import os

from pathlib import Path
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    ChatJoinRequestHandler,
    CommandHandler,
    ContextTypes,
)


# ---------------------------------------------------------
# Configuration des journaux affichés dans le terminal
# ---------------------------------------------------------

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Chargement du token depuis le fichier .env
# ---------------------------------------------------------

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")
PORT = int(os.getenv("PORT", "10000"))

# Lien de la conversation privée (OnlyChat).
TELEGRAM_PRIVATE_LINK = "https://t.me/Valentinabennz"
WELCOME_IMAGE = Path(__file__).parent / "assets" / "welcome.jpg"


# ---------------------------------------------------------
# Commande /start
# ---------------------------------------------------------

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Répond lorsqu'un utilisateur démarre le bot."""

    user = update.effective_user

    if user is None or update.message is None:
        return

    first_name = user.first_name or "toi"

    message = (
        f"Coucou {first_name} 💕\n\n"
        "Bienvenue dans mon univers ✨\n\n"
        "Sur mon canal Telegram, je partage régulièrement des photos, "
        "des vidéos, des coulisses et différents moments de mon quotidien. 🌸\n\n"
        "Et si tu veux me parler, écris-moi en privé : "
        "touche le bouton juste en dessous 👇💖"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "💌 M'écrire en privé",
                url=TELEGRAM_PRIVATE_LINK,
            )
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text=message,
        reply_markup=reply_markup,
    )


# ---------------------------------------------------------
# Nouvelle demande d'adhésion au canal
# ---------------------------------------------------------

async def welcome_new_member(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Accueille et accepte automatiquement une demande d'adhésion."""

    join_request = update.chat_join_request

    if join_request is None:
        return

    user = join_request.from_user
    first_name = user.first_name or "toi"

    welcome_message = (
        f"💕 Bienvenue dans mon petit univers, {first_name} ! 🌸\n\n"
        "Je suis vraiment heureuse de t'accueillir ici. Merci d'avoir rejoint mon canal Telegram. 🥰\n\n"
        "✨ Ici, tu découvriras chaque jour un aperçu de mon quotidien : selfies, photos inédites, petites vidéos, coulisses du bureau et bien d'autres surprises. 💖\n\n"
        "💌 Et si tu veux me parler, écris-moi en privé : touche le bouton juste en dessous 👇\n\n"
        "💖 Passe régulièrement sur le canal, de nouvelles publications arrivent très souvent… 😉✨"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "💌 M'écrire en privé",
                url=TELEGRAM_PRIVATE_LINK,
            )
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
    # 1. Envoi de l'image
        if WELCOME_IMAGE.exists():
            with WELCOME_IMAGE.open("rb") as image_file:
                await context.bot.send_photo(
                    chat_id=join_request.user_chat_id,
                    photo=image_file,
                )
        else:
            logger.warning(
                "Image de bienvenue introuvable : %s",
                WELCOME_IMAGE,
            )

    # 2. Envoi du message et des boutons
        await context.bot.send_message(
            chat_id=join_request.user_chat_id,
            text=welcome_message,
            reply_markup=reply_markup,
        )

    # 3. Acceptation automatique de la demande
        await context.bot.approve_chat_join_request(
            chat_id=join_request.chat.id,
            user_id=user.id,
        )

        logger.info(
            "Demande acceptée : %s, identifiant %s",
            first_name,
            user.id,
        )

    except TelegramError as error:
            logger.exception(
            "Erreur lors du traitement de la demande de %s : %s",
            first_name,
            error,
        )


# ---------------------------------------------------------
# Gestion générale des erreurs
# ---------------------------------------------------------

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    logger.exception(
        "Une erreur non gérée est survenue :",
        exc_info=context.error,
    )


# ---------------------------------------------------------
# Démarrage du bot
# ---------------------------------------------------------

def main() -> None:
    if not BOT_TOKEN:
        raise ValueError(
            "Le token est introuvable. Vérifie la variable BOT_TOKEN."
        )

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        ChatJoinRequestHandler(welcome_new_member)
    )
    application.add_error_handler(error_handler)

    if RENDER_EXTERNAL_URL:
        webhook_url = f"{RENDER_EXTERNAL_URL}/telegram"

        print("✅ Démarrage du bot en mode webhook.")
        print(f"Webhook : {webhook_url}")

        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path="telegram",
            webhook_url=webhook_url,
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=False,
        )

    else:
        print("✅ Démarrage local en mode polling.")
        print("Appuie sur Ctrl + C pour arrêter le bot.")

        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=False,
        )


if __name__ == "__main__":
    main()
