# Data Server

This app answers requests with data fetched from the database.


## Operation

Launch with `python -m flask --app water run --port 8000`.
Add `--debug` if needed.

Test by visiting `http://localhost:8000`.


## Installation

Install Python v3.11. <https://www.python.org/downloads/release/python-3117/>

Create folder for server app. `users/macombs/stormwater exhibit/data server`

Create virtual environment and install packages.

```shell
c:\ python -m venv venv
c:\ venv\Scripts\activate.bat
c:\ pip install -r requirements.txt
```

Instantiate DB: `python -m flask --app water init-db`.

Load test data into DB: `python -m flask --app water add-test-data`
