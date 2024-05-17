import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
import logging
from flask_jwt_extended import JWTManager,jwt_required, get_jwt_identity
from logging.handlers import RotatingFileHandler





app = Flask(__name__)
app.config.from_object('Config.config.DevelopmentConfig')
csrf = CSRFProtect(app)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
mail = Mail(app)
socketio = SocketIO(app,cors_allowed_origins="*")
jwt = JWTManager(app)
logging.basicConfig(filename='app.log', level=logging.INFO, 
                    format=f'%(asctime)s %(levelname)s %(name)s : %(message)s')

handler = RotatingFileHandler('loren.log', maxBytes=10000, backupCount=3)
logger = logging.getLogger('root')
app.logger.setLevel(logging.INFO)
app.logger.addHandler(handler)


login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'  
login_manager.session_protection = "strong"
login_manager.init_app(app)

jwt.init_app(app)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPOLAD_DIRECTORY = os.path.join(APP_ROOT, "static/uploads/")
AVATAR_UPOLAD_DIRECTORY = os.path.join(UPOLAD_DIRECTORY, "avatars/")
if not os.path.isdir(AVATAR_UPOLAD_DIRECTORY):
    os.mkdir(AVATAR_UPOLAD_DIRECTORY)


with app.app_context():
    db.create_all()

from chat_app.auth.views.auth_views import auth_views_module
from chat_app.site.views.site_index_views import site_index_views_module
from chat_app.site.views.site_chat_views import site_chat_views_module
from chat_app.errors.views.hanldes import errors_handle_module


app.register_blueprint(auth_views_module)
app.register_blueprint(site_index_views_module)
app.register_blueprint(site_chat_views_module)
app.register_blueprint(errors_handle_module)




