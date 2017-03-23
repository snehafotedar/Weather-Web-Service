from flask import Flask, request, make_response, render_template, jsonify, abort, url_for
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask_httpauth import HTTPBasicAuth
from collections import defaultdict
import datetime, requests
from datetime import date, timedelta
import random, ast, json

#Create a engine for connecting to SQLite3.

e = create_engine('sqlite:///weather.db')

app = Flask(__name__)
api = Api(app)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'message': error.description}),404)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}),404)

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'message': error.description}),400)

@app.route('/', methods=['GET','POST'])
def weather():
        return render_template("weather.html")

class Weather_Meta(Resource):
    def get(self):
        #Connect to databse
        conn = e.connect()
    
        #Perform query and return JSON data
        query = conn.execute("select DATE from weather")
        result = [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]
        
        if result == []:
            abort(404, 'Not Found')
        else:
            return make_response(jsonify(result),200)


class Weather_Date(Resource):
    def get(self, userdate):
        conn = e.connect()
        query = conn.execute("select DATE, TMAX, TMIN from weather where Date='%s'"%userdate)
        #Query the result and get cursor.Dumping that data to a JSON is looked by extension
        result = [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]
    
        if result == []:
            abort(404, 'Not Found')
        else:
            r = ast.literal_eval(json.dumps(result))
            res = ", ".join(repr(e) for e in r)
            res = eval(res)

            return make_response(jsonify(res),200)
    
class Delete_Date(Resource):
    def delete(self, userdate):
        conn = e.connect()
        qr = conn.execute("select * from weather where Date='%s'"%userdate)
        result = [dict(zip(tuple(qr.keys()) , i)) for i in qr.cursor]

        if result == []:
            abort(400, 'Bad Request -  Enter valid data')
        else:
            query = conn.execute("delete from weather where Date='%s'"%userdate)

            #Query the result and get cursor.Dumping that data to a JSON is looked by extension
            return make_response(jsonify({'Data deleted for': userdate}), 204) 

@app.route('/historical/', methods=['POST'])
def post():
        conn = e.connect()

        data = request.data
        print data
        print(type(data))

        data = ast.literal_eval(data)
        print data
        print(type(data))

        tmpmax = data['TMAX']
        tmpmin = data['TMIN']
        userdate = data['DATE']

        qr = conn.execute("select * from weather where Date='%s'"%userdate)
        result = [dict(zip(tuple (qr.keys()) ,i)) for i in qr.cursor]

        if result == []:
            query = conn.execute("insert into weather(DATE,TMAX,TMIN) values (?,?,?)",(userdate,tmpmax,tmpmin))
        else:
            query = conn.execute("update weather set TMAX=?,TMIN=? where Date=?",(tmpmax,tmpmin,userdate))
            #Query the result and get cursor.Dumping that data to a JSON is looked by extension
        return make_response(jsonify({'DATE': userdate}), 201)

class Forecast(Resource):
    def get(self, userdate):
        f_date = []
        f_tmax = []
        f_tmin = []
        conn = e.connect()
        qr = conn.execute("select * from weather where Date='%d'"%userdate)
        result = {'Data': [dict(zip(tuple (qr.keys()) ,i)) for i in qr.cursor]}

        if result == {"Data": []}:
            t_date = str(userdate)
            t_tmax = int(t_date[-2:]) + 20
            t_tmin = int(t_date[-2:]) - 20
        else:

            q1 = conn.execute("select DATE from weather where Date='%d'"%userdate)
            q2 = conn.execute("select TMAX from weather where Date='%d'"%userdate)
            q3 = conn.execute("select TMIN from weather where Date='%d'"%userdate)

            c_date = q1.cursor.fetchone()
            c_tmax = q2.cursor.fetchone()
            c_tmin = q3.cursor.fetchone()
            t_date = str(c_date[0]) 
            t_tmax = float(c_tmax[0])
            t_tmin = float(c_tmin[0])

        date_1 = datetime.datetime.strptime(t_date, "%Y%m%d").strftime("%Y-%m-%d")
        date_1a = datetime.datetime.strptime(date_1, "%Y-%m-%d")
    
        t_datenew = date_1a.strftime("%Y%m%d")
        t_tmaxnew = t_tmax + 1.5
        t_tminnew = t_tmin + 0.5

        f_date = f_date + [t_datenew]
        f_tmax = f_tmax + [t_tmaxnew]
        f_tmin = f_tmin + [t_tminnew]

        t_date = f_date[0]
        t_tmax = f_tmax[0]
        t_tmin = f_tmin[0]

    
        for i in range(1,7):
            date_1 = datetime.datetime.strptime(t_date, "%Y%m%d").strftime("%Y-%m-%d")
            date_1a = datetime.datetime.strptime(date_1, "%Y-%m-%d") 
            date_2 = date_1a + datetime.timedelta(days=1)
            t_datenew = date_2.strftime("%Y%m%d")
            t_tmaxnew = t_tmax + 1.5
            t_tminnew = t_tmin + 0.5
            
            f_date = f_date + [t_datenew]
            f_tmax = f_tmax + [t_tmaxnew]
            f_tmin = f_tmin + [t_tminnew]
        
            t_date = f_date[i]
            t_tmax = f_tmax[i]
            t_tmin = f_tmin[i]
        
        result = make_response(jsonify([{'DATE': f_date[0], 'TMAX': f_tmax[0], 'TMIN': f_tmin[0]},{'DATE': f_date[1], 'TMAX': f_tmax[1], 'TMIN': f_tmin[1]},{'DATE': f_date[2], 'TMAX': f_tmax[2], 'TMIN': f_tmin[2]},{'DATE': f_date[3], 'TMAX': f_tmax[3], 'TMIN': f_tmin[3]},{'DATE': f_date[4], 'TMAX': f_tmax[4], 'TMIN': f_tmin[4]},{'DATE': f_date[5], 'TMAX': f_tmax[5], 'TMIN': f_tmin[5]},{'DATE': f_date[6], 'TMAX': f_tmax[6], 'TMIN': f_tmin[6]}]), 200)

        return result

api.add_resource(Weather_Meta, '/historical/')
api.add_resource(Weather_Date, '/historical/<string:userdate>')
api.add_resource(Delete_Date, '/historical/<string:userdate>')
api.add_resource(Forecast, '/forecast/<int:userdate>')

if __name__ == '__main__':
     app.run(debug = True)
