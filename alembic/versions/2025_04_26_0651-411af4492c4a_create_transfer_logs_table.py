"""create_transfer_logs_table

Revision ID: 411af4492c4a
Revises: 73a4e9aff6e7
Create Date: 2025-04-26 06:51:28.167793

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '411af4492c4a'
down_revision: Union[str, None] = '73a4e9aff6e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Cria a extensão uuid-ossp se necessário (para PostgreSQL < 13)
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    op.create_table('transfer_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), 
                 server_default=sa.text('gen_random_uuid()'), 
                 primary_key=True, index=True,
                 comment='Unique identifier for the transfer'),
        sa.Column('record_id', postgresql.UUID(as_uuid=True), 
                 nullable=False, index=True,
                 comment='ID of the medical record being transferred'),
        sa.Column('source_org_id', postgresql.UUID(as_uuid=True), 
                 nullable=False,
                 comment='Source healthcare organization ID'),
        sa.Column('destination_org_id', postgresql.UUID(as_uuid=True), 
                 nullable=False,
                 comment='Destination healthcare organization ID'),
        sa.Column('status', sa.Enum('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 
                                  name='transferstatus'),
                 nullable=False, 
                 server_default='PENDING',
                 comment='Current status of the transfer'),
        sa.Column('created_at', sa.DateTime(timezone=True), 
                 server_default=sa.text('now()'), 
                 nullable=False,
                 comment='Timestamp when transfer was initiated'),
        sa.Column('updated_at', sa.DateTime(timezone=True), 
                 server_default=sa.text('now()'), 
                 nullable=False,
                 comment='Timestamp when transfer was last updated'),
        sa.Column('completed_at', sa.DateTime(timezone=True), 
                 nullable=True,
                 comment='Timestamp when transfer was completed'),
        sa.Column('parameters', postgresql.JSONB, 
                 nullable=False, 
                 server_default=sa.text("'{}'::jsonb"),
                 comment='Configuration parameters for the transfer'),
        sa.Column('error_details', postgresql.JSONB, 
                 nullable=True,
                 comment='Error details if transfer failed'),
        sa.Column('audit_log', postgresql.JSONB, 
                 nullable=True,
                 comment='Complete audit trail for compliance'),
        comment='Audit log for medical record transfers between organizations'
    )


def downgrade():
    op.drop_table('transfer_logs')
    op.execute('DROP TYPE IF EXISTS transferstatus')