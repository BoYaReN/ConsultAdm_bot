import json

with open('config.json', 'r') as f:
    config = json.load(f)

    TOKEN = config['bot_token']
    DEVELOPER_ID = config['developer_id']
    DATABASE_FILENAME = config['database_filename']
    MODE = config['mode']
