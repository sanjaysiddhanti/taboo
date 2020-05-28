from src.app import db


def create_schema_and_tables():
    db.create_all()


def drop_schema_and_tables():
    db.drop_all()