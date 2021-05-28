import sys
from peewee import *
from config import MODE, DATABASE_FILENAME

db = SqliteDatabase(None)


def init_db():
    if MODE == 'DEBUG':
        db_name = DATABASE_FILENAME
    elif MODE == 'TESTING':
        db_name = ':memory:'
    else:
        sys.exit()  # TODO: exit codes
    db.init(db_name)

    try:
        db.connect()
        db.close()
    except Exception as ex:
        print(f'Something went wrong during DB init: {ex}')
        sys.exit()


@db.connection_context()
def init_tables():
    db.create_tables(
        [
            Person,
        ]
    )


init_db()


class BaseModel(Model):

    class Meta:
        database = db


class Person(BaseModel):
    telegram_id = IntegerField(primary_key=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    phone_number = BlobField(null=True)


init_tables()
