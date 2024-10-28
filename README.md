# semiml

semi-auto Machine Learning for structured data.



## What is semiml?

It’s a Web Application in form of a **REST API**. 

It enables users to upload and store their structured data in form of **.csv** files, allowing them to create **Experiments** to train **ML** models quickly on their uploaded files and have it deployed and ready-to-use through an endpoint to share it with other users.



## Installation

First, please ensure Docker is up and running on your system.

**1. clone repo.**

```bash
git clone https://github.com/mohammedsalah-ai/semiml
```

**2. go to the cloned directory.**

```bash
cd semiml
```

**3. create a .env file, and put the following.**

```txt
ENVIRONMENT=local

# Postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

**4. launch compose.**

```bash
docker compose up
```

**5. Navigate to localhost:8000/docs in your favorite web browser, to access the Swagger API interactive documentation.**

## Walkthrough

https://github.com/user-attachments/assets/e063104a-9789-4625-9e6e-c5a2ce7759f6


## CAPABILITIES

- User Registration.
- User Verification.
- User Login and Forgot Password.
- CSV File Upload and File Management.
- Classification ML Experiment Creation with Uploaded CSV Files.
- Turn ON/OFF Experiment Models LIVE to Accept Inference or to Reject it.
- Inference From Experiment Models.
- MORE TO COME!

## TESTING
Ensure you have a test database up and running with alembic migrations applied, and run
```bash
pytest
```
this will trigger `pytest` tests exploration and run them, <br>
**Note** <br>
tests are written with the `pytest-asyncio` plugin which allows writing asynchronous tests, also tests use `httpx` as it provides access to an asynchronous HTTP client. 
