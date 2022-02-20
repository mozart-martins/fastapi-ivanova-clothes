"""Initial

Revision ID: 818d1c6930c4
Revises: 
Create Date: 2022-02-19 14:08:29.941019

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '818d1c6930c4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('clothes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=True),
    sa.Column('color', sa.Enum('pink', 'black', 'white', 'yellow', name='colorenum'), nullable=False),
    sa.Column('size', sa.Enum('xs', 's', 'm', 'l', 'xl', 'xxl', name='sizeenum'), nullable=False),
    sa.Column('photo_url', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('last_modified_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=True),
    sa.Column('full_name', sa.String(length=200), nullable=True),
    sa.Column('phone', sa.String(length=13), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('last_modified_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    op.drop_table('clothes')
    # ### end Alembic commands ###
