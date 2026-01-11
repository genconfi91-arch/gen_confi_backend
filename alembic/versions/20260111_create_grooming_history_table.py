"""create grooming_history table

Revision ID: 20260111_create_grooming_history
Revises: 20260111_create_user_features
Create Date: 2026-01-11 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260111_create_grooming_history'
down_revision = '20260111_create_user_features'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create grooming_history table
    op.create_table(
        'grooming_history',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('analysis_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('before_image_url', sa.String(length=10000), nullable=True),
        sa.Column('after_image_url', sa.String(length=10000), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Create indexes
    op.create_index(op.f('ix_grooming_history_id'), 'grooming_history', ['id'], unique=False)
    op.create_index(op.f('ix_grooming_history_user_id'), 'grooming_history', ['user_id'], unique=False)
    op.create_index(op.f('ix_grooming_history_created_at'), 'grooming_history', ['created_at'], unique=False)
    op.create_index('ix_grooming_history_user_created', 'grooming_history', ['user_id', 'created_at'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_grooming_history_user_created', table_name='grooming_history')
    op.drop_index(op.f('ix_grooming_history_created_at'), table_name='grooming_history')
    op.drop_index(op.f('ix_grooming_history_user_id'), table_name='grooming_history')
    op.drop_index(op.f('ix_grooming_history_id'), table_name='grooming_history')
    # Drop table
    op.drop_table('grooming_history')

