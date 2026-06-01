import os
from dotenv import load_dotenv

load_dotenv()

ENVIRONMENT = os.getenv('RUN_AS', 'dev')

if ENVIRONMENT == 'prod':
    from .prod import *
elif ENVIRONMENT == 'stage':
    from .stage import *
else:
    from .dev import *