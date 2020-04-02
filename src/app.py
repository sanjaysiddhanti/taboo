import logging
import random
import string

from flask import Flask
from flask_socketio import SocketIO, emit, send, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@postgres:5432"
socketio = SocketIO(app)

db = SQLAlchemy(app)

@socketio.on('connect')
def test_connect():
    emit('connected', {'data': 'Connected'})

@socketio.on('hello world')
def hello_world():
    app.logger.info("Hello World!")
    emit('hello world', {'msg': 'hello, world'})

@socketio.on('create game')
def create_game(data):
    app.logger.info("Creating game")
    new_game = Game(room_id=generate_room_id())
    db.session.add(new_game)
    db.session.commit()
    emit('game created', {'id': new_game.id})
    join_game({'username': data['username'], 'room': new_game.room_id})
    db.session.remove()

@socketio.on('join game')
def join_game(data):
    username = data['username']
    room = data['room']
    assert Game.query.filter(Game.room_id==room).count() == 1, 'Game does not exist'
    game = Game.query.filter(Game.room_id==room).first()
    assert game.in_progress == False, 'Game is in progress, too late to join'
    assert game.completed == False, 'Game is already over'
    assert Player.query.filter(Player.game==game, Player.name==username).count() == 0, f'Player {username} is already in room {room}'
    join_room(room)
    player = Player(name=username, game=game)
    db.session.add(player)
    db.session.commit()
    db.session.remove()
    send(f'{username} has entered the room.', room=room)

@socketio.on('start game')
def start_game(data):
    username = data['username']
    room = data['room']
    assert Game.query.filter(Game.room_id==room).count() == 1, 'Game does not exist'
    game = Game.query.filter(Game.room_id==room).first()
    assert game.in_progress == False, 'Game is already in progress'
    assert game.completed == False, 'Game is already over'
    assert Player.query.filter(Player.game==game, Player.name==username).count() == 1, f'Player {username} is is not in the game {game.room_id}. Cannot start it.'
    game.in_progress = True
    db.session.commit()
    send(f'Game {game.room_id} has started.', room=room)
    db.session.remove()


@socketio.on('end game')
def start_game(data):
    room = data['room']
    assert Game.query.filter(Game.room_id==room).count() == 1, 'Game does not exist'
    game = Game.query.filter(Game.room_id==room).first()
    assert game.in_progress == True, "Game is not in progress; can't end it"
    assert game.completed == False, 'Game is already over'
    game.in_progress = False
    game.completed = True
    db.session.commit()
    send(f'Game {game.room_id} has finished.', room=room)
    db.session.remove()

@socketio.on_error()        # Handles the default namespace
def error_handler(e):
    raise e

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
    in_progress = db.Column(db.Boolean, nullable=False, default=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"<Game {self.id}>"


def generate_room_id():
    while True:
        room_id = "".join(random.choice(string.ascii_uppercase) for k in range(4))
        # Make sure another game doesn't have this room ID
        if not Game.query.filter_by(room_id=room_id).first():
            return room_id

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)