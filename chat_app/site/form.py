from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextAreaField,IntegerField
from wtforms.validators import DataRequired

class room_Form(FlaskForm):
    user_id2 = IntegerField('user_id2',validators=[DataRequired()])
class delete_room_Form(FlaskForm):
    room_id = IntegerField('room_id',validators=[DataRequired()])
class add_user_to_room_Form(FlaskForm):
    user_id = IntegerField('user_id',validators=[DataRequired()])
    room_id = IntegerField('room_id',validators=[DataRequired()])
class block_user_Form(FlaskForm):
    blocked_id = IntegerField('blocked_id',validators=[DataRequired()])
class send_message_Form(FlaskForm):
    room_id = IntegerField('room_id',validators=[DataRequired()])
    content = TextAreaField('Content',validators=[DataRequired()])
    
