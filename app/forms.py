from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, SelectField, BooleanField, validators, DateField, FileField
from wtforms.validators import InputRequired, EqualTo, Optional, Length, Email, ValidationError
from app import db

# Define login and registration forms (for flask-login)

class RegisterForm(FlaskForm):
    name = TextField(validators=[InputRequired(), Length(max=50, message='Limited to 50 letters')])
    password = PasswordField(validators=[InputRequired(), Length(min=4, message='Passowrd too short')])
    email = TextField(validators=[InputRequired()])
    gender = SelectField( choices=[('0', 'Female'), ('1', 'Male'), ('2', 'Other')])
    interested_in = SelectField( choices=[('0', 'Female'), ('1', 'Male'), ('2', 'Other')])
    birthdate = DateField(format='%Y-%m-%d')
    location = SelectField( choices=[('(41.8781,87.6298)', 'Chicago'), ('(40.1164,88.2434)', 'Champaign'), ('(39.7817,89.6501)', 'Springfield')])
    zipcode = TextField(validators=[InputRequired()])
    file = FileField()

    def validate_email(self, field):
        sql = "SELECT COUNT(*) FROM public.users WHERE email='{}'".format(self.email.data)
        result = db.engine.execute(sql).fetchone()
        if result[0] != 0:
            raise ValidationError('This Email is taken')

class ProfileForm(FlaskForm):
    name = TextField()
    password = PasswordField()
    email = TextField()
    gender = SelectField( choices=[('0', 'Female'), ('1', 'Male'), ('2', 'Other')])
    interested_in = SelectField( choices=[('0', 'Female'), ('1', 'Male'), ('2', 'Other')])
    birthdate = DateField(format='%Y-%m-%d')
    location = SelectField( choices=[('(41.8781,87.6298)', 'Chicago'), ('(40.1164,88.2434)', 'Champaign'), ('(39.7817,89.6501)', 'Springfield')])
    