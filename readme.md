#GhostM2M Project

_REST API for M2M communications based on DJango Framework and oneM2M standard_

This project implements some oneM2M standard parts of HTTP protocol binding for a minimal implementation.

## Pre-requisites
pymongo

## Settings

Under project folder create settings_production.py and settings_development files, then redefine GHOSTM2M dict with your own settings.
Run with "django-admin runserver --settings=maquitta.settings_development" or "django-admin runserver --settings=maquitta.settings_production"

Example of settings_environment.py file:

```
from .settings import *

# GhostM2M configuration
GHOSTM2M = {
    'mongodb': 'mongodb://admin:password@localhost:27017',
    'dbname-test': 'test',
    'dbname': 'mydbname',
    'CSE-ID': 'cseid',
    'admin-user': {
        'username':'admin',
        'pwd': 'mypassword'
    }
}
```

## Test

python manage.py test --settings=ghostm2m.settings_development
python manage.py test --settings=ghostm2m.settings_production