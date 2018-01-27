from flask import Flask, g, request, render_template, Response
from plotly.offline import plot
from plotly.graph_objs import Scatter, Layout
import sqlite3
from functools import wraps

app = Flask(__name__)

DATABASE = '/home/pi/thermopylae/temp_db.sqlite'
db_table = 'temps'

#if __name__ == "__main__":
#        app.run(ssl_context='adhoc',host='0.0.0.0')

def get_db():
        db = getattr(g, '_database', None)
	if db is None:
		db = g._database = sqlite3.connect(DATABASE, timeout=10)
	return db


def is_num(n):
        try:
                float(n)
                return True
        except ValueError:
                return False


def make_control_response(msg, row):
        if row:
                return {'msg': msg, 'curr_setpoint': row['setpoint'], 'curr_offset': row['offset']}
        else:
                return {'msg': msg, 'curr_setpoint': 0, 'curr_offset': 0}


def get_control(msg):
        try:
                db = get_db()
                db.row_factory = sqlite3.Row
                c = db.cursor()
                c.execute("SELECT * FROM control")
                row = c.fetchone()
                return make_control_response(msg, row)
        except sqlite3.Error as e:
                return make_control_response(e.args[0], None)


def update_control(setpoint, offset):
        try:
                db = get_db()
                db.execute("UPDATE control SET setpoint = ?, offset = ?", (setpoint, offset))
                db.commit()
                return False
        except sqlite3.Error as e:
                return make_control_response(e.args[0], None)
        
def check_auth(username, password):
        return username=='leonidas' and password == '+300Spartans'

def authenticate():
        return Response(
                'Could not verify your access level for that URL.\n'
                'You have to login with proper credentials', 401,
                {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
        @wraps(f)
        def decorated(*args,**kwargs):
                auth = request.authorization
                if not auth or not check_auth(auth.username,auth.password):
                        return authenticate()
                return f(*args, **kwargs)
        return decorated
        
@app.teardown_appcontext
def close_connection(exception):
        db = getattr(g, '_database', None)
        if db is not None:
                db.close()

        
@app.route('/')
def report():
        try:
                curr = get_db().cursor()
                result = curr.execute("SELECT datetime(time,'localtime'),water_temp,state1 FROM temps WHERE time > datetime('now','-24 hours')").fetchall()
                if not result:
                        div = ""
                else:
                        timeAx,wTemp,st1 = zip(*result)
                        dWTemp = Scatter(x=timeAx,y=wTemp,mode='lines+markers',marker={'color':st1,'colorscale':[[0,'rgb(100,100,200)'],[1,'rgb(160,64,64)']]},line={'color':'rgb(96,96,96)'})
                        div = plot({"data":[dWTemp]},output_type="div")
        except sqlite3.Error as e:
                div = "DB error: %s" % e.args[0]
        retPage = "<html><head><title>Water Temperature</title></head><body>"+div+"</body></html>"
        return(retPage)
@app.route('/current')
def reportCurrent():
        try:
                curr = get_db().cursor()
                result = curr.execute("SELECT datetime(time,'localtime'),water_temp,state1 FROM temps WHERE time > datetime('now','-1 minute')").fetchall()
                timeAx,wTemp,st1 = zip(*result)
                
        except sqlite3.Error as e:
                div = "DB error: %s" % e.args[0]
        retPage = "<html><head><title>Water Temperature</title></head><body><h1>%3.1f</h1></body></html>"%wTemp[-1]
        return(retPage)

@app.route('/temp/<string:sensor>')
def graphlog(sensor):
        hours = 48
        try:
                curr = get_db().cursor()
                result = curr.execute("SELECT datetime(time,'localtime'),%s FROM temps WHERE time > datetime('now','-%f hours')"%(sensor,hours)).fetchall()
                timeAx,wTemp = zip(*result)
                dWTemp = Scatter(x=timeAx,y=wTemp)
                div = plot({"data":[dWTemp]},output_type="div")
        except sqlite3.Error as e:
                div = "DB error: %s" % e.args[0]
        retPage = "<html><head><title>Water Temperature</title></head><body>"+div+"</body></html>"
        return(retPage)

@app.route('/control', methods=['GET', 'POST'])
@requires_auth
def control():
        if request.method == 'GET':
                params = get_control('')
        if request.method == 'POST':
                setpoint = request.form['setpoint']
                offset = request.form['offset']
                if not is_num(setpoint) or not is_num(offset):
                        params = make_control_response("Invalid input", None)
                else:
                        error = update_control(setpoint, offset)
                        if error:
                                params = make_control_response(e, None)
                        else:
                                params = get_control('Updated to %s, %s' % (setpoint, offset))
        return render_template('control.html', **params)
        
app.run(ssl_context=('cert.pem','key.pem'),host='0.0.0.0')


