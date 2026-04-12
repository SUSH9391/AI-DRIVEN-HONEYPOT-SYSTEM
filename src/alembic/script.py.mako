"""${message}

Revision ID: ${repr(revision)}
Revises: ${repr(parent_revision)}
Create Date: ${repr(create_date)}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = '${revision}'
down_revision = '${down_revision}'
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrade_ops}


def downgrade() -> None:
    ${downgrade_ops}

