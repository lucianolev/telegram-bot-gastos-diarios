import telebot

from src.dominio.asistente_personal import AsistentePersonal
from src.dominio.mensaje import Mensaje


class TelegramBot(AsistentePersonal):
    def __init__(self, api_token):
        self._bot = telebot.TeleBot(api_token)

    def construir_mensaje(self, carga_util):
        update = telebot.types.Update.de_json(carga_util)
        if update.message is None:
            return None
        return self._crear_mensaje(update.message)

    def enviar_mensaje(self, chat_id, texto):
        self._bot.send_message(chat_id, texto, parse_mode="Markdown")

    def responder_a(self, mensaje, texto):
        self._bot.send_message(
            mensaje.chat_id,
            texto,
            parse_mode="Markdown",
            reply_to_message_id=mensaje.mensaje_id,
        )

    def _crear_mensaje(self, mensaje_telegram):
        texto = mensaje_telegram.text or ""
        usuario = mensaje_telegram.from_user.first_name
        return Mensaje(
            chat_id=mensaje_telegram.chat.id,
            usuario=usuario,
            texto=texto,
            mensaje_id=mensaje_telegram.message_id,
        )
