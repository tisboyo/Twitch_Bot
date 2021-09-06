"""Add priority column to TriviaQuestions

Revision ID: 8527dda7e7d7
Revises: 582e42d1d66b
Create Date: 2021-09-06 01:45:06.649226

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "8527dda7e7d7"
down_revision = "582e42d1d66b"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("trivia_questions", sa.Column("priority", sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("trivia_questions", "priority")
    # ### end Alembic commands ###
