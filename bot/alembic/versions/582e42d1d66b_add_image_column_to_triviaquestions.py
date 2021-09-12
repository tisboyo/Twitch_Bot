"""Add image column to TriviaQuestions

Revision ID: 582e42d1d66b
Revises: e44461c52ba4
Create Date: 2021-09-05 02:08:27.308744

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "582e42d1d66b"
down_revision = "e44461c52ba4"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("trivia_questions", sa.Column("image", sa.String(length=32), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("trivia_questions", "image")
    # ### end Alembic commands ###
