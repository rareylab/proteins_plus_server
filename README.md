# ProteinsPlus

## Installation

Get Python dependencies with [conda](https://docs.conda.io/en/latest/miniconda.html).
```bash
conda env create -f environment.yml
conda activate pplus
```

The executable files for the integrated tools should be placed in **bin/toolname/**.
E.g.: bin/preprocessor/

## Getting Started

There are a few commands you need to execute to get the server running. Make sure you have activated
your conda environment with:
```bash
conda activate pplus
```

Open a separate terminal and start the redis server which is needed by celery which we use for
distributed task execution.
```bash
redis-server
```

Open another separate terminal and start the celery worker.
```bash
celery -A proteins_plus worker -O fair --loglevel=INFO
```

At this point either set the environment variables `$USER`, `$PASSWORD` and `$DATABASE` to the ones
configured in the `proteins_plus/settings.py` or replace them with appropriate values below.

proteins_plus requires a postgres database and a separate database user. You can create a user with
appropriate permissions with this:
```bash
psql -d postgres -h localhost -c "CREATE ROLE $USER WITH ENCRYPTED PASSWORD '$PASSWORD'; ALTER ROLE $USER WITH LOGIN CREATEDB;"
```
To create the proteins_plus database execute the following:
```bash
psql -d postgres -h localhost -U $USER -c "CREATE DATABASE $DATABASE;"
```

Migrate pending changes to the database. You need to repeat this step whenever you have made any
changes to the project's database **Models**.
```bash
python manage.py makemigrations
python manage.py migrate
```

Generate the API schema with this command:
```bash
python manage.py spectacular --file schema.yml
```

To start the server run:
```bash
python manage.py runserver
```

Now the server is running at http://localhost:8000/.

## Running tests

You can run the included unit tests with
```bash
python manage.py test                    # Run all unit tests
python manage.py test <path_to_app>      # Only run unit tests for specific application
```

Run test coverage

```bash
coverage run manage.py test <path_to_app>
coverage report
```

Run pylint for static code quality check with

```bash
find . -type f -name "*.py" | xargs pylint --load-plugins pylint_django --django-settings-module=proteins_plus.settings
```

## Development Guide

If you intend to work with the server's code, please read the Developer Guide found in
**Developer-Guide.md**. 
