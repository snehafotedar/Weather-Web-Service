from flask import Flask, request, make_response, jsonify, abort, url_for
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask_httpauth import HTTPBasicAuth
from collections import defaultdict
import datetime
from datetime import date, timedelta

#Create a engine for connecting to SQLite3.

e = create_engine('sqlite:///weather.db')

app = Flask(__name__)
api = Api(app)

@app.errorhandler(404)
def not_found(error):
    #response = jsonify({'message': error.description})
    return make_response(jsonify({'message': error.description}),404)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}),404)

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'message': error.description}),400)


class Weather_Meta(Resource):
    def get(self):
        #Connect to databse
        conn = e.connect()
    
        #Perform query and return JSON data
        query = conn.execute("select DATE from weather")
        result = {'Data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
        
        if result == {"Data": []}:
            abort(404, 'Not Found')
        else:
            return result


class Weather_Date(Resource):
    def get(self, userdate):
        conn = e.connect()
        query = conn.execute("select * from weather where Date='%s'"%userdate)
        
        #Query the result and get cursor.Dumping that data to a JSON is looked by extension
        result = {'Data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
    
        if result == {"Data": []}:
            abort(404, 'Not Found')
        else:
            return result
    
class Delete_Date(Resource):
    def get(self, userdate):
        conn = e.connect()
        qr = conn.execute("select * from weather where Date='%s'"%userdate)
        result = {'Data': [dict(zip(tuple(qr.keys()) , i)) for i in qr.cursor]}

        if result == {"Data": []}:
            abort(400, 'Bad Request -  Enter valid data')
        else:
            query = conn.execute("delete from weather where Date='%s'"%userdate)

            #Query the result and get cursor.Dumping that data to a JSON is looked by extension
            return make_response(jsonify({'Data deleted for': userdate}), 200) 

class Insert_Date(Resource):
    def get(self, userdate, tmpmax, tmpmin):
        conn = e.connect()
        if userdate.isnumeric() and tmpmax.isnumeric() and tmpmin.isnumeric():
            qr = conn.execute("select * from weather where Date='%s'"%userdate)
            result = {'Data': [dict(zip(tuple (qr.keys()) ,i)) for i in qr.cursor]}

            if result == {"Data": []}:
                query = conn.execute("insert into weather(DATE,TMAX,TMIN) values (?,?,?)",(userdate,tmpmax,tmpmin))
            else:
                query = conn.execute("update weather set TMAX=?,TMIN=? where Date=?",(tmpmax,tmpmin,userdate))
            #Query the result and get cursor.Dumping that data to a JSON is looked by extension
            return make_response(jsonify({'DATE': userdate}), 201)

        else:
            abort(400, 'Bad Request- Enter valid data')
        #Query the result and get cursor.Dumping that data to a JSON is looked by extension
        #return make_response(jsonify({'DATE': userdate}), 201)

class Forecast(Resource):
    def get(self, userdate):
        f_date = []
        f_tmax = []
        f_tmin = []
        conn = e.connect()
        qr = conn.execute("select * from weather where Date='%d'"%userdate)
        result = {'Data': [dict(zip(tuple (qr.keys()) ,i)) for i in qr.cursor]}

        if result == {"Data": []}:
            abort(400, 'Bad Request -  Enter valid data')
        else:

            q1 = conn.execute("select DATE from weather where Date='%d'"%userdate)
            q2 = conn.execute("select TMAX from weather where Date='%d'"%userdate)
            q3 = conn.execute("select TMIN from weather where Date='%d'"%userdate)

            c_date = q1.cursor.fetchone()
            c_tmax = q2.cursor.fetchone()
            c_tmin = q3.cursor.fetchone()
            t_date = str(c_date[0]) 
            t_tmax = int(c_tmax[0])
            t_tmin = int(c_tmin[0])
    
            for i in range(0,7):
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
        
            return make_response(jsonify([{'DATE': f_date[0], 'TMAX': f_tmax[0], 'TMIN': f_tmin[0]},{'DATE': f_date[1], 'TMAX': f_tmax[1], 'TMIN': f_tmin[1]},{'DATE': f_date[2], 'TMAX': f_tmax[2], 'TMIN': f_tmin[2]},{'DATE': f_date[3], 'TMAX': f_tmax[3], 'TMIN': f_tmin[3]},{'DATE': f_date[4], 'TMAX': f_tmax[4], 'TMIN': f_tmin[4]},{'DATE': f_date[5], 'TMAX': f_tmax[5], 'TMIN': f_tmin[5]},{'DATE': f_date[6], 'TMAX': f_tmax[6], 'TMIN': f_tmin[6]}]), 200)


api.add_resource(Weather_Meta, '/historical')
api.add_resource(Weather_Date, '/historical/<string:userdate>')
api.add_resource(Delete_Date, '/historical/delete/<string:userdate>')
api.add_resource(Insert_Date, '/historical/<string:userdate>,<string:tmpmax>,<string:tmpmin>')
api.add_resource(Forecast, '/forecast/<int:userdate>')

if __name__ == '__main__':
     app.run(debug = True)
