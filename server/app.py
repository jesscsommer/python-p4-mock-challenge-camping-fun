#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

@app.route('/')
def home():
    return ''

class Campers(Resource):
    def get(self):
        campers = [c.to_dict(only =('id', 'name', 'age')) for c in Camper.query.all()]
        return make_response(campers, 200)
    
    def post(self):
        req = request.get_json()
        try: 
            new_camper = Camper(
                name = req.get('name'),
                age = req.get('age')
            )
            db.session.add(new_camper)
            db.session.commit()
            return make_response(new_camper.to_dict(only=('id','name', 'age')), 201)
        except: 
            return make_response({'errors': 'Validation error'}, 400)
    
api.add_resource(Campers, '/campers')

class CampersById(Resource):
    def get(self, id):
        camper = db.session.get(Camper, id)
        if camper: 
            return make_response(camper.to_dict(), 200)
        else:
            response_body = {"error": "Camper not found"}
            return make_response(response_body, 404)
        
    def patch(self, id): 
        camper = db.session.get(Camper, id)
        req = request.get_json()
        if camper: 
            try: 
                for attr in req: 
                    setattr(camper, attr, req.get(attr))
                db.session.add(camper)
                db.session.commit()
                return make_response(camper.to_dict(only=('id', 'name', 'age')), 202)
            except: 
                return make_response({'errors': ['validation errors']}, 400)
        else:
            response_body = {"error": "Camper not found"}
            return make_response(response_body, 404)

api.add_resource(CampersById, '/campers/<int:id>')

class Activities(Resource):
    def get(self): 
        activities = [a.to_dict() for a in Activity.query.all()]
        return make_response(activities, 200)
    
api.add_resource(Activities, '/activities')

class ActivitiesById(Resource):
    def delete(self, id):
        activity = db.session.get(Activity, id)
        if activity: 
            db.session.delete(activity)
            db.session.commit()
            return make_response("", 204)
        else: 
            response_body = {"error": "Activity not found"}
            return make_response(response_body, 404)

api.add_resource(ActivitiesById, '/activities/<int:id>')

class Signups(Resource):
    def post(self):
        req = request.get_json()
        try:
            new_signup = Signup(
                time=req.get('time'),
                camper_id=req.get('camper_id'),
                activity_id=req.get('activity_id')
            )
            db.session.add(new_signup)
            db.session.commit()
            return make_response(new_signup.to_dict(), 201)
        except: 
            return make_response({"errors": ["validation errors"]}, 400)
        
api.add_resource(Signups, '/signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
