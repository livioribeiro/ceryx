from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import InputRequired, ValidationError

from . import CERYX, DOCKER


class RouteForm(FlaskForm):
    source = StringField('Hostname', [InputRequired()])
    target = SelectField('Service', [InputRequired()])

    def validate_source(self, field):
        if CERYX.has_route(field.data):
            raise ValidationError(f'Route "{field.data}" already exists')

    def validate_target(self, field):
        if not DOCKER.has_service(field.data):
            raise ValidationError('Service does not exist')
