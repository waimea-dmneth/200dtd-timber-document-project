#===========================================================
# YOUR PROJECT TITLE HERE
# YOUR NAME HERE
#-----------------------------------------------------------
# BRIEF DESCRIPTION OF YOUR PROJECT HERE
#===========================================================

from flask import Flask, render_template, request, flash, redirect, send_file, jsonify
import html
import io, base64

from app.helpers.session import init_session
from app.helpers.db      import connect_db
# from app.helpers.errors  import init_error, not_found_error
from app.helpers.logging import init_logging
from app.helpers.time    import init_datetime, utc_timestamp, utc_timestamp_now

from app.thing import getDBForm

# Create the app
app = Flask(__name__)

# Configure app
init_session(app)   # Setup a session for messages, etc.
init_logging(app)   # Log requests
# init_error(app)     # Handle errors and exceptions
init_datetime(app)  # Handle UTC dates in timestamps

formID = None

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
# Home page route
#-----------------------------------------------------------
@app.get("/")
def index():
    formID = getDBForm()
    with connect_db() as client:
        # Get all the things from the DB
        sql = "SELECT profile FROM Profile"
        params = []
        results = client.execute(sql, params).rows

        #--------------------------------------------\|/

        sql2 = "Select species, profile FROM Requests WHERE id = ?"
        chosen = client.execute(sql2, [formID]).rows
        species, profile = chosen[0]  # unpack tuple
        chosen = {
        "species": species if species is not None else "none",
        "profile": profile if profile is not None else "none"
        }
            
        return render_template("pages/home.jinja", profiles = results, selected = chosen)


@app.post("/pageSubmit/")
def submit():
    species = request.form.get("species")
    profile  = request.form.get("profile")

    with connect_db() as client:
        sql = "UPDATE Requests SET species = ?, profile = ? WHERE id = ?"
        params = [species, profile, formID]
        client.execute(sql, params)

        return redirect("/details/")

#-----------------------------------------------------------
# details page route
#-----------------------------------------------------------
@app.get("/details/")
def details():
    with connect_db() as client:
        if not formID: chosen = {"species" : "None", "profile" : "None"}
        else :
            sql2 = "Select species, profile FROM Requests WHERE id = ?"
            chosen = client.execute(sql2, [formID]).rows
            
            species, profile = chosen[0]  # unpack tuple
            chosen = {
                "species": species if species is not None else "none",
                "profile": profile if profile is not None else "none"
            }
            
        return render_template("pages/details.jinja", selected = chosen)

#-----------------------------------------------------------
# confirmation page route
#-----------------------------------------------------------
@app.get("/confirmation/")
def confirm():
    return render_template("pages/confirmation.jinja")


#-----------------------------------------------------------
# Things page route - Show all the things, and new thing form
#-----------------------------------------------------------
@app.get("/docs/")
def show_all_things():
    with connect_db() as client:
        # Get all the things from the DB
        sql = "SELECT id, name FROM things ORDER BY name ASC"
        params = []
        result = client.execute(sql, params)
        things = result.rows

        # And show them on the page
        return render_template("pages/docs.jinja", things=things)


#-----------------------------------------------------------
# Thing page route - Show details of a single thing
#-----------------------------------------------------------
# @app.get("/thing/<int:id>")
# def show_one_thing(id):
#     with connect_db() as client:
#         # Get the thing details from the DB
#         sql = "SELECT id, name, price FROM things WHERE id=?"
#         params = [id]
#         result = client.execute(sql, params)

#         # Did we get a result?
#         if result.rows:
#             # yes, so show it on the page
#             thing = result.rows[0]
#             return render_template("pages/thing.jinja", thing=thing)

#         else:
#             # No, so show error
#             return not_found_error()


#-----------------------------------------------------------
# Route for adding a thing, using data posted from a form
#-----------------------------------------------------------
# @app.post("/add")
# def add_a_thing():
#     # Get the data from the form
#     name  = request.form.get("name")
#     price = request.form.get("price")

#     # Sanitise the text inputs
#     name = html.escape(name)

#     with connect_db() as client:
#         # Add the thing to the DB
#         sql = "INSERT INTO things (name, price) VALUES (?, ?)"
#         params = [name, price]
#         client.execute(sql, params)

#         # Go back to the home page
#         flash(f"Thing '{name}' added", "success")
#         return redirect("/things")


# #-----------------------------------------------------------
# # Route for deleting a thing, Id given in the route
# #-----------------------------------------------------------
# @app.get("/delete/<int:id>")
# def delete_a_thing(id):
#     with connect_db() as client:
#         # Delete the thing from the DB
#         sql = "DELETE FROM things WHERE id=?"
#         params = [id]
#         client.execute(sql, params)

#         # Go back to the home page
#         flash("Thing deleted", "success")
#         return redirect("/things")


