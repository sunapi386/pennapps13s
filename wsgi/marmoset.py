import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
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


app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
db = SQLAlchemy(app)

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  fbid = db.Column(db.String(128), unique=True)

  def __init__(self, fbid):
    self.fbid = fbid

  def __repr__(self):
    return "<User {0} {1}>".format(self.id, self.fbid)

@app.route("/")
def hello():
    #user = User.query.filter_by(fbid='100005073064107').first()
    #user = User(100005073064107)
    #db.session.add(user)
    #db.session.commit()
    return render_template("index.html")

if __name__ == "__main__":
    app.run()

