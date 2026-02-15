#/bin/bash
hg pull
hg up
venv/bin/python manage.py migrate
venv/bin/python manage.py collectstatic --noinput

