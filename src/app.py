import json
import logging
import random
import string

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@postgres:5432"

db = SQLAlchemy(app)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=True)

    def to_json(self):
        return json.dumps({"id": self.id, "name": self.name})


class Prompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_word = db.Column(db.String(25), unique=True)
    banned_words = db.Column(JSONB)

    def to_json(self):
        return json.dumps(
            {
                "id": self.id,
                "target_word": self.target_word,
                "banned_words": self.banned_words,
            }
        )


class GamePrompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prompt_id = db.Column(db.Integer, db.ForeignKey("prompt.id"), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey("game.id"), nullable=False)
    used = db.Column(db.Boolean, nullable=False, default=False)

    game = relationship("Game", uselist=False)
    prompt = relationship("Prompt", uselist=False)


class NameAlreadyTaken(Exception):
    status_code = 500

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


def generate_game_name():
    while True:
        game_name = "".join(random.choice(string.ascii_uppercase) for k in range(4))
        # Make sure another game doesn't have this name
        if not Game.query.filter_by(game_name=game_name).first():
            return game_name


@app.route("/game", methods=["POST"])
def create_game():
    game_name = request.json.get("game_name")
    if game_name:
        if Game.query.filter_by(name=game_name).first():
            raise NameAlreadyTaken(f"A game named {game_name} already exists.")
    else:
        game_name = generate_game_name()
    new_game = Game(name=game_name)
    db.session.add(new_game)
    db.session.flush()

    prompts = Prompt.query.all()
    for prompt in prompts:
        game_prompt = GamePrompt(prompt_id=prompt.id, game_id=new_game.id, used=False)
        db.session.add(game_prompt)
    db.session.commit()
    return new_game.to_json()


@app.route("/game/<game_name>", methods=["GET"])
def get_game(game_name: str):
    game = Game.query.filter_by(name=game_name).first()
    if game:
        return game.to_json()


@app.route("/game/<game_name>/prompts", methods=["GET"])
def get_game_prompts(game_name: str):
    """Get the unused prompts for a game
    """
    game = GamePrompt.query.filter_by(name=game_name).first()
    if game:
        prompts = db.session.query(GamePrompt).join(GamePrompt.game, GamePrompt.prompt).filter(Game.name==game_name, GamePrompt.used==False).paginate()
        return jsonify(prompts)


@app.errorhandler(NameAlreadyTaken)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
