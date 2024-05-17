import datetime
from flask_login import UserMixin
from chat_app import app,db,login_manager
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
import jwt
# nullable=False

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255))
    address = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    email = db.Column(db.String(191), unique=True)
    username = db.Column(db.String(191))
    password = db.Column(db.String(191))
    avatar = db.Column(db.String(191))
    create_at = db.Column(db.DateTime(), default=datetime.datetime.utcnow())
    status = db.Column(db.Integer)
    socketio_session_id = db.Column(db.String(191))
    rooms = db.relationship('RoomParticipant', backref='user')
    messages_sent = db.relationship('Messenger', foreign_keys='Messenger.sender_id', backref='sender', lazy='dynamic')
    messages_received = db.relationship('Receiver', backref='receiver', lazy='dynamic')

    
    def get_password_reset_token(self, expires_sec=1800):
        token = jwt.encode(
            {"user_id": self.id, "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_sec)},
            app.config['SECRET_KEY'], algorithm="HS256")
        return token

    @staticmethod
    def verify_password_reset_token(token):
        try:
            decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            user_id = decoded['user_id']
        except:
            return None
        return User.query.get(user_id)

class Room(db.Model):
    __tablename__ = 'Rooms'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, nullable=False)
    create_at = db.Column(db.DateTime)
    status = db.Column(db.Integer)
    participants = db.relationship('RoomParticipant', backref='room')
    messages = db.relationship('Messenger', backref='room', lazy='dynamic')

    
class RoomParticipant(db.Model):
    __tablename__ = 'RoomParticipants'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('Rooms.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    status = db.Column(db.Integer)

class Messenger(db.Model):
    __tablename__ = 'Messengers'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('Rooms.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    create_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    status = db.Column(db.Integer)
    receivers = db.relationship('Receiver', backref='message', lazy='dynamic')



class Receiver(db.Model):
    __tablename__ = 'Receivers'
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('Messengers.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)


class UserBlocks(db.Model):
    __tablename__ = 'UserBlocks'
    
    id = db.Column(db.Integer, primary_key=True)
    blocker_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    blocked_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    create_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    __table_args__ = (
        db.UniqueConstraint('blocker_id', 'blocked_id'),
    )