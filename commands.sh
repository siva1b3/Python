



docker build -t django-development:5.2 .







uv init --bare --no-workspace



uv run django-admin startproject backend_trail1 .


uv run python manage.py runserver 0.0.0.0:8000

