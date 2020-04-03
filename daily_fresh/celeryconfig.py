BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']

CELERY_TIMEZONE = 'Asia/Shanghai'

from datetime import timedelta
CELERYBEAT_SCHEDULE = {
    'add-every-30-seconds': {
        'task': 'user.tasks.add_test',
        'schedule': timedelta(seconds=30),
        'args': (17, 16)
    },
}