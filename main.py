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
        return render_template('boat_creation.html', error = None, success = 'Successfull')
    except:
        return render_template('boat_creation.html', error = 'failed', success = None)

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/<name>')
def greetings(name):
    return render_template('user.html', name = name)


if __name__ == '__main__':
    app.run(debug=True)