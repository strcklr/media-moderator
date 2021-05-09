# Backend

This directory contains the backend for the project. It utilizes a RESTful API to to receive files via an HTTP POST, sanitize the input, then feed the file to the machine learning model, finally responding to the request with a prediction. 

The backend is currently in it's very early stages and needs some cleaning up and design work. Eventually, I would like the API flow to look a bit like this:

> Backend: Receives file via POST -> Respond with unique token and status 200 -> Spin up progress page for request at <URL>/api/predict/<TOKEN> -> Begin prediction process

## Requirements

This project uses [Python3](https://www.python.org/downloads/). See which version of Python you have installed as default using:

```bash
python --version
```

To specifically check your Python 3 version, run the following command:

```bash
python3 --version
```

Additionally, the backend depends on [PostgreSQL](https://www.postgresql.org/). Once downloaded, using PGAdmin create a new database and user, then update the source code to reflect that.

### Environment File

To use this project with Docker, you'll need to create your own .env files. On the same level as this README, create a .env file with the following definitions:

```bash
DJANGO_ENV=[production/development]
DEBUG=[0 or 1]
SECRET_KEY=[SECRET KEY]
DJANGO_ALLOWED_HOSTS=[www.example.com localhost 127.0.0.1 [::1]]

DJANGO_ADMIN_USER=[USER]
DJANGO_ADMIN_EMAIL=[EMAIL]
DJANGO_ADMIN_PASSWORD=[PASSWORD]

DATABASE=postgres

DB_ENGINE=django.db.backends.postgresql
DB_DATABASE=[DATABASE]
DB_USER=[USER]
DB_PASSWORD=[PASSWORD]
DB_HOST=[HOST]
DB_PORT=[PORT]
```

## Installation

Run the following command to install requirements:

```bash
pip install -r requirements.txt
```

Once your database is set up, you will then need to run a migration using the following command:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Usage

To run the server, type following in your terminal:

```bash
python manage.py runserver
```

The server should now be running at either localhost:8000 or 127.0.0.1:8000. You can verify this by going to localhost/admin or 127.0.0.1/admin, where you should see a login page.

Once running, you can test the prediction API at 127.0.0.1/api/predict/ directly in the browser or using [Postman](https://www.postman.com/).
