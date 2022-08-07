from __future__ import annotations

import typing

import pydantic
from flask import Flask, jsonify, request
from flask.views import MethodView
from sqlalchemy import Column, Integer, String, DateTime, func, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


class HttpError(Exception):
    def __init__(self, status_code: int, massage: str | list | dict):
        self.status_code = status_code
        self.message = massage

class CreateMail(pydantic.BaseModel):
    header: str
    description: str

class PatchMail(pydantic.BaseModel):
    header: typing.Optional[str]
    description: typing.Optional[str]

def validate(model, raw_data: dict):
    try:
        return model(**raw_data).dict()
    except pydantic.ValidationError as error:
        raise HttpError(400, error.errors())



app = Flask('app')

@app.errorhandler(HttpError)
def http_error_handler(error: HttpError):
    response = jsonify({
        'status': 'error',
        'reason': error.message
    })
    response.status_code = error.status_code
    return response

PG_DSN = 'postgresql://postgres:postgres@127.0.0.1/flask'

engine = create_engine(PG_DSN)
Session = sessionmaker(bind=engine)

Base = declarative_base()

class Mail(Base):

    __tablename__ = 'mails'
    id = Column(Integer, primary_key=True)
    header = Column(String, nullable=False)
    description = Column(String, nullable=False)
    sender = Column(String, nullable=True)
    date_creation = Column(DateTime, server_default=func.now())

def get_mail(session: Session, mail_id: int):
    with Session() as session:
        mail = session.query(Mail).get(mail_id)
        if mail is None:
            raise HttpError(404, 'mail not found')
        return mail

Base.metadata.create_all(engine)

class MailView(MethodView):

    def get(self, mail_id:int):
        with Session() as session:
            mail = get_mail(session, mail_id)
            return jsonify({'header': mail.header, 'date_creation': mail.date_creation.isoformat()})

    def post(self):
        validated = validate(CreateMail, request.json)
        with Session() as session:
            mail = Mail(header=validated['header'], description=validated['description'])
            session.add(mail)
            session.commit()
            return {'id': mail.id}


    def patch(self, mail_id: int):
        validated = validate(PatchMail, request.json)

        with Session() as session:
            mail = get_mail(session, mail_id)
            if validated.get('header'):
                mail.header = validated['header']
            if validated.get('description'):
                mail.description = validated['description']
            session.add(mail)
            session.commit
            return {
                'header': mail.header,
                'description': mail.description,
                'id': mail.id
            }

    def delete(self, mail_id: int):
        with Session() as session:
            mail = get_mail(session, mail_id)
            session.delete(mail)
            session.commit()
            return {'status': 'succes'}

mail_view = MailView.as_view('mails')
app.add_url_rule('/mails/', view_func=mail_view, methods=['POST'])
app.add_url_rule('/mails/<int:mail_id>', view_func=mail_view, methods=['GET','PATCH', 'DELETE'])


# @app.route('/test/', methods=['GET'])
# def test():
#
#     return jsonify({'status': 'ok'})
#

app.run()