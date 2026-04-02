from os import environ

SESSION_CONFIGS = [
    dict(
        name='sequential',
        display_name="Sequential Housing Experiment",
        num_demo_participants=3,
        app_sequence=['sequential'],
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.01,
    participation_fee=10.00,
    doc=""
)

PARTICIPANT_FIELDS = ['treatment']
SESSION_FIELDS = []
LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'NZD'
USE_POINTS = True

ROOMS = [dict(name='housing_lab', display_name='Housing Experiment')]

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

SECRET_KEY = '7144185848074'
INSTALLED_APPS = ['otree']
