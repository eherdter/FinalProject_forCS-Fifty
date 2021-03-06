import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify, Response
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

import io
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

import base64

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

@app.route("/")
@login_required
def index():

    return render_template("index.html")

@app.route("/findfriends", methods=["GET", "POST"])
@login_required
def findfriends():
    """Search for new friends"""
     #check to see the pets the user has
    pets = db.execute("SELECT name  FROM pets WHERE user_id=:user_id", user_id=session["user_id"])

    if request.method == "GET":
        return render_template("findfriends.html", pets=pets)

    elif request.method == "POST":

        if not request.form.get("name"):
            return apology("missing pet selection")

        if not request.form.get("zipcode") and not request.form.get("city") and not request.form.get("state"):
            return apology("must enter location search criteria")

        if request.form.get("zipcode") and request.form.get("city") and request.form.get("state"):
            return apology("make only one location selection")

        if request.form.get("zipcode") and request.form.get("state"):
            return apology("make only one location selection")

        if request.form.get("zipcode") and request.form.get("city"):
            return apology("make only one location selection")

        if request.form.get("city") and request.form.get("state"):
            return apology("make only one location selection")

        if not request.form.get("M") and not request.form.get("F") and not request.form.get("NP"):
            return apology("must make selection")

        if request.form.get("M") and request.form.get("F") and request.form.get("NP"):
            return apology("please make one selection")

        if not request.form.get("no") and not request.form.get("yes"):
            return apology("Must tell us if you want to find dog friends of the same breed")

        if request.form.get("no") and request.form.get("yes"):
            return apology("Please make one selection only")

        #obtain name selection and user_id info
        name = request.form.get("name")
        user_id=session['user_id']

        #obtain user information  for location queries, type queries and sex queries
        #this should return a list with one dictionary item (1 row of the db) that has the pets.name (given the selected form input),
        # its type, sex and DOB and joins this to the users table with user_id as foreign key to then get information about the dogs (owners) location where user id
        user_data= db.execute("SELECT pets.name, pets.type, pets.sex, pets.user_id, pets.DOB, users.email, users.zipcode, users.city, users.state FROM pets INNER JOIN users ON pets.user_id = users.id WHERE pets.user_id = :user_id AND pets.name = :name", name=name, user_id=user_id)

        #user_id,  zipcode, city, state FROM users WHERE user_id = :user_id", user_id==session['user_id'])
        zipcode = user_data[0]['zipcode']
        city= user_data[0]['city']
        state = user_data[0]['state']
        type = user_data[0]['type']
        sex=user_data[0]['sex']

        M = "M"
        F = "F"

        #MAKE QUERIES BASED ON ALL COMBINATION OF SELECTION ITEMS..
        #OPTIONS
        #1. By type, postal code, M
        #2. By type, postal code, F
        #3. By type, postal code, NP
        #4. By type, city, M
        #5. By type, city, F
        #6. By type, city, NP
        #7. By type, state, M
        #8. By type, state, F
        #9. By type, state, NP
        #10. N, postal code, M
        #11. N, postal code, F
        #12. N, postal code, NP
        #13. N, city, M
        #14. N, city, F
        #15. N, city, NP
        #16. N, state, M
        #17. N, state, F
        #18. N, state, NP

        #result type
        #type = results[0]["type"]


        #obtain dog information of user for selecting on tyoe
        #results = db.execute("SELECT name, type, sex, DOB FROM pets WHERE name = :name", name = request.form.get("name"))


        #MAKE JOINS to find selection and obtain owners email
        #1. if they selected postal code, Male dogs, and same type
         #found = db.execute("SELECT pets.name, pets.type, pets.sex, pets.user_id, pets.DOB, users.email FROM pets INNER JOIN users ON pets.user_id = users.id WHERE type = :type", type=type)
        # found returns a list of dictionary obkects
        # i.e. for three rows it would be like this   [{name:" ", type: " "}, {}, {} ]

        #just based on location and type


        found = db.execute("SELECT pets.name, pets.type, pets.sex, pets.user_id, users.email, users.zipcode, users.city, users.state FROM pets INNER JOIN users ON pets.user_id = users.id")

        if request.form.get("zipcode"):
            if request.form.get("yes"):
                if request.form.get("M"):
                    filter = [d for d in found if d.get('user_id') != user_id and d.get('zipcode') == zipcode and d.get('type') == type and d.get('sex') == M ]
                elif request.form.get("F"):
                    filter = [d for d in found if d.get('user_id') != user_id and d.get('zipcode') == zipcode and d.get('type') == type and d.get('sex') == F ]
                else:
                    filter = [d for d in found if d.get('user_id') != user_id and d.get('zipcode') == zipcode and d.get('type') == type]
            else:
                if request.form.get("M"):
                    filter = [d for d in found if d.get('user_id') != user_id and d.get('zipcode') == zipcode and d.get('sex') == M]
                elif request.form.get("F"):
                    filter = [d for d in found if d.get('user_id') != user_id and d.get('zipcode') == zipcode and d.get('sex') == F]
                else:
                    filter = [d for d in found if d.get('user_id') != user_id and d.get('zipcode') == zipcode]

        elif request.form.get("city"):
            if request.form.get("yes"):
                if request.form.get("M"):
                    filter = [d for d in found if d.get('user_id') != user_id and d.get('city') == city and d.get('type') == type and d.get('sex') == M]
                elif request.form.get("F"):
                    filter = [d for d in found if d.get('user_id') != user_id and d.get('city') == city and d.get('type') == type and d.get('sex') == F]
                else:
                    filter = [d for d in found if d.get('user_id') != user_id and d.get('city') == city and d.get('type') == type]
            else:
                if request.form.get("M"):
                    filter = [d for d in found if d.get('user_id') != user_id and d.get('city') == city and d.get('sex') == M]
                elif request.form.get("F"):
                    filter = [d for d in found if d.get('user_id') != user_id and d.get('city') == city and d.get('sex') == F]
                else:
                    filter = [d for d in found if d.get('user_id') != user_id and d.get('city') == city]
        else:
            if request.form.get("yes"):
                if request.form.get("M"):
                    filter = [d for d in found if d.get('user_id') != user_id and d.get('state') == state and d.get('type') == type and d.get('sex') == M]
                elif request.form.get('F'):
                    filter = [d for d in found if d.get('user_id') != user_id and d.get('state') == state and d.get('type') == type and d.get('sex') == F]
                else:
                    filter = [d for d in found if d.get('user_id') != user_id and d.get('state') == state and d.get('type') == type]
            else:
                if request.form.get("M"):
                    filter = [d for d in found if d.get('user_id') != user_id and d.get('state') == state and d.get('sex') == M]
                elif request.form.get("F"):
                    filter = [d for d in found if d.get('user_id') != user_id and d.get('state') == state and d.get('sex') == F]
                else:
                    filter = [d for d in found if d.get('user_id') != user_id and d.get('state') == state]

        if len(filter) <= 1:
            return apology("Sorry, there are no other dogs in our database that match your selection... WOOF!")


        #test = [d for d in found if d.get('user_id') != user_id]
        #exclude other dogs that may be of the same type from the user
        #https://stackoverflow.com/questions/1235618/python-remove-dictionary-from-list
        #these two below are visually equivalent
        #found[:] = [d for d in found if d.get('user_id') != user_id]

        #filter = [d for d in found if d.get('user_id') != user_id]

        #test = [d for d in found1 if d.get('user_id') != user_id and d.get('state') == state]
        #filter = [d for d in found if d.get('user_id') != user_id and d.get('state') == state]

        #test = next(item for item in found if item['user_id'] != user_id) - for some reason this throws and error if nothing is in it

        if not filter:
            return apology("no friends that match those selections")

        #return render_template("found.html", results=filter, test=test)
        return render_template("found.html", results=filter, filter=filter)



