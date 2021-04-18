"""Add enabled column to trivia

Revision ID: 6c0b348d98ac
Revises: 81c034a85150
Create Date: 2021-04-18 20:16:42.779934

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "6c0b348d98ac"
down_revision = "81c034a85150"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("trivia_questions", sa.Column("enabled", sa.Boolean(), nullable=True))
    # Insert the default value
    op.execute("UPDATE trivia_questions SET enabled = TRUE")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("trivia_questions", "enabled")
    # ### end Alembic commands ###
