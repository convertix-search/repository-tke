#/bin/bash
hg pull
hg up
leadformenv/bin/python manage.py migrate
leadformenv/bin/python manage.py collectstatic --noinput

