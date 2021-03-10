from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid

load_dotenv

app = Flask(__name__)

app.config['SECRET_KEY'] = 'pouecsecret'
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASS')}@{os.environ.get('POSTGRES_HOST')}/{os.environ.get('POSTGRES_DB')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(100))

@app.route('/user', methods=['GET'])
def get_all_users():
    return ''

@app.route('/user/<user_id>', methods=['GET'])
def get_user():
    return ''

@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = Users(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message' : 'New user created !'})

@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user():
    return ''

#db.create_all()

if __name__ == '__main__':
    app.run(debug=True)