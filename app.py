import os
import calendar 

from cs50 import SQL 
from datetime import date
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session 
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///calendar.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])
@login_required
def index(): 

    # Months
    months = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }
    # Years
    years = []
    x = range(1900, 2201, 1)
    for n in x:
        years.append(n)
    
    # Days
    days = []
    y = range(1, 32, 1)
    for n in y:
        days.append("%02d" % n)


    if request.method == "POST":
        if request.form.get("cal") == "2":
            try: 
                month = int(request.form.get("month"))
                year = int(request.form.get("year"))
            except ValueError: 
                return apology("invalid submission", 400)
            if month < 1 or month > 12 or year < 1900 or year > 2200:
                return apology("invalid submission", 400)
            cal = calendar.monthcalendar(year,month)
            this_month = months[month]
            # Get Event Data
            if month == 12:
                search_year = year + 1
                search_month1 = "01"
            elif month > 9:
                search_year = year
                search_month1 = month
                search_month2 = month + 1
            elif month == 9:
                search_year = year
                search_month1 = "09"
                search_month2= "10"
            else:
                search_year = year
                search_month1 = "0" + str(month)
                search_month2 = "0" + str(month + 1)
            date1 = str(year) + "-" + search_month1 + "-01"
            date2 = str(search_year) + "-" + search_month2 + "-01"
            yearmonth = str(year) + "-" + search_month1
            events = db.execute("SELECT title, date, starttime, endtime, details, COUNT(date) AS count FROM events WHERE creator = ? and date BETWEEN ? AND ? GROUP BY date", session.get("user_id"), date1, date2)

            num_of_events = []
            for day in days:
                current = yearmonth + "-" + day
                z = db.execute("SELECT COUNT(date) AS count FROM events WHERE date = ?", current)[0]["count"]
                num_of_events.append(z) 
            
            return render_template("index.html", cal=cal, year=year, years=years, month=month, months=months, this_month=this_month, events=events, yearmonth=yearmonth, num_of_events=num_of_events)    
        else: 
            return apology("invalid submission", 400)
    else:
    # Get current time
        today = date.today()
        year = today.year
        month = today.month
        this_month = months[month]
        cal = calendar.monthcalendar(year,month)
    
    # Get event data
        if month == 12:
            search_year = year + 1
            search_month1 = "01"
        elif month > 9:
            search_year = year
            search_month1 = month
            search_month2 = month + 1
        elif month == 9:
            search_year = year
            search_month1 = "09"
            search_month2= "10"
        else:
            search_year = year
            search_month1 = "0" + str(month)
            search_month2 = "0" + str(month + 1)
        date1 = str(year) + "-" + search_month1 + "-01"
        date2 = str(search_year) + "-" + search_month2 + "-01"
        yearmonth = str(year) + "-" + search_month1
        events = db.execute("SELECT title, date, starttime, endtime, details FROM events WHERE creator = ? and date BETWEEN ? AND ?", session.get("user_id"), date1, date2)
       
        num_of_events = []
        for day in days:
            current = yearmonth + "-" + day
            z = db.execute("SELECT COUNT(date) AS count FROM events WHERE date = ?", current)[0]["count"]
            num_of_events.append(z) 

        return render_template("index.html", cal=cal, year=year, years=years, month=month, months=months, this_month=this_month, events=events, yearmonth=yearmonth, num_of_events=num_of_events)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)
        
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Ensure profile name was submitted
        if not request.form.get("profile"):
            return apology("must provide a profile name", 400)

        # Check that username is not already taken
        if not request.form.get("username"):
            return apology("must provide username", 400)
        search = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(search) > 0:
            return apology("username already taken", 400)

        # Check password is filled out and same password confirmed
        if not request.form.get("password"):
            return apology("must provide password", 400)
        elif request.form.get("password") != request.form.get("password") != request.form.get("confirmation"):
            return apology("password does not match", 400)
        
        # Store username and password
        newprofile = request.form.get("profile")
        newuser = request.form.get("username")
        newpass = request.form.get("password")
        newhash = generate_password_hash(newpass, method="pbkdf2:sha256", salt_length=8)
        db.execute("INSERT INTO users (profile_name, username, hash) VALUES (?, ?, ?)", newprofile, newuser, newhash)
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        account = session.get("user_id")
        if request.form.get("profile") == "1":
            if not request.form.get("old-profile"):
                return apology("must enter current profile name", 400)
            if not request.form.get("new-profile"):
                return apology("must enter new profile name", 400)
            current = db.execute("SELECT profile_name FROM users WHERE id = ?", account)
            if current[0]["profile_name"] != request.form.get("old-profile"):
                    return apology("incorrect current profile name", 400)
            db.execute("UPDATE users SET profile_name = ? WHERE id = ?", request.form.get("new-profile"), account)
            return redirect("/settings")
        elif request.form.get("pass") == "2":
            if not request.form.get("old-pass"):
                return apology("must enter current password", 400)
            old = db.execute("SELECT hash FROM users WHERE id = ?", account)[0]["hash"]
            if not check_password_hash(old, request.form.get("old-pass")):
                return apology("current password is incorrect", 400)
            if not request.form.get("new-pass") or not request.form.get("confirm-pass") or request.form.get("new-pass") != request.form.get("confirm-pass"):
                return apology("must enter and confirm new password", 400)
            newhash = generate_password_hash(request.form.get("new-pass"), method="pbkdf2:sha256", salt_length=8)
            db.execute("UPDATE users SET hash = ? WHERE id = ?", newhash, account)
            return redirect("/settings")
        else: 
            return apology("Invalid Submission", 400)
    else:
        return render_template("settings.html")


@app.route("/addevent", methods=["GET", "POST"])
@login_required
def addevent():
    if request.method == "POST":

        # Add checks for valid answers

        title = request.form.get("title")
        date = request.form.get("date")
        start = request.form.get("starttime")
        end = request.form.get("endtime")
        details = request.form.get("details")
        account = session.get("user_id")
        db.execute("INSERT INTO events (creator, title, date, starttime, endtime, details) VALUES(?, ?, ?, ?, ?, ?)", account, title, date, start, end, details)
        return redirect("/")
    else:
        return render_template("addevent.html")

@app.route("/events", methods=["GET"])
@login_required
def events():
    today = date.today()
    account = session.get("user_id")
    past = db.execute("SELECT title, strftime('%m/%d/%Y', date) AS date,starttime, endtime, details FROM events WHERE creator = ? AND date < ? ORDER BY date, starttime", account, today)
    future = db.execute("SELECT title, strftime('%m/%d/%Y', date) AS date,starttime, endtime, details FROM events WHERE creator = ? AND date > ? ORDER BY date, starttime", account, today)
    current = db.execute("SELECT title, strftime('%m/%d/%Y', date) AS date, starttime, endtime, details FROM events WHERE creator = ? AND date = ? ORDER BY starttime", account, today)
    today = today.strftime("%m/%d/%y")
    
    return render_template("events.html", today=today, past=past, future=future, current=current)