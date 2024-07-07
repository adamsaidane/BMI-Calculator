from flask import Flask, render_template, request, session, redirect, flash, url_for
from cs50 import SQL
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = 'your_secret_key_here'
Session(app)

db = SQL("sqlite:///bmi.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()

    error = ''
    if request.method == "POST":
        if not request.form.get("username"):
            error = 'Must provide username'
            return render_template('register.html', error=error)
        elif not request.form.get("password"):
            error = 'Must provide password'
            return render_template('register.html', error=error)
        elif not request.form.get("mail"):
            error = 'Must provide email adress'
            return render_template('register.html', error=error)
        elif not request.form.get("confirmation"):
            error = 'Must confirm password'
            return render_template('register.html', error=error)
        elif not request.form.get("birth_date"):
            error = 'Must provide birth date'
            return render_template('register.html', error=error)
        elif request.form.get("confirmation") != request.form.get("password"):
            error = 'Password not matching'
            return render_template('register.html', error=error)
        rows = db.execute("SELECT * FROM users WHERE username=? OR email=?",
                          request.form.get("username"), request.form.get("mail"))
        if len(rows) != 0:
            error = 'User exists already'
            return render_template('register.html', error=error)
        db.execute("INSERT INTO users (username, email,birth_date, hash) VALUES (?, ?, ?, ?)",
                   request.form.get("username"), request.form.get("mail"),request.form.get("birth_date") ,generate_password_hash(request.form.get("password")))
        rows = db.execute("SELECT * FROM users WHERE username=?", request.form.get("username"))
        session["user_id"] = rows[0]["id"]
        return redirect("/login")
    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    error = ''
    if request.method == "POST":
        if not request.form.get("username_or_mail"):
            error = 'Must provide username or mail'
            return render_template('login.html', error=error)
        elif not request.form.get("password"):
            error = 'Must provide password'
            return render_template('login.html', error=error)
        rows = db.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?", request.form.get("username_or_mail"), request.form.get("username_or_mail"))
        if len(rows) != 1 or not check_password_hash(
                rows[0]["hash"], request.form.get("password")):
            error = 'Invalid username/email and/or password'
            return render_template('login.html', error=error)
        session["user_id"] = rows[0]["id"]
        return redirect("/")
    else:
        return render_template("login.html")


@app.route('/', methods=['GET', 'POST'])
def index():
    bmi = None
    category = ''
    error = ''
    if request.method == 'POST':
        system = request.form.get("system")
        if system == 'metric':
            height = float(request.form.get("height"))/100
            weight = float(request.form.get("weight"))
            if not weight > 0 and not height > 0:
                error = 'Enter Valid Weight And Height!'
                return render_template('index.html', bmi=bmi, category=category, error=error)
            elif not weight > 0:
                error = 'Enter Valid Weight!'
                return render_template('index.html', bmi=bmi, category=category, error=error)
            elif not height > 0:
                error = 'Enter Valid Height!'
                return render_template('index.html', bmi=bmi, category=category, error=error)
        elif system == 'us':
            height_feet = float(request.form.get("height_feet"))
            height_inches = float(request.form.get("height_inches"))
            weight = float(request.form.get("weight_us"))*0.453592
            height = (height_inches+12*height_feet)*0.0254
            if not weight > 0 and not height > 0:
                error = 'Enter Valid Weight And Height!'
                return render_template('index.html', bmi=bmi, category=category, error=error)
            elif not weight > 0:
                error = 'Enter Valid Weight!'
                return render_template('index.html', bmi=bmi, category=category, error=error)
            elif not height > 0:
                error = 'Enter Valid Height!'
                return render_template('index.html', bmi=bmi, category=category, error=error)
        bmi = weight/(height**2)
        if bmi < 18.5:
            category = 'Underweight'
        elif 18.5 <= bmi < 25:
            category = 'Healthy'
        elif 25 <= bmi < 30:
            category = 'Overweight'
        elif 30 <= bmi < 40:
            category = 'Obese'
        else:
            category = 'Extremely Obese'
        if "user_id" in session:
            db.execute("INSERT INTO bmi_history (user_id,weight,height,bmi,category) VALUES (:user_id,:weight,:height,:bmi,:category)",
                       user_id=session["user_id"], weight=round(weight, 2), height=round(height, 2), bmi=bmi, category=category)
    return render_template('index.html', bmi=bmi, category=category, error=error)


@app.route('/history')
def bmi_history():
    if "user_id" in session:
        history = db.execute(
            "SELECT * FROM bmi_history WHERE user_id=:user_id ORDER BY timestamp DESC", user_id=session["user_id"])
        return render_template("history.html", history=history)
    else:
        return render_template('login.html')


@app.route('/history_graph')
def bmi_history_graph():
    if "user_id" in session:
        history = db.execute("SELECT * FROM bmi_history WHERE user_id=:user_id",
                             user_id=session["user_id"])
        if not history:
            return redirect(url_for('index'))
        dates = [entry["timestamp"] for entry in history]
        bmis = [entry["bmi"] for entry in history]

        import matplotlib.pyplot as plt
        from io import BytesIO
        import base64

        plt.figure(figsize=(12, 8))
        plt.plot(dates, bmis, marker='o', color='black')
        plt.title('BMI History',  fontweight='bold')
        plt.xlabel('Date', fontweight='bold')
        plt.ylabel('BMI', fontweight='bold')
        plt.grid(False)
        plt.xticks(rotation=45)
        plt.tight_layout()

        categories = ['Underweight', 'Healthy', 'Overweight', 'Obese', 'Extremely Obese']
        category_colors_back = ['blue', 'green', 'orange', 'coral', 'darkred']
        category_colors_point = ['blue', 'green', 'yellow', 'red', 'darkred']
        category_ranges = [min(bmis)-1.5, 18.5, 25, 30, 40, max(bmis) + 1.5]

        for i in range(len(category_ranges) - 1):
            plt.axhspan(category_ranges[i], category_ranges[i + 1],
                        color=category_colors_back[i], alpha=0.5)
            plt.text(dates[0], (category_ranges[i] + category_ranges[i + 1]) / 2, categories[i],
                     verticalalignment='top', horizontalalignment='left', color='white', fontweight='bold')

        for i in range(len(dates)):
            for j in range(len(category_ranges) - 1):
                if category_ranges[j] <= bmis[i] < category_ranges[j + 1]:
                    plt.plot(dates[i], bmis[i], marker='o', color=category_colors_point[j])

        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)

        plot_url = base64.b64encode(img.getvalue()).decode()
        return render_template("history_graph.html", plot_url=plot_url)
    else:
        return render_template('login.html')
