"""empty message

Revision ID: 0d1902c2b67b
Revises: e2c453017b11
Create Date: 2020-01-21 02:14:56.933777

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0d1902c2b67b'
down_revision = 'e2c453017b11'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Artist', 'genres',
               existing_type=sa.ARRAY(sa.String()),
               type_=sa.VARCHAR(length=120),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Artist', 'genres',
               existing_type=sa.ARRAY(sa.String()),
               type_=sa.VARCHAR(length=120),
               existing_nullable=True)
    # ### end Alembic commands ###
