import json
import logging
import os
import random
import string

import settings

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI")

db = SQLAlchemy(app)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Prompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_word = db.Column(db.String(25), unique=True)
    banned_words = db.Column(JSONB)

    def to_dict(self):
        return {
            "id": self.id,
            "target_word": self.target_word,
            "banned_words": self.banned_words,
        }


class GamePrompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prompt_id = db.Column(db.Integer, db.ForeignKey("prompt.id"), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey("game.id"), nullable=False)
    used = db.Column(db.Boolean, nullable=False, default=False)

    game = relationship("Game", uselist=False)
    prompt = relationship("Prompt", uselist=False)

    def to_dict(self):
        return {
            "id": self.id,
            "prompt_id": self.prompt_id,
            "game_id": self.game_id,
            "used": self.used,
        }


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


class EntityNotFound(Exception):
    status_code = 404

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


@app.route("/", methods=["GET"])
def ping():
    return "pong", 200


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
    return jsonify(new_game.to_dict())


@app.route("/game/<game_name>", methods=["GET"])
def get_game(game_name: str):
    game = Game.query.filter_by(name=game_name).first()
    if game:
        return jsonify(game.to_dict())


@app.route("/game/<game_name>/prompts", methods=["GET"])
def get_game_prompts(game_name: str):
    """Get the unused prompts for a game
    """
    game = Game.query.filter_by(name=game_name).first()
    page = int(request.args.get("page", 1))
    if game:
        prompts = (
            db.session.query(GamePrompt, Prompt)
            .join(GamePrompt.game, GamePrompt.prompt)
            .filter(Game.name == game_name, GamePrompt.used == False)
            .paginate(page=page)
        )
        response = [
            (game_prompt.to_dict(), prompt.to_dict())
            for (game_prompt, prompt) in prompts.items
        ]
        response = {
            "prompts": [
                dict(prompt, **game_prompt) for game_prompt, prompt in response
            ],
            "page": page,
            "num_pages": prompts.pages,
        }
        return jsonify(response)


@app.route("/game_prompt/update", methods=["PUT"])
def update_game_prompt():
    game_prompt_id = request.json.get("game_prompt_id")
    game_prompt = GamePrompt.query.get(game_prompt_id)
    if not game_prompt:
        raise EntityNotFound(f"Could not find a GamePrompt with id {game_prompt_id}")
    game_prompt.used = True
    db.session.add(game_prompt)
    db.session.commit()
    return jsonify(), 204


@app.errorhandler(NameAlreadyTaken)
def handle_name_already_exists(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(EntityNotFound)
def handle_entity_not_found(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

if __name__ == '__main__':
    app.run()