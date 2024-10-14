"""Add webauth table

Revision ID: bddf52d4e7df
Revises: b21121e9831b
Create Date: 2021-07-25 22:40:03.107459

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "bddf52d4e7df"
down_revision = "b21121e9831b"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "web_auth",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_web_auth_id"), "web_auth", ["id"], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_web_auth_id"), table_name="web_auth")
    op.drop_table("web_auth")
    # ### end Alembic commands ###
