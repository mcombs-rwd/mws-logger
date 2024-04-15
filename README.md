# Data Server

This app provides a REST API to get measurements from water meters and the
rain gauge associated with the Stormwater project. Queries can specify a
specific sensor, date range, and hour/day/week/month resolution for history.
It supports XML and CSV formats for easy import into spreadsheets,
and JSON for use by the Stormwater Exhibit app.


## Operation

Change working directory with `cd data_server`.
Launch with `python -m flask --app water run --port 8000`.
Add `--debug` if needed.

Test by visiting `http://localhost:8000`.


## Installation

Install Python v3.11. <https://www.python.org/downloads/release/python-3117/>

Create folder for server app. `users/macombs/stormwater exhibit/data server`

Create virtual environment and install packages.

```shell
c:\ cd 'data_server'
c:\ python -m venv venv
c:\ venv\Scripts\activate.bat
c:\ pip install -r requirements.txt
```

Instantiate DB: `python -m flask --app water init-db`.

Load test data into DB: `python -m flask --app water add-test-data`
