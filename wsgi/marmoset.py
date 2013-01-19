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

print db_uri

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
db = SQLAlchemy(app)

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  fbid = db.Column(db.String(128), unique=True)

  def __init__(self, fbid):
    self.fbid = fbid

  def __repr__(self):
    return "<User {0} {1}>".format(self.id, self.fbid)

@app.route("/")
def hello():
    db.create_all()
    user = User(100005073064107)
    db.session.add(user)
    db.session.commit()
    return "Hello, {0}!".format(user)

if __name__ == "__main__":
    app.run()

