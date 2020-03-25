from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@postgres:5400"
db = SQLAlchemy(app)


@app.route("/")
def hello_world():
    return "Hello, World!"


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(14), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey("game.id"), nullable=False)
    game = db.relationship("Game", backref=db.backref("players", lazy=True))

    def __repr__(self):
        return f"<Player {self.name} in game {self.game_id}>"


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.String(4), unique=True)

    def __repr__(self):
        return f"<Game {self.id}>"


def generate_room_id():
    while True:
        room_id = "".join(random.choice(string.ascii_uppercase) for k in range(4))
        # Make sure another game doesn't have this room ID
        if not Game.query.filter(Game.room_id == room_id).first():
            return room_id
