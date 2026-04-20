"""sandbox_models

Revision ID: 003
Revises: 002
Create Date: 2026-04-20 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add new fields to users
    op.add_column('users', sa.Column('supabase_uid', sa.String(), nullable=True))
    op.add_column('users', sa.Column('username', sa.String(), nullable=True))
    op.add_column('users', sa.Column('total_xp', sa.Integer(), server_default='0', nullable=False))
    op.add_column('users', sa.Column('level', sa.Integer(), server_default='1', nullable=False))
    # Drop old unused columns
    op.drop_constraint('users_email_key', 'users', type_='unique')
    op.drop_column('users', 'email')
    op.drop_column('users', 'role')
    
    # Create sandbox_sessions table
    op.create_table('sandbox_sessions',
    sa.Column('id', postgresql.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('user_id', postgresql.UUID(), nullable=False),
    sa.Column('env_type', sa.String(), nullable=False),
    sa.Column('theme_template', sa.String(), nullable=False),
    sa.Column('difficulty_level', sa.Integer(), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('attacks_detected', sa.Integer(), nullable=False),
    sa.Column('xp_earned', sa.Integer(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Create badges table
    op.create_table('badges',
    sa.Column('id', postgresql.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('user_id', postgresql.UUID(), nullable=False),
    sa.Column('badge_type', sa.String(), nullable=False),
    sa.Column('earned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('sandbox_id', postgresql.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['sandbox_id'], ['sandbox_sessions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    pass
