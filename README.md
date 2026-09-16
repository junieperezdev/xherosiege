# Northfield — Operations Desk

<img width="1089" height="927" alt="image" src="https://github.com/user-attachments/assets/082f2dc5-0582-4d0f-9161-45646a584ce0" />


A small office dashboard: KPIs, weekly calendar, tasks, and team status.
Python (Flask) backend serving a JSON API, plain HTML/CSS/JS frontend.

## Run it

```bash
cd northfield-dashboard
sudo apt install python3-pip python3-venv
pip3 install flask --break-
pip install -r requirements.txt
python3 app.py
```

Then open **http://127.0.0.1:5000** in your browser.

## Project structure

```
northfield-dashboard/
├── app.py              Flask app + API routes + placeholder data
├── requirements.txt
├── templates/
│   └── index.html      Page shell
└── static/
    ├── style.css        Styling (light/dark theme)
    └── script.js        Fetches API data and renders the dashboard
```

## API

| Method | Route                     | Description                          |
|--------|---------------------------|---------------------------------------|
| GET    | `/api/overview`           | Company stats, KPIs, calendar, teams  |
| GET    | `/api/kpis`                | KPI list                             |
| GET    | `/api/calendar`            | Week's events                        |
| GET    | `/api/teams`                | Team statuses                       |
| GET    | `/api/tasks`                | Task list                           |
| POST   | `/api/tasks`                | Add a task (`{title, owner, priority}`) |
| POST   | `/api/tasks/<id>/toggle`    | Toggle a task done/not done          |
| DELETE | `/api/tasks/<id>`           | Remove a task                        |

## Making it real

Everything in `app.py`'s `DATA` dict is placeholder data. To connect real
numbers:

1. Replace `DATA` with queries against your database (Postgres, SQLite,
   whatever you use) or calls out to internal tools (Jira, HR system, CRM).
2. Keep the route shapes the same and the frontend won't need to change.
3. For multiple users editing tasks at once, swap the in-memory list for a
   real database table so changes aren't lost on restart.
