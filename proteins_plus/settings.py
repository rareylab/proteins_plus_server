"""Django settings for proteins_plus project."""
from pathlib import Path
import os
import json
from datetime import datetime

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-vnltu0uost-cm8h=psgz6$v!pfz^%w)8v2el!eez-$qsbb$ic#' \
    if 'SECRET_KEY' not in os.environ else os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True \
    if 'DEBUG' not in os.environ or os.environ['DEBUG'].capitalize() == 'True' else False

ALLOWED_HOSTS = [
    '.localhost', '127.0.0.1', '[::1]', 'proteins.plus',
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_spectacular',
    'molecule_handler.apps.MoleculeHandlerConfig',
    'protoss.apps.ProtossConfig',
    'ediascorer.apps.EdiascorerConfig',
    'proteins_plus.apps.ProteinsPlusConfig',
    'metalizer.apps.MetalizerConfig',
    'poseview.apps.PoseviewConfig',
    'siena.apps.SienaConfig',
    'dogsite.apps.DoGSiteConfig',
    'structureprofiler.apps.StructureprofilerConfig',
    'geomine.apps.GeoMineConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'proteins_plus.urls'

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

WSGI_APPLICATION = 'proteins_plus.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': 'localhost' if 'PPLUS_DB_HOST' not in os.environ else os.environ['PPLUS_DB_HOST'],
        'PORT': 5432 if 'PPLUS_DB_PORT' not in os.environ else os.environ['PPLUS_DB_PORT'],
        'NAME': 'pplusdb' if 'PPLUS_DB_NAME' not in os.environ else os.environ['PPLUS_DB_NAME'],
        'USER': 'pplususer' if 'PPLUS_DB_USER' not in os.environ else os.environ['PPLUS_DB_USER'],
        'PASSWORD': 'PPlusRocks' if 'PPLUS_DB_PASS' not in os.environ else os.environ['PPLUS_DB_PASS'],
    },
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/server/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Celery settings
CELERY_BROKER_URL = 'redis://localhost:6378'
CELERY_RESULT_BACKEND = 'redis://localhost:6378'

# Swagger Config
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10
}
SPECTACULAR_SETTINGS = {
    'TITLE': 'ProteinsPlus Swagger',
    'DESCRIPTION': 'Software tools for protein analysis',
    'VERSION': '1.0.0',
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX_INSERT': '' if 'MOUNT_POINT' not in os.environ else os.environ['MOUNT_POINT'],
    'SWAGGER_UI_SETTINGS': {
        'url': '/schema/' if 'SCHEMA_URL' not in os.environ else os.environ['SCHEMA_URL'],
    },
}

# Media files (Images for ligands)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') if 'MEDIA_ROOT' not in os.environ else os.environ['MEDIA_ROOT']
MEDIA_URL = '/static/media/'

# Media paths
MEDIA_DIRECTORIES = {
    'ligands': 'ligands/',
    'density_files': 'density_files/',
    'posview_images': 'poseview/',
}

# Paths for binary files
if 'PPLUS_BINARIES_JSON' in os.environ:
    BINARY_PATHS_CONFIG = os.environ['PPLUS_BINARIES_JSON']
else:
    BINARY_PATHS_CONFIG = os.path.join(BASE_DIR, 'proteins_plus', 'binaries.json')
with open(BINARY_PATHS_CONFIG, encoding='utf8') as binary_paths_file:
    BINARIES = json.load(binary_paths_file)

# Important urls
URLS = {
    'pdb_files': 'https://files.rcsb.org/download/',
    'alphafold_files': 'https://alphafold.ebi.ac.uk/api/prediction/',
    'density_files': 'https://www.ebi.ac.uk/pdbe/entry-files/',
}

# local data mirrors
LOCAL_PDB_MIRROR_DIR = Path('/data/pdb/current/data/structures/all/pdb/') \
    if 'LOCAL_PDB_MIRROR_DIR' not in os.environ else Path(os.environ['LOCAL_PDB_MIRROR_DIR'])
LOCAL_DENSITY_MIRROR_DIR = Path('') \
    if 'LOCAL_DENSITY_MIRROR_DIR' not in os.environ else Path(
    os.environ['LOCAL_DENSITY_MIRROR_DIR'])
LOCAL_AFDB_MIRROR_DIR = Path('') if 'LOCAL_AFDB_MIRROR_DIR' not in os.environ else Path(
    os.environ['LOCAL_AFDB_MIRROR_DIR'])

# Configuration of logging module
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': f'logs/log_{datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")}.txt',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'DEBUG',
    }
}

DEFAULT_JOB_CACHE_TIME = 7  # days
