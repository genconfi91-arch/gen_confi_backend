"""create user_features table

Revision ID: 20260111_create_user_features
Revises: 20260108_create_user_analyses
Create Date: 2026-01-11 09:45:04.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260111_create_user_features'
down_revision = '20260108_create_user_analyses'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_features table
    op.create_table(
        'user_features',
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('gen_confi_user_id', sa.Integer(), nullable=True),
        sa.Column('gender', sa.String(length=10), nullable=False),
        sa.Column('face_shape', sa.String(length=50), nullable=True),
        sa.Column('face_length', sa.Float(), nullable=True),
        sa.Column('face_width', sa.Float(), nullable=True),
        sa.Column('forehead_width', sa.Float(), nullable=True),
        sa.Column('jaw_width', sa.Float(), nullable=True),
        sa.Column('chin_length', sa.Float(), nullable=True),
        sa.Column('skin_tone', sa.String(length=50), nullable=True),
        sa.Column('undertone', sa.String(length=50), nullable=True),
        sa.Column('ita_score', sa.Float(), nullable=True),
        sa.Column('hairline_type', sa.String(length=50), nullable=True),
        sa.Column('recession_level', sa.String(length=50), nullable=True),
        sa.Column('hair_texture', sa.String(length=50), nullable=True),
        sa.Column('beard_type', sa.String(length=50), nullable=True),
        sa.Column('beard_density', sa.String(length=50), nullable=True),
        sa.Column('eyebrow_shape', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('user_id'),
        sa.ForeignKeyConstraint(['gen_confi_user_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index(op.f('ix_user_features_user_id'), 'user_features', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_features_gen_confi_user_id'), 'user_features', ['gen_confi_user_id'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_user_features_gen_confi_user_id'), table_name='user_features')
    op.drop_index(op.f('ix_user_features_user_id'), table_name='user_features')
    # Drop table
    op.drop_table('user_features')

