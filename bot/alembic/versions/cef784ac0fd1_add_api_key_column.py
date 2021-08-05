"""Add api_key column

Revision ID: cef784ac0fd1
Revises: 7e445071ceea
Create Date: 2021-08-05 00:49:21.765654

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "cef784ac0fd1"
down_revision = "7e445071ceea"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("web_auth", sa.Column("api_key", sa.String(length=32), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("web_auth", "api_key")
    # ### end Alembic commands ###
