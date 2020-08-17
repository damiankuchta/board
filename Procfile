release: python manage.py migrate
web: gunicorn boards_project.wsgi --log-file -
py manage.py collectstatic --noinput