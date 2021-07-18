# proteins_plus


### Installation

Get Python dependencies with [conda](https://docs.conda.io/en/latest/miniconda.html).
```bash
conda env create -f environment.yml
conda activate pplus
```

The binary files for the tools are placed in `bin/<tool>/`. All paths expected to exist can be found in the `proteins_plus/binaries.json`.

### Getting Started

Activate the conda environment.
```bash
conda activate pplus
```

Open a separate terminal and start the redis-server which is needed by celery which
we use for distributed task execution.
```bash
redis-server
```

Open another separate terminal and start the celery worker.
```bash
celery -A proteins_plus worker --loglevel=INFO
```
...or in a more debug and IDE friendly way:
```bash
python path/to/celery -A fast_grow_server worker --loglevel=INFO
```

At this point either set the environment variables `$USER`, `$PASSWORD` and
`$DATABASE` to the ones configured in the `proteins_plus/settings.py` or
replace them with appropriate values below.

proteins_plus requires a postgres database and a separate database user.
You can create a user with appropriate permissions with this:
```bash
psql -d postgres -c "CREATE ROLE $USER WITH ENCRYPTED PASSWORD '$PASSWORD'; ALTER ROLE $USER WITH LOGIN CREATEDB;"
```
To create the proteins_plus database execute the following:
```bash
psql -d postgres -c "CREATE DATABASE $DATABASE;"
```

Migrate pending changes to the database.
```bash
python manage.py migrate
```

Run unit tests
```bash
python manage.py test
```

To start the server run:
```bash
python manage.py runserver
```
which should start the server at http://localhost:8000/

### API Reference - Swagger

See the interactive API at http://localhost:8000/api/schema/swagger-ui
or download the API schema at http://localhost:8000/api/schema

### Development Guide

Contributions to the project must comply to the following quality criteria to keep the
code maintainable for all developers:

| Criteria               | Threshold     |
| -------------          |:-------------:|
| pylint                 | \>9.0         |
| coverage (overall)     | \>90%         |
| coverage (single file) | \>80%         |


Run pylint for static code quality check with
```bash
find . -type f -name "*.py" | xargs pylint --load-plugins pylint_django --django-settings-module=proteins_plus.settings
```

Run test coverage
```bash
coverage run --source=<path_to_app1>,<path_to_app2> manage.py test
coverage report
```
