"""Add TriviaResults table

Revision ID: 81c034a85150
Revises: 8afcb0f7aad7
Create Date: 2021-04-09 00:02:50.832576

"""
import sqlalchemy as sa
from alembic import op

# from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "81c034a85150"
down_revision = "8afcb0f7aad7"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "trivia_results",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("channel", sa.Integer(), nullable=False),
        sa.Column("total_wins", sa.Integer(), nullable=False),
        sa.Column("trivia_points", sa.Integer(), nullable=False),
        sa.Column("questions_answered_correctly", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel"],
            ["users.channel"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
        ),
        sa.PrimaryKeyConstraint("user_id", "channel"),
    )
    op.create_index(op.f("ix_trivia_results_channel"), "trivia_results", ["channel"], unique=False)
    op.create_index(op.f("ix_trivia_results_user_id"), "trivia_results", ["user_id"], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("trivia_results")
    # Indexes are automagically removed when the table is dropped.
    # op.drop_index(op.f("ix_trivia_results_user_id"), table_name="trivia_results")
    # op.drop_index(op.f("ix_trivia_results_channel"), table_name="trivia_results")

    # ### end Alembic commands ###
