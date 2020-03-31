from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Email


class QSForm(FlaskForm):
    first_name = StringField('FirstName*', validators=[DataRequired(message=u'FistName should not be NULL')])
    last_name = StringField('LastName*', validators=[DataRequired(message=u'LastName should not be NULL')])
    # email = StringField('Email', validators=[DataRequired(message=u'email address should not be NULL'), Length(1, 64),
    #                                          Email(message=u'Please input right email address, example：username@domain.com')])
    email = StringField('Email*', validators=[DataRequired(message=u'email address should not be NULL')])
    order_num = StringField('Order Id*', validators=[DataRequired(message=u'order_num should not be NULL')])
    score = StringField('Score', validators=[DataRequired(message=u'score should not be NULL, it should be 1-5')])
    submit = SubmitField('Send')