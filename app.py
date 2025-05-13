#importing Flask module from flask
from flask import Flask , render_template, request, redirect

from flask_mysqldb import MySQL
#import db 
from scraping import scrape_events,save_events_to_db        #events for sydney

from apscheduler.schedulers.background import BackgroundScheduler

app  = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DB'] = 'eventdb'

mysql = MySQL(app)      #help in connecting flask app to mysql db


#using route() of Flask Class to map each function defined below that route to with URL specified 
#inside the route



#default route that redirect to homepage.
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/sydney')
def index():
    cur = mysql.connection.cursor()
    cur.execute("select * from events")
    events = cur.fetchall()

    return render_template('index.html',events = events)




#showing events of australia
@app.route('/australia')
def australia_events():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM events_au")
    events = cur.fetchall()
    return render_template('australia.html', events=events)



@app.route('/get_ticket', methods = ['POST'])
def get_ticket():
    email = request.form['email']
    event_id = request.form['event_id']
    ticket_url = request.form['redirect_url']

    cur = mysql.connection.cursor()
    cur.execute("Insert into emails(email,event_id) values(%s,%s)",(email,event_id))
    mysql.connection.commit()

    return redirect(ticket_url)


@app.route('/scrape')
def scrape():
    events = scrape_events()
    print(f"Inserting {len(events)} events into the database")

    save_events_to_db(events)

    return "Scraping Done!"



#functnion to run scraping of event details in backgorund
def scheduled_scrape():
    print("Running scheduled event scrape...")
    events = scrape_events()
    save_events_to_db(events)


#set up
scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_scrape, 'interval', hours=24)  # Every 24 hours
scheduler.start()

#main fucntion
if __name__ == '__main__':
    app.run(host = '0.0.0.0',port = 5001)
