"""Add auth fields to users

Revision ID: 20251231_220951
Revises: 
Create Date: 2025-12-31 22:09:51.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20251231_220951'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum type for user role
    op.execute("CREATE TYPE userrole AS ENUM ('client', 'expert', 'admin')")
    
    # Add phone column (nullable)
    op.add_column('users', sa.Column('phone', sa.String(length=20), nullable=True))
    
    # Add password column (nullable initially to handle existing users)
    op.add_column('users', sa.Column('password', sa.String(length=255), nullable=True))
    
    # Add role column with default
    op.add_column('users', sa.Column('role', postgresql.ENUM('client', 'expert', 'admin', name='userrole', create_type=False), server_default='client', nullable=False))
    
    # Handle existing users: set a placeholder password (users will need to reset)
    # If no existing users, this will just set the constraint
    op.execute("""
        UPDATE users 
        SET password = '$2b$12$PLACEHOLDER_PASSWORD_RESET_REQUIRED' 
        WHERE password IS NULL
    """)
    
    # Now make password NOT NULL
    op.alter_column('users', 'password', nullable=False)


def downgrade() -> None:
    # Remove columns
    op.drop_column('users', 'role')
    op.drop_column('users', 'password')
    op.drop_column('users', 'phone')
    
    # Drop enum type
    op.execute('DROP TYPE IF EXISTS userrole')

