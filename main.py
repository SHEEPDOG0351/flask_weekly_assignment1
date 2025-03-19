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
        params["id"] = int(search_query["id"])  # Convert to int

    if search_query["name"]:
        query += " AND name LIKE :name"
        params["name"] = f"%{search_query['name']}%"

    if search_query["type"]:
        query += " AND type LIKE :type"
        params["type"] = f"%{search_query['type']}%"

    if search_query["owner_id"]:
        query += " AND owner_id = :owner_id"
        params["owner_id"] = int(search_query["owner_id"])  # Convert to int

    if search_query["rental_price"]:
        query += " AND ROUND(rental_price, 3) = ROUND(:rental_price, 3)"
        params["rental_price"] = float(search_query["rental_price"])  # Convert to float

    boats = conn.execute(text(query), params).fetchall()

    return render_template('boats.html', boats=boats)



@app.route('/<name>')
def greetings(name):
    return render_template('user.html', name = name)


if __name__ == '__main__':
    app.run(debug=True)