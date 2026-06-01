from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from dotenv import load_dotenv

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

db = Database()

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/create', methods=['GET', 'POST'])
def create_player():
    if request.method == 'POST':
        playerName = request.form['name']
        playerBalance = request.form['balance']
        db.create_player(playerName, playerBalance)
        return redirect(url_for("home"))
    return render_template("create.html")
        

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        playerName = request.form['name']
        result = db.login(playerName)
        if result:
            session['username'] = playerName
            return redirect(url_for("playerHome"))
        else:
            return "Player not found"
    return render_template("login.html")

@app.route('/playerhome')
def playerHome():
    username = session["username"]
    result = db.login(username)
    balance = result[1]
    return render_template("userPage.html", username=session["username"], balance=balance)


@app.route('/players')
def players():
    all_players = db.getAllPlayers()
    return render_template("players.html", players=all_players)

@app.route('/userPage/update')
def update_balance():
    pass



if __name__ == "__main__":
    app.run(debug=True)






