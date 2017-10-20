import os

app_stage = os.environ.get('DJANGO_APP_STAGE', 'dev')
if app_stage == 'prod':
    from .prod import *
else:
    from .dev import *