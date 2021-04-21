FROM python:3.8.5

LABEL author='Talpa Vladimir' version=1 about='YaMdb'

# System environments
ENV LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1

WORKDIR /code

COPY . .

RUN pip install -r /code/requirements.txt

CMD gunicorn api_yamdb.wsgi:application --bind 0.0.0.0:8000