# Flask Bank Game

A browser-based bank game built with Python and Flask. This project evolved from a JSON-based CLI app, to a SQLite-backed CLI app, and finally into a full web application — still powered by SQLite but now accessible through the browser!

## What it does

- Create players and add them to the database
- Attempt to steal money from other players (outcome is probability based)
- Update player balances
- Delete players from the database
- Session-based authentication — log in as a player to interact as them
- Two different views depending on whether you are logged in or not

## What I learned

- How HTTP sessions work and how to protect routes without using Flask-Login
- How browser caching works and how to prevent stale pages from showing after logout
- How to use Jinja2 templating to render dynamic HTML
- The full request/response cycle in Flask including GET and POST requests

## Tech Stack

- Python / Flask
- SQLite3
- HTML / CSS / Jinja2

## Running locally

**1. Clone the repo**
```
git clone https://github.com/Tharms/flask-bank-game.git
cd flask-bank-game
```

**2. Install dependencies**
```
pip install -r requirements.txt
```

**3. Create a `.env` file in the root directory**
```
FLASK_SECRET_KEY=your_secret_key_here
```

**4. Run the app**
```
python main.py
```

Then open your browser and go to `http://127.0.0.1:5000`
