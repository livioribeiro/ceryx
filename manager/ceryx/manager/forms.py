from flask_wtf import FlaskForm
import wtforms as wtf
from wtforms import validators as val

from . import ceryx_api, docker_api


class RouteForm(FlaskForm):
    source = wtf.StringField('Hostname', [val.InputRequired()])
    target = wtf.SelectField('Service', [val.InputRequired()])

    def validate_source(self, field):
        if ceryx_api.has_route(field.data):
            raise val.ValidationError('Route "{}" already exists'.format(field.data))

    def validate_target(self, field):
        if not docker_api.has_service(field.data):
            raise val.ValidationError('Service does not exist')


class LoginForm(FlaskForm):
    email = wtf.StringField('Email', [val.InputRequired()])
    password = wtf.PasswordField('Password', [val.InputRequired()])


class UserAddForm(FlaskForm):
    name = wtf.StringField('Name', [val.InputRequired()])
    email = wtf.StringField('Email', [
        val.InputRequired(),
        val.Email(),
    ])
    password = wtf.PasswordField('Password', [
        val.InputRequired(),
        val.EqualTo('confirm', message='Password and Confirmation must match'),
    ])
    confirm = wtf.PasswordField('Confirm Password', [val.InputRequired()])


class UserEditForm(FlaskForm):
    name = wtf.StringField('Name', [val.Optional()])
    email = wtf.StringField('Email', [
        val.Optional(),
        val.Email(),
    ])
    password = wtf.PasswordField('Password', [
        val.Optional(),
        val.EqualTo('confirm', message='Password and Confirmation must match'),
    ])
    confirm = wtf.PasswordField('Confirm Password', [val.Optional()])