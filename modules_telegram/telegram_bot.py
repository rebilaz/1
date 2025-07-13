import logging
import threading
from queue import Queue
from typing import Callable, Dict
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str, chat_id: int, command_handlers: Dict[str, Callable]):
        self.token = token
        self.chat_id = chat_id
        self.command_handlers = command_handlers
        self.updater = Updater(token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.queue = Queue()
        self._setup_handlers()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info("Telegram bot initialized.")

    def _setup_handlers(self):
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self._on_message))
        for cmd, handler in self.command_handlers.items():
            self.dispatcher.add_handler(CommandHandler(cmd, handler))

    def _on_message(self, update: Update, context: CallbackContext):
        text = update.message.text.strip()
        logger.info(f"Received message: {text}")
        if text.startswith("valide "):
            mod_id = text.split(" ", 1)[1]
            self.queue.put(("valide", mod_id))
            self.send_message(f"[Module {mod_id}] Action: validation demandée.")
        elif text.startswith("corrige "):
            mod_id = text.split(" ", 1)[1]
            self.queue.put(("corrige", mod_id))
            self.send_message(f"[Module {mod_id}] Action: correction demandée.")
        # Extend here for more commands
        elif text.startswith("rejoue "):
            mod_id = text.split(" ", 1)[1]
            self.queue.put(("rejoue", mod_id))
            self.send_message(f"[Module {mod_id}] Action: rejouer demandée.")
        elif text.startswith("archive "):
            mod_id = text.split(" ", 1)[1]
            self.queue.put(("archive", mod_id))
            self.send_message(f"[Module {mod_id}] Action: archivage demandé.")
        elif text.startswith("show log "):
            mod_id = text.split(" ", 2)[1]
            self.queue.put(("show_log", mod_id))
            self.send_message(f"[Module {mod_id}] Action: affichage du log demandé.")
        else:
            self.send_message("Commande non reconnue. Utilisez: valide <mod_id>, corrige <mod_id>, rejoue <mod_id>, archive <mod_id>, show log <mod_id>.")

    def _run(self):
        logger.info("Starting Telegram polling thread.")
        self.updater.start_polling()
        self.updater.idle()

    def send_message(self, text: str):
        bot = Bot(self.token)
        bot.send_message(chat_id=self.chat_id, text=text)
        logger.info(f"Sent message: {text}")

    def get_next_action(self):
        return self.queue.get()

# Example usage (to be adapted in main pipeline):
# def handle_valide(update, context):
#     ...
# command_handlers = {"start": handle_start}
# bot = TelegramBot(token="YOUR_TOKEN", chat_id=123456789, command_handlers=command_handlers)
# bot.send_message("Test message.")
# action, mod_id = bot.get_next_action()
