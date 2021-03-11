from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import uuid
import jwt
import datetime

##################### SETUP #####################
#################################################

load_dotenv

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASS')}@{os.environ.get('POSTGRES_HOST')}/{os.environ.get('POSTGRES_DB')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


##################### MODELS #####################
##################################################

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(100))


##################### AUTHENTICATION #####################
##########################################################

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token is missing !'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = Users.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message' : 'Token is invalid !'}), 401

        return f(current_user, *args, **kwargs)
    return decorated


##################### ROUTES #####################
##################################################

@app.route('/user', methods=['POST'])
@token_required
def create_user(current_user):
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = Users(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message' : 'New user created !'})


@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):

    users = Users.query.all()

    output = []

    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        output.append(user_data)
    
    return jsonify({'users' : output})

@app.route('/user/<public_id>', methods=['GET'])
@token_required
def get_user(current_user, public_id):

    user = return_user(public_id)

    if not user:
        return jsonify({'message' : 'No user found !'})

    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.password

    return jsonify({'user' : user_data})


@app.route('/user/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):

    user = return_user(public_id)

    if not user:
        return jsonify({'message' : 'No user found !'})

    db.session.delete(user)
    db.session.commit()  

    return jsonify({'message' : f'User {user.name} has been deleted'})


@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required !"'})

    user = Users.query.filter_by(name=auth.username).first()

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required !"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id' : user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        print(token)
        return jsonify({'token' : token})

    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required !"'})


##################### UTILS #####################
#################################################

def return_user(public_id='',name=''):
    if public_id != '':
        return Users.query.filter_by(public_id=public_id).first()

    if name != '':
        return Users.query.filter_by(name=name).first()       


##################### MAIN #####################
##################################################

if __name__ == '__main__':
    app.run(debug=True)