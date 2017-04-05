from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField
from wtforms.validators import InputRequired, ValidationError

from . import ceryx_api, docker_api


class RouteForm(FlaskForm):
    source = StringField('Hostname', [InputRequired()])
    target = SelectField('Service', [InputRequired()])

    def validate_source(self, field):
        if ceryx_api.has_route(field.data):
            raise ValidationError('Route "{}" already exists'.format(field.data))

    def validate_target(self, field):
        if not docker_api.has_service(field.data):
            raise ValidationError('Service does not exist')


class LoginForm(FlaskForm):
    email = StringField('Email', [InputRequired()])
    password = PasswordField('Password', [InputRequired()])