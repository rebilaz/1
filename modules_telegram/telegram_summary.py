from typing import Literal
from .telegram_bot import TelegramBot
from .telegram_logger import log_action

# Cette fonction est à appeler lors de la création/correction/test d’un module

def send_module_summary(bot: TelegramBot, module_id: str, action: Literal['création','correction','test'], summary: str):
    msg = f"[Module {module_id}] Action: {action}\nRésumé: {summary}"
    bot.send_message(msg)
    log_action(module_id, action, summary)
