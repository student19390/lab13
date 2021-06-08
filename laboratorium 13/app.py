from flask import Flask, Response, redirect, url_for, request, session, abort, render_template
from flask_login import LoginManager, UserMixin,login_required, login_user, logout_user
import sqlite3 as sql

app = Flask(__name__)

app.config.update(
 DEBUG = False,
 SECRET_KEY = 'sekretny_klucz'
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.name = "user" + str(id)
        self.password = self.name + "_secret"

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)
#login: user1 Password: user1_secret
#generacja uzytkownikow
users = [User(id) for id in range(1, 10)]

@app.route("/login", methods=["GET", "POST"])
def login():
    dane = {'tytul': 'Zalgouj się', 'tresc': 'Zaloguj się do swojego konta.'}
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if password == username + "_secret":
            id = username.split('user')[1]
            user = User(id)
            login_user(user)
            return redirect(url_for("main"))
        else:
            return abort(401)
    else:
        return render_template('formularz_logowania.html', tytul = dane['tytul'], tresc = dane['tresc'])
    
@app.errorhandler(401)
def page_not_found(e):
    dane = {'tytul': 'Coś poszło nie tak...', 'blad': '401'}
    return render_template('blad.html', tytul = dane['tytul'], blad = dane['blad'])

@app.route("/logout")
@login_required
def logout():
    logout_user()
    dane = {'tytul': 'Wylogowanie'}
    return render_template('logout.html', tytul = dane['tytul'])

# przeladowanie uzytkownika
@login_manager.user_loader
def load_user(userid):
    return User(userid)


@app.route("/")
@login_required
def main():
     dane = {'tytul': 'Strona główna', 'tresc': 'Witaj na stronie głównej.'}
     return render_template('index.html', tytul = dane['tytul'], tresc = dane['tresc'])

@app.route("/dodaj")
@login_required
def dodaj():
    dane = {'tytul': 'Dodaj pracownika', 'tresc': 'Dodaj pracownika.'}
    return render_template('dodaj.html', tytul = dane['tytul'], tresc = dane['tresc'])

@app.route('/addrec',methods = ['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        try:
            imienazwisko = request.form['imienazwisko']
            nrpracownika = request.form['nrpracownika']
            adres = request.form['adres']
            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO pracownicy (imienazwisko, nrpracownika, adres) VALUES (?, ?, ?)", (imienazwisko, nrpracownika, adres))
                con.commit()
                msg = "Sukces. Rekord zapisany"
        except:
            con.rollback()
            msg = "Blad. Rekord niezapisany"
        finally:
            return render_template("rezultat.html", tytul = "Rezultat", tresc = msg)
            con.close()

@app.route("/lista")
@login_required
def lista():
    dane = {'tytul': 'Lista pracownikow', 'tresc': 'Lista pracowników'}
    con = sql.connect('database.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM pracownicy")
    rekordy = cur.fetchall()
    con.close()
    return render_template('lista.html', tytul = dane['tytul'], tresc = dane['tresc'], rekordy = rekordy)

if __name__ == "__main__":
    app.run()