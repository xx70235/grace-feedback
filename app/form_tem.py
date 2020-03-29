from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class QSForm(FlaskForm):
    first_name = StringField('FirstName', validators=[DataRequired()])
    last_name = StringField('LastName', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    order_num = StringField('OrderNum', validators=[DataRequired()])
    score = StringField('Score', validators=[DataRequired()])
    submit = SubmitField('Send')