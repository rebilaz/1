import logging
from typing import Any

def log_action(module_id: str, action: str, details: Any = None):
    msg = f"[Module {module_id}] Action: {action}"
    if details:
        msg += f" | Détails: {details}"
    logging.info(msg)
    # Ici, on pourrait aussi archiver dans un fichier ou une base de données
