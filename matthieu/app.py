from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from hashlib import sha256
from datetime import datetime, timedelta
import jwt
from functools import wraps
from internal_lib.bruteforce import BruteForcer


CLASSES = {
    "brute_forcer": BruteForcer
}

# charger le .env
load_dotenv()

# créer le serveur d'api
app = Flask(__name__)

# config db
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASS')}@{os.environ.get('POSTGRES_HOST')}/{os.environ.get('POSTGRES_DB')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# db object
db = SQLAlchemy(app)


# model user
class User(db.Model):

    __tablename__ = 'auth_user'

    id = db.Column('id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(100))
    password = db.Column('password', db.String(255))


# model project
class Project(db.Model):

    __tablename__ = 'app_project'

    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String(100))
    token = db.Column('token', db.String(300))
    url = db.Column('url', db.String(300))
    tests = db.relationship("PenTest")


# model pentest
class PenTest(db.Model):

    __tablename__ = 'app_pentest'

    id = db.Column('id', db.Integer, primary_key=True)
    entity = db.Column('entity', db.String(50))
    attr = db.Column('attr', db.String(50))
    value = db.Column('value', db.String(100))
    project_id = db.Column(db.Integer, db.ForeignKey('app_project.id'))


# authentication
@app.route('/auth', methods=['GET'])
def auth():

    creds = request.authorization

    if not creds or not creds.username or not creds.password:
        return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

    try:
        username = User.query.filter_by(username=creds.username).first().username
        project_token = Project.query.filter_by(token=sha256(creds.password.encode()).hexdigest())
    except:
        return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})
    else:
        token = jwt.encode({
            'username': username,
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }, app.config['SECRET_KEY'])
        return jsonify({'token': token})


# décorateur de vérification du token
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None if 'x-access-tokens' not in request.headers else request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'a valid token is missing'})

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], options={"verify_signature": False})
            user = User.query.filter_by(username=data['username']).first()
        except:
            return jsonify({'message': "token is invalid"})
        else:
            return f(user, *args, **kwargs)
    return decorator


@app.route('/project/<project_token>', methods=['GET'])
@token_required
def get_project( _, project_token):
    project = Project.query.filter_by(token=project_token).first()
    tests = list(set(map(lambda obj: obj.entity, project.tests)))
    return jsonify({
        "name": project.name,
        "url": project.url,
        "tests": tests
    })


@app.route('/launch/<project_token>', methods=['POST'])
@token_required
def launch_tests(_, project_token):
    project = Project.query.filter_by(token=project_token).first()
    to_launch = {entity: {} for entity in request.json["to_test"]}
    results = {}
    for t in project.tests:
        if t.entity not in to_launch:
            continue
        to_launch[t.entity][t.attr] = t.value
    for entity, params in to_launch.items():
        results[entity] = CLASSES[entity](**params).launch()
    return jsonify(results)


# run app
if __name__ == "__main__":
    app.run("0.0.0.0", 8000, debug=True)
