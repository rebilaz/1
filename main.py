import os
import glob
import importlib.util
import subprocess
import logging
from loguru import logger
from dotenv import load_dotenv
from google.cloud import bigquery
from openai import OpenAI
import time
from modules_telegram import TelegramBot
from modules_telegram.telegram_summary import send_module_summary

load_dotenv()

# Variables d'environnement
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = int(os.getenv('TELEGRAM_CHAT_ID', '0'))
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_APPLICATION_CREDENTIALS or ''

# Initialisation des clients
bq_client = bigquery.Client()
telegram_bot = TelegramBot(token=TELEGRAM_BOT_TOKEN, chat_id=TELEGRAM_CHAT_ID, command_handlers={}) if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID else None
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

MODULES_DIR = 'modules_proposes'
LOGS_DIR = 'logs'

# 1. Découverte des datasets crypto publics sur BigQuery
def discover_crypto_datasets():
    logger.info('Recherche des datasets crypto publics sur BigQuery...')
    query = """
        SELECT project_id, dataset_id, description
        FROM `bigquery-public-data`.INFORMATION_SCHEMA.SCHEMATA
        WHERE LOWER(dataset_id) LIKE '%crypto%' OR LOWER(description) LIKE '%crypto%'
    """
    results = bq_client.query(query).result()
    datasets = [dict(row) for row in results]
    logger.info(f"{len(datasets)} datasets trouvés.")
    return datasets

# 2. Génération automatique de workers Python
def generate_worker(dataset):
    template = f""""""
import os
from google.cloud import bigquery

def main():
    client = bigquery.Client()
    query = f\"SELECT * FROM `{{dataset['project_id']}}.{{dataset['dataset_id']}}.INFORMATION_SCHEMA.TABLES` LIMIT 10\"
    results = client.query(query).result()
    for row in results:
        print(row)

if __name__ == '__main__':
    main()
""""""
    filename = f"worker_{dataset['project_id']}_{dataset['dataset_id']}.py"
    path = os.path.join(MODULES_DIR, filename)
    with open(path, 'w') as f:
        f.write(template)
    logger.info(f"Worker généré : {path}")
    return path

# 3. Exécution et boucle de correction automatique
def run_worker(path):
    log_path = os.path.join(LOGS_DIR, os.path.basename(path) + '.log')
    for attempt in range(3):
        logger.info(f"Exécution du worker {path}, tentative {attempt+1}")
        with open(log_path, 'w') as log_file:
            proc = subprocess.Popen(['python', path], stdout=log_file, stderr=log_file)
            proc.wait()
        with open(log_path) as log_file:
            logs = log_file.read()
        if proc.returncode == 0:
            logger.success(f"Succès : {path}")
            return True, logs
        else:
            logger.warning(f"Erreur détectée dans {path}, tentative de correction...")
            if openai_client:
                with open(path) as f:
                    code = f.read()
                prompt = f"""
Contexte :
Voici le code du worker Python qui a échoué :
---
{code}
---
Voici le log d’erreur obtenu lors de l’exécution :
---
{logs}
---
Corrige le code pour que le worker fonctionne sans erreur. Explique brièvement la correction apportée.
"""
                response = openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}]
                )
                corrected_code = response.choices[0].message.content
                # Extraction du code corrigé (suppose que le code est entre balises ```)
                if '```' in corrected_code:
                    corrected_code = corrected_code.split('```')[1]
                with open(path, 'w') as f:
                    f.write(corrected_code)
            else:
                logger.error("OPENAI_API_KEY manquant, impossible de corriger automatiquement.")
                break
    return False, logs

# 4. Documentation automatique
def document_worker(path):
    with open(path) as f:
        code = f.read()
    docstring = f"""
# Documentation auto-générée
# Input: Aucun argument, utilise BigQuery Client
# Output: Affiche les 10 premières tables du dataset
"""
    code = docstring + '\n' + code
    with open(path, 'w') as f:
        f.write(code)

# 5. Notification Telegram

def notify_telegram(message):
    if telegram_bot:
        telegram_bot.send_message(message)


def pipeline_action(module_id, action, summary):
    if telegram_bot:
        send_module_summary(telegram_bot, module_id, action, summary)
    else:
        logger.info(f"[Module {module_id}] Action: {action} | {summary}")

def main_loop():
    datasets = discover_crypto_datasets()
    success, fail = 0, 0
    for ds in datasets:
        worker_path = generate_worker(ds)
        ok, logs = run_worker(worker_path)
        document_worker(worker_path)
        mod_id = os.path.splitext(os.path.basename(worker_path))[0]
        if ok:
            success += 1
            pipeline_action(mod_id, "création", "Worker généré et exécuté avec succès.")
        else:
            fail += 1
            pipeline_action(mod_id, "correction", "Erreur détectée, correction automatique tentée.")
    notify_telegram(f"Scan terminé. Succès: {success}, Échecs: {fail}, Total: {len(datasets)}")
    logger.info("Pipeline terminé.")

    # Boucle d'écoute des commandes Telegram
    if telegram_bot:
        print("En attente de commandes Telegram (valide, corrige, rejoue, archive, show log)...")
        while True:
            action, mod_id = telegram_bot.get_next_action()
            if action == "valide":
                pipeline_action(mod_id, "validation", "Module validé et intégré au pipeline.")
            elif action == "corrige":
                pipeline_action(mod_id, "correction", "Correction automatique lancée.")
            elif action == "rejoue":
                pipeline_action(mod_id, "rejeu", "Rejeu du module demandé.")
            elif action == "archive":
                pipeline_action(mod_id, "archive", "Archivage du module demandé.")
            elif action == "show_log":
                pipeline_action(mod_id, "log", "Affichage du log du module.")
            else:
                pipeline_action(mod_id, "inconnu", f"Action inconnue : {action}")
            time.sleep(0.5)

if __name__ == '__main__':
    main_loop()
