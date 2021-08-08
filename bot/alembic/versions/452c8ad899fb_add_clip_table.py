"""Add clip table

Revision ID: 452c8ad899fb
Revises: cef784ac0fd1
Create Date: 2021-08-08 23:20:09.526773

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "452c8ad899fb"
down_revision = "cef784ac0fd1"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "clips",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=1024), nullable=True),
        sa.Column("url", sa.String(length=256), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("clips")
    # ### end Alembic commands ###
