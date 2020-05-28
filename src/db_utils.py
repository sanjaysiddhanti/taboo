from src.app import db, Prompt


def create_schema_and_tables():
    db.create_all()


def drop_schema_and_tables():
    db.drop_all()

def seed_db():
    prompts = [{
        "target_word": "pizza",
        "banned_words": ["food", "Domino's", "pepperoni"]
    }, {
        "target_word": "mars",
        "banned_words": ["planet", "space", "moon"]
    }, {
        "target_word": "California",
        "banned_words": ["state", "LA", "San Francisco"]
    }]
    for prompt in prompts:
        p = Prompt(**prompt)
        db.session.add(p)
    db.session.commit()