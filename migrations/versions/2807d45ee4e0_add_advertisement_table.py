"""Add Advertisement table

Revision ID: 2807d45ee4e0
Revises: 
Create Date: 2016-07-12 16:55:41.856871

"""

# revision identifiers, used by Alembic.
revision = '2807d45ee4e0'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('auto_advertisement',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('brand', sa.String(), nullable=True),
    sa.Column('model', sa.String(), nullable=True),
    sa.Column('complectation', sa.String(), nullable=True),
    sa.Column('is_new', sa.Boolean(), nullable=True),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('auto_advertisement')
    ### end Alembic commands ###
