![Tests](../../actions/workflows/tests.yml/badge.svg)
# StackTracker

![StackTracker](assets/stacktracker.png)

## Table of Contents
- [Overview](#overview)
- [Technologies Used](#technologies-used)
- [Requirements](#requirements)
- [Local Use (Docker)](#local-use-docker)
- [Tests](#tests)
- [Demo](#demo)

## Overview
StackTracker is a web application designed to help small businesses monitor daily stock and price changes from multiple suppliers.

The system allows users to configure supplier-specific Excel schemas, upload daily stock files, and automatically detect product additions, removals, and price updates.

StackTracker focuses on simplicity and clarity, providing a clean interface while maintaining a well-structured backend architecture suitable for scaling.

Click [here](https://stacktracker-1.onrender.com/) to try it!

## Technologies used
- **[Django](https://www.djangoproject.com/)**: Web development framework that follows the Model–View–Controller design pattern.
- **[PostgreSQL](https://www.postgresql.org/)**: Relational database management system.
- **[Docker](https://www.docker.com/)**: Platform for containerization and service deployment.
- **[Pandas](https://pandas.pydata.org/)**: Python library specialized in data manipulation and analysis.

## Requirements
- Python 3.12+
- Docker + Docker Compose

## Local use (Docker)

To use this project locally, it uses docker compose with a postgres service and local storage. Files will be stored in `supplier_files`

How to use it:

```bash
# Build and start Postgres + Django app
chmod +x entrypoint.sh
docker compose up --build

# App will be available at
# http://localhost:8000/
```

## Tests

To run the tests locally, you need to create a venv and install dependencies first:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then, you can run all tests:

```bash
DJANGO_SETTINGS_MODULE=stacktracker.test_settings python3 manage.py test
```

If you only want to run selected tests:

```bash
python3 manage.py test accounts.tests.test_excel_compare_unit
python3 manage.py test accounts.tests.test_upload_view
```


## Demo
Below are several screenshots showcasing key parts of the application:

![Screen 1 - Home](assets/screen1.png)
![Screen 2 - Login](assets/screen2.png)
![Screen 3 - Dashboard](assets/screen3.png)
![Screen 4 - Suppliers List](assets/screen4.png)
![Screen 5 - Upload](assets/screen5.png)
![Screen 6 - Comparison](assets/screen6.png)





