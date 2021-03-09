from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv

app = Flask(__name__)

app.config['SECRET_KEY'] = 'pouecsecret'
app.config['SQLALCHEMY_ALCHEMY_URI'] = f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASS')}@{os.environ.get('POSTGRES_HOST')}/{os.environ.get('POSTGRES_DB')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

if __name__ == '__main__':
    app.run(debug=True)