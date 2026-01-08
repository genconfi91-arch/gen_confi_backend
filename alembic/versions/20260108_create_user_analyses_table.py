"""create user_analyses table

Revision ID: 20260108_create_user_analyses
Revises: 20251231_220951_add_auth_fields_to_users
Create Date: 2026-01-08 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260108_create_user_analyses'
down_revision = '20251231_220951_add_auth_fields_to_users'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_analyses table
    op.create_table(
        'user_analyses',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('image_path', sa.String(length=500), nullable=False),
        sa.Column('chat_answers', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('face_analysis', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('style_recommendations', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('personalized_insights', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    )
    op.create_index(op.f('ix_user_analyses_id'), 'user_analyses', ['id'], unique=False)
    op.create_index(op.f('ix_user_analyses_user_id'), 'user_analyses', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_user_analyses_user_id'), table_name='user_analyses')
    op.drop_index(op.f('ix_user_analyses_id'), table_name='user_analyses')
    # Drop table
    op.drop_table('user_analyses')

