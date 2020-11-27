import os
import time
from flask import Flask, render_template,redirect,url_for,flash
from flask_login import LoginManager, login_user,current_user,login_required,logout_user
from wtform_fields import *
from models import *
from flask_socketio import SocketIO,send,join_room,leave_room



app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY')



app.config['SQLALCHEMY_DATABASE_URI']=os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS')

db = SQLAlchemy(app)

login = LoginManager(app)
login.init_app(app)







@login.user_loader
def load_user(id):
    return User.query.get(int(id))

socketio = SocketIO(app,manage_session=False)

ROOMS = ["movies","news","coding","games"]

@app.route("/",methods=['GET','POST'])
def index():
    reg_form = RegistrationForm()
    if reg_form.validate_on_submit():
        username = reg_form.username.data
        password = reg_form.password.data

        hashed_pwd = pbkdf2_sha256.hash(password)


        user = User(username=username,password=hashed_pwd)
        db.session.add(user)
        db.session.commit()
        flash('Registered successfully. Please login','success')
        return redirect(url_for('login'))

    return render_template("index.html",form = reg_form)

@app.route("/login",methods=['GET','POST'])
def login():
    login_form = LoginForm()

    if login_form.validate_on_submit():
        user_object = User.query.filter_by(username=login_form.username.data).first()
        login_user(user_object)
        return redirect(url_for('chat'))

    return render_template("login.html",form=login_form)

@app.route("/chat",methods=['GET','POST'])
@login_required
def chat():
    if not current_user.is_authenticated:
        flash('Please login.','danger')
        return redirect(url_for('login'))

    return render_template('chat.html',username=current_user.username,rooms=ROOMS)

@app.route("/logout",methods=['GET'])
def logout():

    logout_user()
    flash('you have logged out successfuly.','success')
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@socketio.on('incoming-msg')
def on_message(data):
    msg = data["msg"]
    username = data["username"]
    room = data["room"]
    time_stamp = time.strftime('%b-%d %I:%M%p', time.localtime())
    send({"username":username, "msg":msg, "time_stamp":time_stamp}, room=room)

@socketio.on('join')
def on_join(data):
    username = data["username"]
    room = data["room"]
    join_room(room)
    send({"msg":username + " has joined the " + room + " room."}, room=room)


@socketio.on('leave')
def on_leave(data):
    username = data["username"]
    room = data["room"]
    leave_room(room)
    send({"msg":username + " has left the " + " room."}, room=room)



if __name__ == "__main__":
    socketio.run(app)
