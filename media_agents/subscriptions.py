import os
import dotenv

dotenv.load_dotenv()

storage_file=os.getenv('SUBSCRIPTIONS_STORAGE')

def get_recipients():
    with open(storage_file, 'r', encoding='utf-8') as f:
        recipients = [r.strip('/n') for r in f.readlines()]
    return recipients
