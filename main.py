from flask import Flask, render_template, request
from sqlalchemy import create_engine, text

app = Flask(__name__)
conn_str = "mysql://root:cset155@localhost/boatdb"
engine = create_engine(conn_str, echo=True)
conn = engine.connect() # needed for the connection from the database to application

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/boats')

def boats():
    boats = conn.execute(text('select * from boats')).all() # use .all() when retrieving information like we are here
    # print(boats_full) # to verify if data is coming in properly or not. You have to run the boats website once for this function to get called and printed to the terminal
    return render_template('boats.html', boats = boats[:10]) # first is html, second python

@app.route('/boatCreate', methods = ['GET']) # get method
def getBoat():
    return render_template('boat_creation.html')

@app.route('/boatCreate', methods = ['POST']) # post method
def createBoat():
    try:
        conn.execute(text('insert into boats values(:id, :name, :type, :owner_id, :rental_price)'), request.form)
        conn.commit()
        return render_template('boat_creation.html', error = None, success = 'Successfull')
    except:
        return render_template('boat_creation.html', error = 'failed', success = None)

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/searchResults', methods=['GET'])
def search_results():
    search_query = {
        "id": request.args.get("id", "").strip(),
        "name": request.args.get("name", "").strip(),
        "type": request.args.get("type", "").strip(),
        "owner_id": request.args.get("owner_id", "").strip(),
        "rental_price": request.args.get("rental_price", "").strip()
    }

    # Convert numeric values to the correct data type
    params = {}
    query = "SELECT * FROM boats WHERE 1=1"

    if search_query["id"]:
        query += " AND id = :id"
        params["id"] = int(search_query["id"]) 

    if search_query["name"]:
        query += " AND name LIKE :name"
        params["name"] = f"%{search_query['name']}%"

    if search_query["type"]:
        query += " AND type LIKE :type"
        params["type"] = f"%{search_query['type']}%"

    if search_query["owner_id"]:
        query += " AND owner_id = :owner_id"
        params["owner_id"] = int(search_query["owner_id"]) 

    if search_query["rental_price"]:
        query += " AND ROUND(rental_price, 3) = ROUND(:rental_price, 3)"
        params["rental_price"] = float(search_query["rental_price"])

    boats = conn.execute(text(query), params).fetchall()

    return render_template('boats.html', boats=boats)

@app.route('/delete', methods=['GET', 'POST'])
def delete_item():
    if request.method == 'POST':
        boat_id = request.form.get("boat_id")  # Get ID from form input

        if not boat_id:
            return render_template('delete.html', error="Please enter a Boat ID.")

        try:
            boat_id = int(boat_id)  # Ensure it's an integer
            result = conn.execute(text("DELETE FROM boats WHERE id = :id"), {"id": boat_id})
            conn.commit()  # Save changes

            if result.rowcount > 0:
                return render_template('delete.html', success=f"Boat with ID {boat_id} deleted.")
            else:
                return render_template('delete.html', error=f"No boat found with ID {boat_id}.")

        except Exception as e:
            return render_template('delete.html', error=f"Error deleting boat: {e}")

    return render_template('delete.html')  # Show delete page on GET request

@app.route('/update', methods=['GET', 'POST'])
def update_item():
    if request.method == 'GET':
        return render_template("update.html")  # Show the update form

    try:
        # Fetch current highest ID
        result = conn.execute(text("SELECT MAX(id) FROM boats"))
        max_id = result.scalar()  # Get the highest ID
        new_id = (max_id + 1) if max_id else 1  # If no rows exist, start at 1

        # Get data from form
        boat_name = request.form.get("name", "").strip()
        boat_type = request.form.get("type", "").strip()
        owner_id = request.form.get("owner_id", "").strip()
        rental_price = request.form.get("rental_price", "").strip()

        # Ensure required fields are not empty
        if not boat_name or not boat_type or not owner_id or not rental_price:
            return render_template("update.html", error="All fields are required.")

        # Convert necessary values
        owner_id = int(owner_id)
        rental_price = float(rental_price)

        # Insert new boat with auto-incremented ID
        conn.execute(text("""
            INSERT INTO boats (id, name, type, owner_id, rental_price)
            VALUES (:id, :name, :type, :owner_id, :rental_price)
        """), {"id": new_id, "name": boat_name, "type": boat_type, "owner_id": owner_id, "rental_price": rental_price})
        
        conn.commit()  # Save changes

        print(f"Current max ID: {max_id}, New ID: {new_id}")

        return render_template("update.html", success=f"Boat added successfully with ID {new_id}.")

    except Exception as e:
        return render_template("update.html", error=f"Error adding boat: {e}")


@app.route('/<name>')
def greetings(name):
    return render_template('user.html', name = name)


if __name__ == '__main__':
    app.run(debug=True)