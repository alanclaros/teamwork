"""
Django settings for app project.

Generated by 'django-admin startproject' using Django 3.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-=g@vb5=hn8&s#s4tnj97cj-zuaz^7p-a+v15=-2+%o&qlip5o0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', '192.168.0.27']
CURRENT_HOST = '127.0.0.1'
HOST_FULL_PATH = '127.0.0.1:8000'
#SUB_URL_EMPRESA = 'teamwork'
SUB_URL_EMPRESA = ''

# base de datos
DATABASE_HOST = 'localhost'
DATABASE_USER = 'root'
DATABASE_PASSWORD = ''
DATABASE_NAME = 'condominiosv10'
# email contacto
EMAIL_CONTACT_FROM = 'root@gidaesrl.com'
EMAIL_CONTACT_TO = 'acc.claros@gmail.com'
EMAIL_SERVER_NAME = 'gidaesrl.com'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'pages.apps.PagesConfig',
    'status.apps.StatusConfig',
    'permisos.apps.PermisosConfig',
    'configuraciones.apps.ConfiguracionesConfig',
    'cajas.apps.CajasConfig',
    'departamentos.apps.DepartamentosConfig',
    'lecturas.apps.LecturasConfig',
    'calendario.apps.CalendarioConfig',
    'webpush',
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

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries':{
                'jinja_tags': 'templatetags.jinja_tags',
            }
        },
    },
]

WSGI_APPLICATION = 'app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DATABASE_NAME,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': DATABASE_HOST,
        'PORT': '3306',
    }
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


# webpush
# https://web-push-codelab.glitch.me/
WEBPUSH_SETTINGS = {
    "VAPID_PUBLIC_KEY": "BG95g_H1e_D0wRD7DTN2rcvaZiPPVAh83KQG3balVN1BS58KESMSFihE50n4MQVT6GOyRY4v4fW2Cx4dyjO7jIA",
    "VAPID_PRIVATE_KEY": "YpOP04j0nkwO-nlDOS2dA5MEVn5HeJ1q_iRrA_Zv_fg",
    "VAPID_ADMIN_EMAIL": "acc.claros@gmail.com"
}

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'es-es'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'America/La_Paz'

USE_I18N = True

# formato de numeros
# USE_L10N = True
USE_L10N = False
DECIMAL_SEPARATOR = '.'

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# acc, para guardar las imagenes, en development y produccion (verificar)
STATIC_ROOT_APP = os.path.join(BASE_DIR, 'app', 'static')

# acc, ruta de archivos estaticos para tener varios sitios en el mismo host wsgi de apache
# se debe cambiar el alias de "/static/", caso contrario chocan entre los sitios web
# esta ruta esta definida en /etc/apache2/sites-available/000-default.conf
if CURRENT_HOST == '127.0.0.1':
    STATIC_URL = '/static/'
    SESSION_COOKIE_NAME = 'ntsoft'
else:
    STATIC_URL = '/' + SUB_URL_EMPRESA + '/' + 'static/'
    # nombre de los cookies por sitio web
    SESSION_COOKIE_NAME = SUB_URL_EMPRESA

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'app/static')
]

# media folders settings
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Redirect to home URL after login (Default redirects to /accounts/profile/)
if CURRENT_HOST == '127.0.0.1':
    LOGIN_REDIRECT_URL = '/'
else:
    LOGIN_REDIRECT_URL = '/' + SUB_URL_EMPRESA


# modulos
# GRUPO 1
MOD_COBROS = 1
MOD_LECTURAS = 2
MOD_DEPARTAMENTOS = 3
MOD_ASIGNAR_COBROS_MANUALES = 4
# GRUPO 2
MOD_INICIAR_CAJA = 5
MOD_INICIAR_CAJA_RECIBIR = 6
MOD_ENTREGAR_CAJA = 7
MOD_ENTREGAR_CAJA_RECIBIR = 8
MOD_CAJAS_MOVIMIENTOS = 9
MOD_CAJAS_INGRESOS = 10
MOD_CAJAS_EGRESOS = 11
# GRUPO 3
MOD_USUARIOS = 12
MOD_BLOQUES = 13
MOD_COBROS_MENSUALES = 14
MOD_COBROS_MANUALES = 15
MOD_CONFIGURACIONES_SISTEMA = 16
MOD_SUCURSALES = 17
MOD_PUNTOS = 18
# GRUPO 4
MOD_CORREGIR_LECTURA = 19
MOD_TABLAS_BACKUP = 20
MOD_REPORTES = 21
MOD_PISOS = 22
MOD_CALENDARIO = 23
MOD_ACTIVIDADES = 24
MOD_LISTA_COBROS = 25

# STATUS
STATUS_ACTIVO = 1
STATUS_INACTIVO = 2
STATUS_ELIMINADO = 3
STATUS_ANULADO = 4
# cajas
STATUS_APERTURA = 5
STATUS_APERTURA_RECIBE = 6
STATUS_CIERRE = 7
STATUS_CIERRE_RECIBE = 8
STATUS_NO_APERTURADO = 9
# MOVIMIENTO CAJA
STATUS_MOVIMIENTO_CAJA = 10
STATUS_MOVIMIENTO_CAJA_RECIBE = 11
STATUS_COBRADO = 12
STATUS_PASIVO = 13

# PERFILES
PERFIL_ADMIN = 1
PERFIL_SUPERVISOR = 2
PERFIL_CAJERO = 3
PERFIL_DEPARTAMENTO = 4

# nombre del sistema para reportes
NOMBRE_SISTEMA = 'TeamWork'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
