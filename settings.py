from os import environ

<<<<<<< HEAD
=======

>>>>>>> 462cb37e00acf6d0675d70f11851905f5e7cf39f
SESSION_CONFIGS = [
    dict(
        name='sequential',
        display_name="Sequential Housing Experiment",
<<<<<<< HEAD
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
=======
        num_demo_participants=1,
        app_sequence=['sequential'],
    ),
]
# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ROOMS = [
    dict(
        name='housing',
        display_name='Housing Experiment',
    ),
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""


SECRET_KEY = '7144185848074'

>>>>>>> 462cb37e00acf6d0675d70f11851905f5e7cf39f
INSTALLED_APPS = ['otree']
