from flask import Flask
from models import *

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='postgres://jlrgcykuytbvms:e2d5f08001fdd255e15e262b17a1b1f4ea5263ac89e18c23afb46532267c548c@ec2-52-7-15-198.compute-1.amazonaws.com:5432/ddhhda0ru61an6'


db.init_app(app)

def main():
    db.create_all()

if __name__ == "__main__":
    with app.app_context():
        main()
