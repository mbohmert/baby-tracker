from flask import Flask, request, render_template, redirect, url_for, session
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# 🔐 CHANGE THIS to something secret and random
app.secret_key = "a-very-secret-key"

# ✅ Set your chosen password here
PASSWORD = anatole

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Suivi enfants lait").worksheet("Heure de lait_A")

@app.route("/", methods=["GET", "POST"])
def index():
    if "logged_in" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        date = request.form["date"]
        time = request.form["time"]
        quantite = request.form["milk"]
        change = request.form["changed"]
        pipi = request.form["pee"]
        caca = request.form["poo"]
        remarques = request.form["comment"]

        try:
            # Get the last filled row in column B (date)
            col_b = sheet.col_values(2)
            last_row = len(col_b)

            # Copy the previous formula from column D (Temps entre repas)
            previous_formula = sheet.cell(last_row, 4).value  # Column D = 4

            # Build new row
            new_row = ["", date, time, previous_formula, quantite, change, pipi, caca, remarques]

            # Insert the row just below the last one
            sheet.insert_row(new_row, last_row + 1)

            return "✅ Données enregistrées avec succès !"

        except Exception as e:
            return f"❌ Erreur lors de l'enregistrement: {str(e)}"

    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            return "❌ Mot de passe incorrect", 401

    return '''
        <form method="post">
            <h3>Connexion</h3>
            <label>Mot de passe :</label><br>
            <input type="password" name="password">
            <button type="submit">Se connecter</button>
        </form>
    '''

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
