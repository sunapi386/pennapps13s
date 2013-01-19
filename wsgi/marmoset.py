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
        "admin",
        "weNIq4pDKBpB",
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
  fb_access_token = db.Column(db.String)
  fb_expires = db.Column(db.DateTime)

  def __init__(self, fb_id):
    self.fb_id = fb_id

  def __repr__(self):
    return "<User {0} {1}>".format(self.id, self.fb_id)

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
    print r_access_token.text
    access_token_dict = urlparse.parse_qs(r_access_token.text)
    print access_token_dict

    me_url = ("https://graph.facebook.com/me?access_token={0}".format(
        access_token_dict[u'access_token']
    ))
    r_me = requests.get(me_url)
    me = r_me.json()
    print me
    user = User.query.filter_by(fbid=me['id']).first()
    if user is None:
      user = User(me['id'])
    user.access_token = access_token_dict['access_token']
    user.expires = (datetime.utcnow() +
      datetime.timedelta(seconds=int(access_token_dict['expires']))
    )
    db.session.add(user)
    db.session.commit()
    return url
    #return redirect(url_for("hello"))

@app.route("/")
def hello():
    #user = User.query.filter_by(fbid="100005073064107").first()
    #user = User(100005073064107)
    #db.session.add(user)
    #db.session.commit()
    return render_template("index.html")

if __name__ == "__main__":
    app.run()

