import json
import os
import uuid
from urllib import urlencode
from flask import Flask, render_template, redirect, url_for, request
from flask.ext.sqlalchemy import SQLAlchemy
import requests
import urlparse
import datetime

app = Flask(__name__)
app.config['SERVER_NAME'] = 'marmoset.iterate.ca'
app.debug = True
db_uri = (
    "postgresql+psycopg2://{0}:{1}@{2}:{3}/{4}".format(
        os.getenv("OPENSHIFT_POSTGRESQL_DB_USERNAME"),
        os.getenv("OPENSHIFT_POSTGRESQL_DB_PASSWORD"),
        os.getenv("OPENSHIFT_POSTGRESQL_DB_HOST"),
        os.getenv("OPENSHIFT_POSTGRESQL_DB_PORT"),
        "marmoset"
    )
)

fb_api_key = "434597593277609"
fb_app_secret = "91be1f6dc17828d953a8cdff997113af"


app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
db = SQLAlchemy(app)

class User(db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  fb_id = db.Column(db.String(128), unique=True)
  fb_name = db.Column(db.String, unique=True)
  fb_access_token = db.Column(db.String)
  fb_expires = db.Column(db.DateTime)
  friends = db.relationship("Friend", lazy="dynamic")

  def __init__(self, fb_id):
    self.fb_id = fb_id

  def __repr__(self):
    return "<User {0} {1} {2}>".format(self.id, self.fb_id, self.fb_access_token)

class Friend(db.Model):
  __tablename__ = 'friends'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  fb_id = db.Column(db.String(128), unique=True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
  fb_id = db.Column(db.String)
  fb_name = db.Column(db.String)
  bot_enabled = db.Column(db.Boolean)

  def __init__(self, user_id, fb_id, fb_name):
    self.user_id = user_id
    self.fb_id = fb_id
    self.fb_name = fb_name
    self.bot_enabled = False

  def __repr__(self):
    return "<User {0} {1} {2}>".format(self.user_id, self.fb_id, self.bot_enabled)

@app.route("/empty")
def empty():
  return ""

@app.route("/login")
def login():
    state = uuid.uuid1()
    url = ("https://www.facebook.com/dialog/oauth?" +
      "client_id={0}&redirect_uri={1}&scope={2}&state={3}".format(
        fb_api_key,
        url_for('loginsuccess', _external=True),
        'xmpp_login',
        state
    ))
    return redirect(url)

@app.route("/loginsuccess")
def loginsuccess():
    state = request.args.get('state', uuid.uuid1())
    #TODO(cbhl): CSRF CHECK
    code = request.args.get('code', '')
    url = ("https://graph.facebook.com/oauth/access_token?" +
      "client_id={0}&redirect_uri={1}&client_secret={2}&code={3}".format(
        fb_api_key,
        url_for('loginsuccess', _external=True),
        fb_app_secret,
        code
    ))
    r_access_token = requests.get(url)
    access_token_dict = urlparse.parse_qs(r_access_token.text)

    me_url = ("https://graph.facebook.com/me?access_token={0}".format(
        access_token_dict[u'access_token'][0]
    ))
    r_me = requests.get(me_url)
    me = r_me.json()
    user = User.query.filter_by(fb_id=me[u'id']).first()
    if user is None:
      user = User(me[u'id'])
    user.fb_name = me[u'name']
    user.fb_access_token = access_token_dict[u'access_token'][0]
    user.fb_expires = (datetime.datetime.utcnow() +
      datetime.timedelta(seconds=int(access_token_dict[u'expires'][0]))
    )
    db.session.add(user)
    db.session.commit()
    return redirect(url_for("manage", id=user.id))

@app.route("/manage/<id>")
def manage(id):
    user = User.query.filter_by(id=id).first()
    friends_url = ("https://graph.facebook.com/me/friends?" + 
      "access_token={0}".format(
        user.fb_access_token
    ))
    r_friends = requests.get(friends_url)
    friends_data = r_friends.json()
    for f in friends_data[u"data"]:
        friend = user.friends.filter_by(fb_id=f[u"id"]).first()
        if friend is None:
            friend = Friend(user.id, f[u"id"], f[u"name"])
            print "Adding new friend: {0}".format(friend)
        db.session.add(friend)
    db.session.commit()
    return render_template("manage.html", user=user, friends=user.friends)

@app.route("/api/v1/friends/<id>")
def apifriends(id):
    user = User.query.filter_by(id=id).first()
    friends_q = user.friends.filter_by(bot_enabled=True)
    friends = [friend.fb_id for friend in friends_q]
    return json.dumps({'friends':friends})

@app.route("/api/v1/manage/<id>")
def apimanage(id):
    pass

@app.route("/")
def hello():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()

