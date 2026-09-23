# practice
this is practice repo

## Run the Flask app

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000/ in a browser. The health endpoint is available at
http://127.0.0.1:5000/health.

## Task management

The app includes a SQLite-backed task manager. From the home page you can add
tasks, mark them complete, and delete them. Task data is stored in
`instance/tasks.db` and is created automatically when the app starts.

Run the test suite with:

```bash
python3 -m pip install pytest
python3 -m pytest
```
