release: python3 manage.py migrate
# web: gunicorn mysite.wsgi

web: daphne mysite.asgi:application --port $PORT --bind 0.0.0.0 -v2