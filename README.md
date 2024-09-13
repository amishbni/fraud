# Voter Fraud Detection Using Z-Scores

This project implements a voter fraud detection system by calculating 
the z-score of each vote in relation to the scores cast in the past 24 hours.
By identifying votes that deviate significantly from the recent voting pattern, 
we can flag (and reverse) potential voter fraud or unusual voting behavior.


## Table of Contents
1. [How It Works](#how-it-works)
2. [Installation](#installation)
3. [Building and Running](#building-and-running)
4. [API Documentation](#api-documentation)

## How It Works
This detection system focuses on the following concepts:

1. Z-Score: A statistical measure that tells us how far away a value is from the mean, measured in terms of standard deviation.
$$Z = \dfrac{\left(X - \mu\right)}{\sigma}$$

    Where:
   - $X$ is the individual vote score.
   - $\mu$ is the mean (average) score of votes cast in the last 24 hours.
   - $\sigma$ is the standard deviation of the votes from the last 24 hours.

2. Recent Voting Data: The system analyzes only the votes cast within the last 24 hours to detect sudden changes in behavior.

3. Threshold: A z-score threshold (e.g., 2 or -2) is used to flag votes as potentially fraudulent. Votes with z-scores that exceed this threshold are considered outliers.


## Installation
Make sure to have [docker](https://docs.docker.com/engine/install/) and [docker-compose](https://docs.docker.com/compose/install/linux/) installed on your system.

## Building and Running
Create a random `SECRET_KEY` using Django:

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Create a `.env` file at the root of the project and fill in these variables with appropriate values.

```python
SECRET_KEY="SECRET_KEY"
DEBUG=False
ALLOWED_HOSTS=* # comma-separated hosts to allow

DATABASE_NAME="blog"
DATABASE_USER="db_user"
DATABASE_PASSWORD="db_password"
DATABASE_HOST=database  # must be the same as the name of the database service in docker-compose.yml
DATABASE_PORT=5432

```

Simply run this command to bring the services up.

```shell
docker compose up -d --build
```

Depending on your installation, the *compose* command might be like this:

```shell
docker-compose up -d --build
```

Create a superuser that has admin privileges.
For simplicity, Basic Authentication is chosen as the method to authenticate users.

```shell
docker compose exec -it web bash
python manage.py createsuperuser
```

## API Documentation
You can view the Swagger UI at http://127.0.0.1/swagger.