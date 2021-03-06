"""Make user name non-unique

Revision ID: adde2f8bdd4e
Revises: 8bd30e288c20
Create Date: 2020-12-20 06:09:37.580898

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "adde2f8bdd4e"
down_revision = "8bd30e288c20"
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
