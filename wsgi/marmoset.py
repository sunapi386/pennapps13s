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
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  fb_id = db.Column(db.String(128), unique=True)
  fb_name = db.Column(db.String, unique=True)
  fb_access_token = db.Column(db.String)
  fb_expires = db.Column(db.DateTime)

  def __init__(self, fb_id):
    self.fb_id = fb_id

  def __repr__(self):
    return "<User {0} {1} {2}>".format(self.id, self.fb_id, self.fb_access_token)

class Friend:
  fb_name = ""
  fb_id = ""

  def __init__(self, fb_name, fb_id):
    self.fb_name = fb_name
    self.fb_id = fb_id

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
    print me
    user.fb_name = me[u'name']
    user.fb_access_token = access_token_dict[u'access_token']
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
    print friends_data
    friends = [Friend(f[u"name"], f[u"id"]) for f in friends_data[u"data"]]
    return render_template("manage.html", user=user, friends=friends)

@app.route("/")
def hello():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()

