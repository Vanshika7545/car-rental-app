from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, FloatField, SelectField, HiddenField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange, Optional
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered. Please use a different one.')

class CarForm(FlaskForm):
    brand = StringField('Brand', validators=[DataRequired(), Length(max=100)])
    year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=1900, max=2100)])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Add Car')

class CarModelForm(FlaskForm):
    car_id = SelectField('Car', coerce=int, validators=[DataRequired()])
    name = StringField('Model Name', validators=[DataRequired(), Length(max=100)])
    price_per_day = FloatField('Price Per Day', validators=[DataRequired(), NumberRange(min=0)])
    mileage = FloatField('Mileage', validators=[Optional()])
    fuel_type = SelectField('Fuel Type', choices=[
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
        ('Electric', 'Electric'),
        ('Hybrid', 'Hybrid')
    ])
    transmission = SelectField('Transmission', choices=[
        ('Manual', 'Manual'),
        ('Automatic', 'Automatic')
    ])
    seats = IntegerField('Number of Seats', validators=[Optional(), NumberRange(min=1, max=10)])
    air_conditioning = BooleanField('Air Conditioning')
    image_url = StringField('Image URL', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Add Car Model')

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[Optional()])
    submit = SubmitField('Search')

class RentalForm(FlaskForm):
    car_model_id = HiddenField('Car Model ID', validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    submit = SubmitField('Rent Now')
    
    def validate_end_date(self, end_date):
        if self.start_date.data and end_date.data:
            if end_date.data < self.start_date.data:
                raise ValidationError('End date must be after start date.')
