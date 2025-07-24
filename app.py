from flask import Flask, request, render_template
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Google Sheets API setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Open the specific sheet
sheet = client.open("Suivi enfants lait").worksheet("Heure de lait_A")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        date = request.form["date"]
        time = request.form["time"]
        quantite = request.form["milk"]
        change = request.form["changed"]
        pipi = request.form["pee"]
        caca = request.form["poo"]
        remarques = request.form["comment"]

        try:
            # Find the last filled row in column B
            col_b = sheet.col_values(2)
            last_row = len(col_b)

            # Read the formula from column D of the last row (if any)
            previous_formula = sheet.cell(last_row, 4).value  # Column D = 4

            # Insert a new row just after the last one
            insert_row_index = last_row + 1

            # New row with copied formula in column D
            new_row = ["", date, time, previous_formula, quantite, change, pipi, caca, remarques]

            sheet.insert_row(new_row, insert_row_index)

            return "✅ Données enregistrées avec succès !"

        except Exception as e:
            return f"❌ Erreur lors de l'enregistrement: {str(e)}"

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
