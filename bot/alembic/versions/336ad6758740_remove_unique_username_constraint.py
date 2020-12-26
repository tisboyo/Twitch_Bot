"""Remove unique username constraint

Revision ID: 336ad6758740
Revises: 6a59c8ba5242
Create Date: 2020-12-26 13:33:28.446674

"""
# import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "336ad6758740"
down_revision = "6a59c8ba5242"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("user", table_name="users")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index("user", "users", ["user"], unique=True)
    # ### end Alembic commands ###