"""empty message

Revision ID: e46b0d3d15f7
Revises: 289e9f10c241
Create Date: 2022-01-11 13:35:37.557857

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e46b0d3d15f7'
down_revision = '289e9f10c241'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('test')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('test',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=40), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='test_pkey')
    )
    # ### end Alembic commands ###
