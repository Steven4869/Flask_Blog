"""Added about author info

Revision ID: 1988082fd2f3
Revises: bc8250af2156
Create Date: 2022-05-21 10:49:52.861646

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1988082fd2f3'
down_revision = 'bc8250af2156'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('about_author', sa.Text(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'about_author')
    # ### end Alembic commands ###
