from flask_wtf import FlaskForm
import wtforms as wtf
from wtforms import validators as val

from . import router, docker_api
from .models import Route

PORT_MIN = 1
PORT_MAX = 65535


_route_port_validators = [
    val.InputRequired(),
    val.NumberRange(min=PORT_MIN, max=PORT_MAX, message='Invalid port'),
]


class RouteForm(FlaskForm):
    source = wtf.StringField('Hostname', [val.InputRequired()])
    path = wtf.StringField('Path', [val.Optional()])
    target = wtf.SelectField('Service', [val.InputRequired()])
    port = wtf.IntegerField('Port',
                            validators=_route_port_validators,
                            default=Route.DEFAULT_PORT)

    def validate(self, extra_validators=None):
        super().validate(extra_validators)
        if self.path.data:
            source = f'{self.source.data}:{self.path.data}'
        else:
            source = self.source.data
        
        route = router.lookup(source, silent=True)
        if route is not None:
            raise val.ValidationError(f'Route "{field.data}" already exists')
    # def validate_source(self, field):
    #     route = router.lookup(field.data, silent=True)
    #     if route is not None:
    #         raise val.ValidationError(f'Route "{field.data}" already exists')

    def validate_target(self, field):
        if not docker_api.has_service(field.data):
            raise val.ValidationError('Service does not exist')


class LoginForm(FlaskForm):
    username = wtf.StringField('Username', [val.InputRequired()])
    password = wtf.PasswordField('Password', [val.InputRequired()])


class UserAddForm(FlaskForm):
    username = wtf.StringField('Username', [val.InputRequired()])
    password = wtf.PasswordField('Password', [
        val.InputRequired(),
        val.EqualTo('confirm', message='Password and Confirmation must match'),
    ])
    confirm = wtf.PasswordField('Confirm Password', [val.InputRequired()])


class UserEditForm(FlaskForm):
    password = wtf.PasswordField('New Password', [
        val.InputRequired(),
        val.EqualTo('confirm', message='Password and Confirmation must match'),
    ])
    confirm = wtf.PasswordField('Confirm Password', [val.InputRequired()])
