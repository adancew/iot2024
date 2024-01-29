"""
Django settings for vending project.

Generated by 'django-admin startproject' using Django 5.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

DEPLOY = True

ALLOWED_HOSTS = [
    '10.108.33.110',
    'localhost',
    '127.0.0.1'
]

if DEPLOY:
    BROKER_IP = '10.108.33.125'
else:
    BROKER_IP = 'localhost'
