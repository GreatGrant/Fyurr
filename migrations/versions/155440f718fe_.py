"""empty message

Revision ID: 155440f718fe
Revises: 92a157b3f828
Create Date: 2022-06-01 16:01:47.048698

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '155440f718fe'
down_revision = '92a157b3f828'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('genre', sa.ARRAY(sa.String()), nullable=False))
    op.add_column('venue', sa.Column('website_link', sa.String(), nullable=True))
    op.add_column('venue', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('venue', sa.Column('seeking_description', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venue', 'seeking_description')
    op.drop_column('venue', 'seeking_talent')
    op.drop_column('venue', 'website_link')
    op.drop_column('venue', 'genre')
    # ### end Alembic commands ###
