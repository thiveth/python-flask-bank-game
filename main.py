from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from dotenv import load_dotenv
from random import randint

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

class Database:
    def __init__(self):
        con = sqlite3.connect("players.db")
        cur = con.cursor()
        cur.execute("""
                         CREATE TABLE IF NOT EXISTS players (
                            name TEXT PRIMARY KEY,
                            balance INTEGER
                        )
                         """)
        con.commit()
        con.close()

    def login(self, playerName):

        con = sqlite3.connect("players.db")
        cur = con.cursor()
        result = cur.execute("SELECT name, balance FROM players WHERE name = ?", (playerName,)).fetchone()
        con.close()
        return result
    
    def getAllPlayers(self):

        con = sqlite3.connect("players.db")
        rows = con.execute("SELECT name, balance FROM players").fetchall()
        con.close()
        return rows
    
    def update_balance(self, playerName, newBalance):

        con = sqlite3.connect("players.db")
        cur = con.cursor()
        result = cur.execute("SELECT name FROM players WHERE name = ?",(playerName,)).fetchone()

        if result:
            cur.execute("UPDATE players SET balance = ? WHERE name = ?", (newBalance, playerName))
            con.commit()
            print("Executed")
        else:
            print(f"{playerName} doesn't exist")
    
    def create_player(self, playerName, playerBalance):

        con = sqlite3.connect("players.db")
        cur = con.cursor()
        cur.execute("INSERT INTO players VALUES (?, ?)", (playerName, playerBalance))
        con.commit()

    def stealMoney(self, playerName, opponentName):

        con = sqlite3.connect("players.db")
        cur = con.cursor()
        player = cur.execute("SELECT name, balance FROM players WHERE name = ?",(playerName,)).fetchone()
        opponent = cur.execute("SELECT name, balance FROM players WHERE name = ?",(opponentName,)).fetchone()
        if not player or not opponent:
            return "Error: one or more players does not exist!"
        elif player[1] == 0 or opponent[1] == 0:
            return "One or more of you has no money.. Try" \
            " updating whoever has a low balance first!"
        else:
            probability = randint(1, 3)
            if probability == 3:
                cur.execute("UPDATE players SET balance = balance + ? where name = ?",(opponent[1], playerName))
                cur.execute("UPDATE players SET balance = 0 where name = ?",(opponent[0],))
                con.commit()
                return f'{player[0]} successfully stole ${opponent[1]} from {opponent[0]}!'
            else:
                cur.execute("UPDATE players SET balance = balance + ? where name = ?",(player[1], opponentName))
                cur.execute("UPDATE players SET balance = 0 where name = ?",(player[0],))
                con.commit()
                return f'{player[0]} failed to steal from {opponent[0]} and lost their balance of ${player[1]}!'

    def removePlayer(self, playerName):
        con = sqlite3.connect("players.db")
        cur = con.cursor()
        result = cur.execute("SELECT name, balance FROM players WHERE name = ?", (playerName,)).fetchone()
        if result:
            cur.execute("DELETE FROM players WHERE name = ?", (playerName,))
            con.commit()
            print(f"Player {playerName} has been removed")
        else:
            print(f"Player {playerName} doesn't exist.")

db = Database()

@app.before_request
def load_user():
    if "username" in session:
        if request.endpoint not in ("playerHome", "logout", "static", "players", "steal_money", "update_balance"):
            return redirect(url_for("playerHome"))


@app.after_request
def no_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route('/')
def home():
    return render_template("home.html")

@app.route('/create', methods=['GET', 'POST'])
def create_player():
    if request.method == 'POST':
        try:
            playerName = request.form['name']
            playerBalance = request.form['balance']
            db.create_player(playerName, playerBalance)
        except sqlite3.IntegrityError:
            flash(f"Player: {playerName} already exists!")
            return render_template("create.html")
        else:
            return redirect(url_for("home"))
    return render_template("create.html")
        

@app.route('/login', methods=['GET','POST'])
def login():

    if "username" in session:
        return redirect(url_for("playerHome"))

    if request.method == 'POST':
        playerName = request.form['name']
        result = db.login(playerName)
        if result:
            session['username'] = playerName
            return redirect(url_for("playerHome"))
        else:
            return flash("Player not found")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route('/playerhome')
def playerHome():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    result = db.login(username)
    balance = result[1]
    return render_template("userPage.html", username=session["username"], balance=balance)


@app.route('/players')
def players():
    all_players = db.getAllPlayers()
    if "username" in session:
        username = session.get("username")
        result = db.login(username)
        balance = result[1]
        return render_template("players.html", players=all_players, username=username,balance=balance)
    else:
        return render_template("players.html", players=all_players, username=None, balance=None)

@app.route('/update_balance', methods=['POST'])
def update_balance():
    if "username" in session:
        playerName = session["username"]
        newBalance = int(request.form["balance"])
        db.update_balance(playerName, newBalance)
        flash(f"Balance updated to {newBalance} for {playerName}!")
        return redirect(url_for("players"))
    else:
        playerName = request.form["playerName"]
        newBalance = int(request.form["balance"])
        db.update_balance(playerName, newBalance)
        flash(f"Balance updated to {newBalance} for {playerName}!")
        return redirect(url_for("players"))

@app.route('/steal_money', methods=['POST'])
def steal_money():
    if "username" in session:
        playerName = session.get("username")
        victim = request.form['steal']
        message = db.stealMoney(playerName, victim)
        flash(message)
        return redirect(url_for("players"))
    else:
        playerName = request.form["stealerName"]
        victim = request.form["targetName"]
        message = db.stealMoney(playerName, victim)
        flash(message)
        return redirect(url_for("players"))

@app.route('/remove_player', methods=['POST'])
def remove_player():
    playerName = request.form["remove"]
    db.removePlayer(playerName)
    if session.get("username") == playerName:
        session.clear()
        return redirect(url_for("home"))
    flash(f"{playerName} has been removed.")
    return redirect(url_for("players"))


if __name__ == "__main__":
    app.run(debug=True)