@app.route("/mypets", methods=["GET", "POST"])
@login_required
def mypets():
    """Show pets"""
    if request.method =="GET":
    # show the pets that the user has registered
        results = db.execute("SELECT name, type, sex, DOB FROM pets WHERE user_id = :user_id", user_id=session['user_id'])
        pets = db.execute("SELECT name, type, sex, DOB FROM pets WHERE user_id = :user_id", user_id=session['user_id'])
        if not pets:
            return apology("To get started add a pet! No time like the present!")

        return render_template("mypets.html", pets=pets)

    elif request.method == "POST":
        pet_name = request.form.get("name")
        weight = request.form.get("weight")
        exercise=request.form.get("exc")
        date = request.form.get("date")

        #insert data into the database userid=session['user_id'] and
        entry = db.execute("INSERT INTO health (user_id, pet_name, weight, exercise, date) VALUES(:user_id, :pet_name, :weight, :exercise, :date)", user_id = session["user_id"], pet_name= pet_name, weight=weight, exercise=exercise, date=date)


    return render_template("mypets.html")
    #return apology("TODO")

@app.route('/plot', methods=["GET", "POST"])
@login_required
def build_plot():

    #pets = db.execute("SELECT DISTINCT pet_name FROM health WHERE user_id=:user_id", user_id=session['user_id'])
    pets = db.execute("SELECT name  FROM pets WHERE user_id=:user_id", user_id=session["user_id"])

    if request.method == "GET":
        return render_template("plot.html", pets=pets)
    #https://stackoverflow.com/questions/41459657/how-to-create-dynamic-plots-to-display-on-flask

    elif request.method == "POST":

        pet_name = request.form.get("name")
        img = io.BytesIO()

        data = db.execute("SELECT weight, exercise, date FROM health WHERE user_id=:user_id AND pet_name = :pet_name", user_id=session['user_id'], pet_name = pet_name)
        if not data:
            return apology("Whoops, looks like you haven't entered any exercise amount into the diary. No time like the present!")

        weight=[]
        for item in data:
            new = item['weight']
            weight.append(new)

        exercise=[]
        for item in data:
            new = item['exercise']
            exercise.append(new)

        date=[]
        for item in data:
            new=item['date']
            date.append(new)

        x=date
        y=exercise
        #y = [1,2,3,4,5]
        #x = [0,2,1,3,4]
        plt.plot(x,y)
        plt.xlabel('Date')
        plt.ylabel('Exercise Time (minutes)')
        plt.savefig(img, format='png')
        img.seek(0)

        plot_url = base64.b64encode(img.getvalue()).decode()

        #return '<img src="data:image/png;base64,{}">'.format(plot_url)
        return render_template('plot.html', plot_url=plot_url)
        #return redirect('plotted')

        #return render_template("plot.html", data=data, new=date)


  #rest of vals follow
  #plt.plot(x, y) #formulate your x, y values before
  #plt.savefig('/app/static/images/filenameXYZ.png') #save to the images directory

