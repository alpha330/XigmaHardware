import os

from dotenv import load_dotenv


load_dotenv()


SETTINGS_BY_ENVIRONMENT = {
    'dev': 'config.settings.dev',
    'stage': 'config.settings.stage',
    'prod': 'config.settings.prod',
    'test': 'config.settings.test',
}


def get_settings_module():
    environment = os.environ.get('RUN_AS', 'dev').strip().lower()
    return SETTINGS_BY_ENVIRONMENT.get(environment, SETTINGS_BY_ENVIRONMENT['dev'])
