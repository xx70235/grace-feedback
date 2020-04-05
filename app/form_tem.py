from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Email


class QSForm(FlaskForm):
    first_name = StringField('FirstName*', validators=[DataRequired(message=u'FistName should not be NULL')])
    last_name = StringField('LastName*', validators=[DataRequired(message=u'LastName should not be NULL')])
    email = StringField('Email*', validators=[DataRequired(message=u'email address should not be NULL')])
    order_num = StringField('Order Id*', validators=[DataRequired(message=u'order_num should not be NULL')])
    score = StringField('Score', validators=[DataRequired(message=u'score should not be NULL, it should be 1-5')])
    submit = SubmitField('Send')


class ConfigForm(FlaskForm):
    account = StringField("account")
    email = StringField("email")
    contact_url = StringField("contact_url")
    password = StringField("password")
    submit = SubmitField("Send")