@app.route("/new", methods=["GET", "POST"])
@login_required
def new():

    breeds = ["American Pit Bull", "Australian Shepherds","Beagle", "Bloodhound",
    "Boston Terrier", "Boxer", "Bulldog", "Cavalier King Charles Spaniel", "Collie", "Corgi",
    "Dachshund", "Doberman Pinscher", "French Bulldog", "German Shepherd", "Golden Retriever",
    "Great Dane", "Greyhound",  "Labrador Retriever", "Mastiff", "Mixed Breed", "Newfoundland",
    "Pointer (English)", "Pointer (German Shorthaired)","Pomeranian", "Poodle", "Rhodesian Ridgeback",
    "Rottweiler", "Schnauzer", "Shih Tzu","Siberian Husky", "Spaniel (Cocker)", "Spaniel (English Springer)",
    "Vizsla", "Weimeraner","Yorkshire Terrier"]

    if request.method == "POST":

     #      # Ensure name was submitted
        if not request.form.get("name"):
            return apology("must provide name", 403)

    #      # Ensure breed was submitted
        elif not request.form.get("type"):
            return apology("must provide type", 403)

        #      # Ensure sex was submitted
        elif not request.form.get("sex"):
            return apology("must provide sex", 403)

        # Ensure DOB entered
        elif not request.form.get("DOB"):
            return apology("must provide DOB", 403)

        #INSERT INTO DATABASE
        newpet = db.execute("INSERT INTO pets (user_id, name, type, sex, DOB) VALUES(:user_id, :name, :type, :sex, :DOB)", user_id = session["user_id"], name= request.form.get("name"), type=request.form.get("type"), sex=request.form.get("sex"), DOB=request.form.get("DOB"))

        if not newpet:
            return apology("Looks like you've already added this pet to our database. Hopefully your pets don't share names!")

        return redirect("/mypets")

    elif request.method == "GET":
        return render_template("new.html", breeds=breeds)



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()
    if request.method == "GET":
        return render_template("login.html")
    #  # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":

    #      # Ensure username was submitted
        if not request.form.get("email"):
            return apology("Please provide your email.", 403)

    #      # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Please provide your password.", 403)

    #      # Query database for username
        rows = db.execute("SELECT * FROM users WHERE email = :email", email=request.form.get("email"))

          # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Hmm, our sniffing dogs have searched our database and it seems like you've entered an invalid email and/or password.", 403)

         # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

    #     # Redirect user to home page
        #return redirect("/")
        return redirect("/mypets")
        #return apology("TODO")
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

    if request.method == "GET":
        return render_template("register.html")

    elif request.method == "POST":
        if not request.form.get("email"):
            return apology("Please provide your email.")

        if not request.form.get("password") or not request.form.get("confirmation"):
            return apology("Please confirm your password.")

        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Hmm, looks like your passwords don't match.")

        if not request.form.get("zipcode"):
            return apology("Whoops, your zipcode is missing.")

        hash = generate_password_hash(request.form.get("password"))

        #session['user_id'] = result


        #get location based on zipcode input
        location = db.execute("SELECT * FROM places WHERE postal_code = :postal_code", postal_code=request.form.get("zipcode"))

        city = location[0]['place_name']
        state = location[0]['admin_name1']


        #insert user information into users database
        result = db.execute("INSERT INTO users (email, hash, zipcode, city, state) VALUES (:email, :hash, :zipcode, :city, :state)",
                            email = request.form.get("email"), hash=hash, zipcode = request.form.get("zipcode"), city=city, state=state)

        if not result:
            return apology("Hmm, our dog sniffers have searched our database and found that email already in existence.")

    return redirect("/mypets")

    #return redirect("/location")
    #return apology("TODO")

# @app.route("/location")
# def search():
#     """Search for location (with typeahead) on register page when accessed via GET """

#     #Ensure parameters are present
#     if not request.args.get("q"):
#         raise RuntimeError("location not valid")

#     #add on a wildcard to enable autocomplete searching functionality
#     q = request.args.get("q") + "%"

#     #query the database for the place entered
#     place = db.execute("SELECT * FROM places WHERE postal_code LIKE :q OR place_name LIKE :q OR admin_name1 LIKE :q", q=q)

#     return jsonify(place)


#def errorhandler(e):
#    """Handle error"""
#    return apology(e.name, e.code)


# listen for errors
#for code in default_exceptions:
#    app.errorhandler(code)(errorhandler)
