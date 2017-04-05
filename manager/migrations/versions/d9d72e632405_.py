"""create users table and insert first user

Revision ID: d9d72e632405
Revises: 
Create Date: 2017-04-05 13:42:02.901715

"""
from alembic import op
import sqlalchemy as sa
import bcrypt


# revision identifiers, used by Alembic.
revision = 'd9d72e632405'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    users_table = op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=True),
        sa.Column('password', sa.String(length=200), nullable=True),
        sa.Column('name', sa.String(length=80), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    op.bulk_insert(users_table, [
        {
            'email': 'admin@example.com',
            'password': bcrypt.hashpw(b'change_me', bcrypt.gensalt()).decode('utf-8'),
            'name': 'Admin',
        }
    ])


def downgrade():
    op.drop_table('user')
