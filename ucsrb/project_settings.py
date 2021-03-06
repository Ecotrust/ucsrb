"""
Django settings for marineplanner project.

Generated by 'django-admin startproject' using Django 1.10.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""


import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASSETS_DIR = os.path.realpath(os.path.join(BASE_DIR, '..', 'assets'))
STYLES_DIR = os.path.realpath(os.path.join(ASSETS_DIR, 'styles'))

MEDIA_ROOT = os.path.realpath(os.path.join(BASE_DIR, '..', 'apps', 'ucsrb', 'ucsrb', 'media'))

SITE_ID = 1

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-u*-d*&7j=c7a7&k5u6e61b4-t=d8ce^2k=jhox#cn8iy8m_%d'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost']


# Application definition

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'marineplanner.urls'

LOGIN_REDIRECT_URL = '/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'marineplanner.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'NAME': 'marineplanner',
        'USER': 'postgres',
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = (
    STYLES_DIR,
    ASSETS_DIR,
)

### Django compressor (mp-visualize/base.html)
COMPRESS_ENABLED = False
COMPRESS_URL = STATIC_URL
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_URL_PLACEHOLDER = '_'
COMPRESS_OUTPUT_DIR = 'CACHE'
COMPRESS_STORAGE = 'compressor.storage.CompressorFileStorage'
COMPRESS_VERBOSE = False
COMPRESS_PARSER = 'compressor.parser.AutoSelectParser'
COMPRESS_DEBUG_TOGGLE = 'None'

COMPRESS_JS_COMPRESSOR = 'compressor.js.JsCompressor'
COMPRESS_JS_FILTERS = ['compressor.filters.jsmin.JSMinFilter']

COMPRESS_CSS_COMPRESSOR = 'compressor.css.CssCompressor'
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter'
]
COMPRESS_CSS_HASHING_METHOD = 'mtime'
COMPRESS_MTIME_DELAY = 10

COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
    ('text/x-sass', 'django_libsass.SassCompiler'),
    ('text/less', 'lessc {infile} {outfile}'),
)
COMPRESS_CACHEABLE_PRECOMPILERS = ()

COMPRESS_CACHE_KEY_FUNCTION = 'compressor.cache.simple_cachekey'
COMPRESS_CACHE_BACKEND = 'default'

COMPRESS_OFFLINE = True
COMPRESS_OFFLINE_CONTEXT = {}
COMPRESS_OFFLINE_MANIFEST = 'manifest.json'

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder',
]

### Note: This MUST be set before importing project_settings, even though
#       INSTALLED_APPS is the first thing project_settings sets.
#       Because... django? ¯\_(?)_/¯
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.gis',
    'django.contrib.flatpages',
    'marineplanner',
    'core',
    'compressor',
    'captcha',
    'import_export',
    'social.apps.django_app.default',
    'social_django',
    ### BEGIN INSERTED INSTALLED APPS ###
    'features',
    'manipulators',
    'accounts',
    'data_manager',
    'drawing',
    'ucsrb',
    'visualize',
    'nursery',
    'rpc4django',
    'analysistools',
    'scenarios',
    # 'filter',
    'geodata',
    ### END INSERTED INSTALLED APPS ###
    'ckeditor',
]

########################################
######        LAYER DATA        ########
########################################
FOCUS_AREA_TYPES = ['HUC10', 'HUC12', 'RMU', 'PourPointOverlap', 'PourPointDiscrete', 'Drawing']
FOCUS_AREA_FIELD_ID_LOOKUP = {
    'HUC10': 'huc_10_id',
    'HUC12': 'huc_12_id',
    'RMU': 'mgmt_unit_id',
    'PourPointOverlap': 'dwnstream_ppt_id',
    'PourPointDiscrete': 'dwnstream_ppt_id',
    'Drawing': False
}
IMPORT_SRID = 3857


GET_SCENARIOS_URL = '/ucsrb/get_scenarios/'
SCENARIO_FORM_URL = '/features/treatmentscenario/form/'
SCENARIO_LINK_BASE = '/features/treatmentscenario/ucsrb_treatmentscenario'

METHOW_YEAR = 1997
ENTIAT_YEAR = 1997
WENATCHEE_YEAR = 1997

WEATHER_STATIONS = {
    'mazama': {   #
        'start': '10.01.1996-00:00:00',
        'end': '09.30.1997-23:00:00'
    },
    'plain': {   #
        'start': '10.01.1996-00:00:00',
        'end': '09.30.1997-23:00:00'
    },
    'poperidge': {   #
        'start': '10.01.1996-00:00:00',
        'end': '09.30.1997-23:00:00'
    },
    'trinity': {   #
        'start': '10.01.1996-00:00:00',
        'end': '09.30.1997-23:00:00'
    },
    'winthrop': {   # METHOW Valley
    'start': '10.01.1996-00:00:00',
    'end': '09.30.1997-23:00:00'
    }
}

########################################
######      TREATMENT VALS      ########
########################################

TREATMENT_TARGETS = {
    'baseline': 100,
    'reduce to 50': 50,
    'reduce to 30': 30,
    'reduce to 0': 0
}

########################################
######      HYDRO RESULTS       ########
########################################

DELETE_CSVS = True

HYDRO_INPUT_HEADERS = [
    'ppt_ID','start_time','end_time','mazama','plain','poperidge','trinity',
    'winthrop','area','mean_elev','avg_slp','slp_gt60','elev_dif','mean_shade',
    'veg_prop','thc_11','thc_12','thc_13','thc_14','thc_15','thc_21','thc_22',
    'thc_23','thc_24','thc_25','bulk_dens','cap_drv','exp_decrs','field_cap',
    'lat_con','mannings','pore_sz','porosity','vert_con','wilt_pt','bbl_prsr',
    'max_inf','center_x','center_y','normal_x','normal_y','normal_z','SDsphrical'
]

ANALYSIS_DIR = os.path.realpath(os.path.join(BASE_DIR, '..', 'ucsrb', 'analysis'))

# TIME_STEP values MUST be factors of 24, and REPORTING must be a multiple of HOURS.
TIME_STEP_HOURS = 3
TIME_STEP_REPORTING = 6

CSV_DIR = os.path.realpath(os.path.join(ANALYSIS_DIR, 'input_csvs'))

NN_DATA_DIR = os.path.realpath(os.path.join(BASE_DIR, '..', 'ucsrb', 'ucsrb', 'data'))
NN_CSV_FLOW_COLUMN = 'C'
DEFAULT_NN_PPT = 114

########################################
######   MODEL FIELD CHOICES    ########
########################################

WATERSHED_CHOICES = [
    ('ent', 'Upper Entiat'),
    ('met', 'Upper Methow'),
    ('wen', 'Chiwawa')
]

########################################
######      FILTER CHOICES      ########
########################################
OWNERSHIP_CHOICES = (
    # ('NULL', '---'),
    ('Bureau of Land Management', 'Bureau of Land Management'),
    ('Bureau of Reclamation', 'Bureau of Reclamation'),
    ('National Park Service', 'National Park Service'),
    ('Native American Land', 'Native American Land'),
    ('Private land', 'Private Land'),
    ('Public Land', 'Public Land'),
    ('U.S. Air Force', 'U.S. Air Force'),
    ('U.S. Army', 'U.S. Army'),
    ('U.S. Fish & Wildlife Service', 'U.S. Fish & Wildlife Service'),
    ('USDA Forest Service', 'USDA Forest Service'),
    ('Washington Department of Fish & Wildlife', 'Washington Department of Fish & Wildlife'),
    ('Washington Department of Forestry', 'Washington Department of Forestry'),
    ('Washington Department of Natural Resources', 'Washington Department of Natural Resources'),
    ('Washington Department of Parks and Recreation', 'Washington Department of Parks and Recreation'),
    ('Washington State Government', 'Washington State Government'),
)

LANDFORM_TYPES = [
    'include_north',
    'include_south',
    'include_ridgetop',
    'include_floors',
    'include_east_west'
]

DEFAULT_PRESENCE_THRESHOLD = 10 # % of planning unit with a given property to count as 'having' that property
LSR_THRESHOLD = DEFAULT_PRESENCE_THRESHOLD
CRIT_HAB_THRESHOLD = DEFAULT_PRESENCE_THRESHOLD
ROADLESS_THRESHOLD = 50
WETLAND_THRESHOLD = 50
RIPARIAN_THRESHOLD = 50
FIRE_RISK_THRESHOLD = 30

DATA_UPLOAD_MAX_NUMBER_FIELDS = 4000

# RDH 3/18/2019 - pour point IDs that we couldn't model or impute
PROBLEMATIC_POUR_POINTS = [
    259,247,302,310,378,311,438,463,870,910,945,976,1068,1122,1153,1150,1242,
    1227,1249,1266,1261,1384,1399,1385,1428,1526,1633,1668,1584,1677,1702,1708,
    1741,1767,1785,1864,1959,1882,1995,2052,2059,2113,2098,2144,2131,2264,2300,
    2310,2203,2348,2133,2409,2443,2351,2481,2494,2497,2547,2556,2610,2537,2608,
    2634,2651,2669,2702,2716,2613,2783,2773,2800,2806,2830,2808,2823,2798,2836,
    2779,2860,2869,2883,2802,2901,2946,2940,2953,3042,3210,3328,3355,3399,3416,
    3482,3395,3470,3478,3528,3521,3488,3556,3576,3579,3583,3624,3653,3606,3524,
    3656,3662,3613,3682,3664,3675,3742,3704,3820,3768,3847,3885,3871,3952,3928,
    4039,4058,4052,4064,4140,4124,4137,4194,4238,4258,4234,4385,4366,4493,4505,
    4580,4587,4603,4611,4612,4652,4641,4775,4800,4884,4858,4920,5002,4999,5005,
    5031,5048,5021,5082,5090,5078,5137,5182,5203,5217,5156,5236,5258,5254,5285,
    5310,5340,5474,5557,5570,5895,6026,6029,5918,6064,6112,6093,6016,6278,6251,
    6268,6226,6328,6312,6342,6427,6535,6471,6634,6651,6583,6688,6776,6808,6756,
    6829,6699,6912,6809,6822,6863,6910,6952,6964,7013,7035,7043,7070,7146,7170,
    7263,7333,7384,7437,7480,7569,7445,7602,7629,7630,7657,7605,7711,7685,7712,
    7751,7684,7844,7862,7749,7812,7915,7898,7925,7940,7944,7961,7962,7950,8049,
    8139,8136,8175,8194,8272,8273,8280,8353,8399,8396,8415,8599,8584,8608,8701,
    8813,8845,8852,8873,8953,8991,9013
]

MAP_TECH = 'ol4'

ALLOW_ANONYMOUS_DRAW = True
ANONYMOUS_USER_PK = 1

MIN_TREATMENT_ACRES = 100

USE_TZ = False

try:
    ### START MODULE SETTINGS IMPORT ###
    from features.settings import *
    from accounts.settings import *
    from data_manager.settings import *
    from drawing.settings import *
    from scenarios.settings import *
    ### END MODULE SETTINGS IMPORT ###
except ImportError:
    pass

ADMIN_URL = '/admin/'
CMS_ADMIN_BUTTON = False

MAX_SCENARIO_RESULTS = 10000
MAPBOX_ACCESS_TOKEN = 'set_in_local_settings'

EMAIL_HOST_USER = 'noreply@s2fdemo.ecotrust.org'
DEFAULT_FROM_EMAIL = 'noreply@s2fdemo.ecotrust.org'
EMAIL_HOST_ADDRESS = 'https://s2fdemo.ecotrust.org'
SERVER_EMAIL = 'noreply@s2fdemo.ecotrust.org'
PROJECT_SITE = 'http://s2fdemo.ecotrust.org'
PROJECT_NAME = 'Snow2Flow'

FORGOT_EMAIL_SUBJECT = 'Snow2Flow Password Reset Request'

LOG_IN_WITH_EMAIL = False

try:
    # Local settings should probably be collected to project folder instead.
    from marineplanner.local_settings import *
except ImportError:
    pass

try:
    from ucsrb.local_settings import *
except ImportError:
    pass

# This seems to help with some backward compatibility
import django
django.setup()
