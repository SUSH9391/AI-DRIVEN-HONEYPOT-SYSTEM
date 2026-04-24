"""sandbox_models

Revision ID: 003_sandbox_models
Revises: 002_create_attack_logs
Create Date: 2026-04-20 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_sandbox_models'
down_revision = '002_create_attack_logs'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Step 1: Add gamification columns to users (keep email & role) ──
    op.add_column('users', sa.Column('username', sa.String(), nullable=True))
    op.add_column('users', sa.Column('supabase_uid', sa.String(), nullable=True))
    op.add_column('users', sa.Column('total_xp', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('level', sa.Integer(), nullable=False, server_default='1'))
    op.create_unique_constraint('uq_users_username', 'users', ['username'])
    op.create_unique_constraint('uq_users_supabase_uid', 'users', ['supabase_uid'])

    # ── Step 2: Create sandbox_sessions table ──
    op.create_table(
        'sandbox_sessions',
        sa.Column('id', postgresql.UUID(), nullable=False,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('env_type', sa.String(), nullable=False),
        sa.Column('theme_template', sa.String(), nullable=False),
        sa.Column('difficulty_level', sa.Integer(), nullable=False,
                  server_default='1'),
        sa.Column('session_token', sa.String(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('attacks_detected', sa.Integer(), nullable=False,
                  server_default='0'),
        sa.Column('xp_earned', sa.Integer(), nullable=False,
                  server_default='0'),
        sa.Column('active', sa.Boolean(), nullable=False,
                  server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )
    op.create_index('ix_sandbox_sessions_user_id',
                    'sandbox_sessions', ['user_id'])
    op.create_index('ix_sandbox_sessions_session_token',
                    'sandbox_sessions', ['session_token'], unique=True)
    op.create_index('ix_sandbox_sessions_active',
                    'sandbox_sessions', ['active'])

    # ── Step 3: Create badges table ──
    op.create_table(
        'badges',
        sa.Column('id', postgresql.UUID(), nullable=False,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('badge_type', sa.String(), nullable=False),
        sa.Column('earned_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('sandbox_id', postgresql.UUID(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['sandbox_id'], ['sandbox_sessions.id']),
    )
    op.create_index('ix_badges_user_id', 'badges', ['user_id'])
    op.create_unique_constraint(
        'uq_badges_user_badge', 'badges', ['user_id', 'badge_type']
    )

    # ── Step 4: Update attack_logs to link to sandbox_sessions ──
    op.add_column('attack_logs',
                  sa.Column('sandbox_id', postgresql.UUID(), nullable=True))
    op.add_column('attack_logs',
                  sa.Column('xp_earned', sa.Integer(), nullable=True))
    op.add_column('attack_logs',
                  sa.Column('user_id', postgresql.UUID(), nullable=True))
    op.create_foreign_key(
        'fk_attack_logs_sandbox_id',
        'attack_logs', 'sandbox_sessions',
        ['sandbox_id'], ['id']
    )
    op.create_foreign_key(
        'fk_attack_logs_user_id',
        'attack_logs', 'users',
        ['user_id'], ['id']
    )


def downgrade() -> None:
    # Reverse order of upgrade

    # Step 4 rollback
    op.drop_constraint('fk_attack_logs_user_id', 'attack_logs', type_='foreignkey')
    op.drop_constraint('fk_attack_logs_sandbox_id', 'attack_logs', type_='foreignkey')
    op.drop_column('attack_logs', 'user_id')
    op.drop_column('attack_logs', 'xp_earned')
    op.drop_column('attack_logs', 'sandbox_id')

    # Step 3 rollback
    op.drop_constraint('uq_badges_user_badge', 'badges', type_='unique')
    op.drop_index('ix_badges_user_id', table_name='badges')
    op.drop_table('badges')

    # Step 2 rollback
    op.drop_index('ix_sandbox_sessions_active', table_name='sandbox_sessions')
    op.drop_index('ix_sandbox_sessions_session_token', table_name='sandbox_sessions')
    op.drop_index('ix_sandbox_sessions_user_id', table_name='sandbox_sessions')
    op.drop_table('sandbox_sessions')

    # Step 1 rollback
    op.drop_constraint('uq_users_supabase_uid', 'users', type_='unique')
    op.drop_constraint('uq_users_username', 'users', type_='unique')
    op.drop_column('users', 'level')
    op.drop_column('users', 'total_xp')
    op.drop_column('users', 'supabase_uid')
    op.drop_column('users', 'username')
