from flask import Blueprint, render_template, redirect, url_for, session, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from password_validator import PasswordValidator
from functools import wraps

import movies.authentication.services as services
import movies.adapters.repository as repo

authentication_blueprint = Blueprint(
    'authentication_bp', __name__, url_prefix='/authentication')


@authentication_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    username_not_unique = None

    if form.validate_on_submit():
        try:
            services.add_user(form.username.data, form.password.data, repo.repo_instance)

            return redirect(url_for('authentication_bp.login'))
        except services.NameNotUniqueException:
            username_not_unique = 'Your username is already taken - please supply another'

    return render_template(
        'authentication/credentials.html',
        title='Register',
        form=form,
        username_error_message=username_not_unique,
        handler_url=url_for('authentication_bp.register'),
    )


@authentication_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    username_not_recognised = None
    password_does_not_match_username = None

    if form.validate_on_submit():
        try:
            user = services.get_user(form.username.data, repo.repo_instance)

            services.authenticate_user(user['username'], form.password.data, repo.repo_instance)

            session.clear()
            session['username'] = user['username']
            return redirect(url_for('home_bp.home'))


        except services.UnknownUserException:
            username_not_recognised = 'Username not recognised - please supply another'

        except services.AuthenticationException:
            password_does_not_match_username = 'Password does not match supplied username - please check and try again'

    return render_template(
        'authentication/credentials.html',
        title='Login',
        username_error_message=username_not_recognised,
        password_error_message=password_does_not_match_username,
        form=form,
    )


@authentication_blueprint.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home_bp.home'))


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'username' not in session:
            return redirect(url_for('authentication_bp.login'))
        return view(**kwargs)
    return wrapped_view


class PasswordValid:
    def __init__(self, message=None):
        if not message:
            message = u'Your password must at least 8 characters, and contain an upper case letter, a lower case letter and a number'
        self.message = message

    def __call__(self, form, field):
        schema = PasswordValidator()
        schema \
            .min(8) \
            .has().uppercase() \
            .has().lowercase() \
            .has().digits()
        if not schema.validate(field.data):
            raise ValidationError(self.message)


class RegistrationForm(FlaskForm):
    username = StringField('Username', [
        DataRequired(message='Your username is required'),
        Length(min=3, message='Your username is too short')])
    password = PasswordField('Password', [
        DataRequired(message='Your password is required'),
        PasswordValid()])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username', [
        DataRequired()])
    password = PasswordField('Password', [
        DataRequired()])
    submit = SubmitField('Login')
