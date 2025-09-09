#===========================================================
# YOUR PROJECT TITLE HERE
# David Neth
#-----------------------------------------------------------
# form for a consent document
#===========================================================

from flask import Flask, render_template, request, flash, redirect, send_file, jsonify, session
import html
import io, base64

from app.helpers.session import init_session
from app.helpers.db      import connect_db
# from app.helpers.errors  import init_error, not_found_error
from app.helpers.logging import init_logging
from app.helpers.time    import init_datetime, utc_timestamp, utc_timestamp_now

# Create the app
app = Flask(__name__)

# Configure app
init_session(app)   # Setup a session for messages, etc.
init_logging(app)   # Log requests
# init_error(app)     # Handle errors and exceptions
init_datetime(app)  # Handle UTC dates in timestamps

#-----------------------------------------------------------
# Send Img
#-----------------------------------------------------------

@app.get("/profile_image/<string:profile>")
def profile_image(profile):
    with connect_db() as client:
        sql = "SELECT pic FROM Profile WHERE profile = ?"
        result = client.execute(sql, [profile])  # already a list of dict-like rows

        if result:
            row = result[0]           # first row
            pic_data = row["pic"]     # get the blob
            img_str = base64.b64encode(pic_data).decode("utf-8")
            return jsonify({"image": f"data:image/png;base64,{img_str}"})
        
        # return not_found_error()

#-----------------------------------------------------------
# pagesubmits to session data
#-----------------------------------------------------------

@app.post("/pageSubmit/timber")
def submit():
    session["species"] = request.form.get("species")
    session["profile"]  = request.form.get("profile")
    return redirect("/details/")

@app.post("/pageSubmit/details")
def submit2():
    session["name"] = request.form.get("name")
    session["phoneNum"] = request.form.get("phoneNum")
    session["email"] = request.form.get("email")
    session["cName"] = request.form.get("cName")
    session["address"] = request.form.get("address")
    return redirect("/confirmation/")

#-----------------------------------------------------------
# formsubmits to db
#-----------------------------------------------------------

@app.get("/submitForm/")
def submitForm():
    with connect_db() as client:
        sql = "INSERT INTO Requests (species, profile) VALUES (?, ?) "
        params = [session["species"], session["profile"]]
        client.execute(sql, params)
        session.clear()
        return redirect("/")
#-----------------------------------------------------------
# Home page route
#-----------------------------------------------------------
@app.get("/")
def index():
    if "species" not in session:
        session["species"] = "None"
        session["profile"] = "None"
        session["name"] = "None"
        session["phoneNum"] = "None"
        session["email"] = "None"
        session["cName"] = "None"
        session["address"] = "None"
        session["sessionDocs"] = "None"
        session["PDF"] = "None"

    with connect_db() as client:
        # Get all the things from the DB
        sql = "SELECT profile FROM Profile"
        params = []
        results = client.execute(sql, params).rows

        #--------------------------------------------\|/

        return render_template("pages/home.jinja", profiles = results, species = session["species"], profile = session["profile"])

#-----------------------------------------------------------
# documents page route
#-----------------------------------------------------------


@app.get("/docs/")
def documents():
    return render_template("pages/docs.jinja")

#-----------------------------------------------------------
# details page route
#-----------------------------------------------------------

@app.get("/details/")
def details():
    default = dict(session)
    for k in list(default.keys()):
        if default[k] == "None": default.pop(k)
    return render_template("pages/details.jinja", defaults = default)

#-----------------------------------------------------------
# confirmation page route
#-----------------------------------------------------------
@app.get("/confirmation/")
def confirm():
    return render_template("pages/confirmation.jinja")


