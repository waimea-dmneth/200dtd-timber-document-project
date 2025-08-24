#===========================================================
# YOUR PROJECT TITLE HERE
# YOUR NAME HERE
#-----------------------------------------------------------
# BRIEF DESCRIPTION OF YOUR PROJECT HERE
#===========================================================

from flask import Flask, render_template, request, flash, redirect, send_file
import html
import io

from app.helpers.session import init_session
from app.helpers.db      import connect_db
from app.helpers.errors  import init_error, not_found_error
from app.helpers.logging import init_logging
from app.helpers.time    import init_datetime, utc_timestamp, utc_timestamp_now


# Create the app
app = Flask(__name__)

# Configure app
init_session(app)   # Setup a session for messages, etc.
init_logging(app)   # Log requests
init_error(app)     # Handle errors and exceptions
init_datetime(app)  # Handle UTC dates in timestamps

@app.get("/profile_image/<int:profile_id>")
def profile_image(profile_id):
    with connect_db() as client:
        sql = "SELECT pic FROM Profile WHERE profile = %s"
        result = client.execute(sql, [profile_id]).fetchone()
        if result:
            return send_file(io.BytesIO(result['pic']), mimetype='image/png')
        return "Not Found", 404


#-----------------------------------------------------------
# Home page route
#-----------------------------------------------------------
@app.get("/")
def index():
    with connect_db() as client:
        # Get all the things from the DB
        sql = "SELECT * FROM Profile"
        params = []
        results = client.execute(sql, params).rows

        profiles = []
        for row in results:
            img_data = io.BytesIO(row['pic'])
            profiles.append({
                'profile': row['profile'],
                'pic': img_data
            })
        print(profiles)

        return render_template("pages/home.jinja", profiles = profiles)


#-----------------------------------------------------------
# details page route
#-----------------------------------------------------------
@app.get("/details/")
def details():
    return render_template("pages/details.jinja")

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
@app.post("/add")
def add_a_thing():
    # Get the data from the form
    name  = request.form.get("name")
    price = request.form.get("price")

    # Sanitise the text inputs
    name = html.escape(name)

    with connect_db() as client:
        # Add the thing to the DB
        sql = "INSERT INTO things (name, price) VALUES (?, ?)"
        params = [name, price]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"Thing '{name}' added", "success")
        return redirect("/things")


#-----------------------------------------------------------
# Route for deleting a thing, Id given in the route
#-----------------------------------------------------------
@app.get("/delete/<int:id>")
def delete_a_thing(id):
    with connect_db() as client:
        # Delete the thing from the DB
        sql = "DELETE FROM things WHERE id=?"
        params = [id]
        client.execute(sql, params)

        # Go back to the home page
        flash("Thing deleted", "success")
        return redirect("/things")


