"""add_payment_gateway_integration

Revision ID: 1a2b3c4d5e6f
Revises: 0c4052a95382
Create Date: 2026-09-28 10:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

revision: str = '1a2b3c4d5e6f'
down_revision: Union[str, Sequence[str], None] = '0c4052a95382'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    existing_tables = inspector.get_table_names()
    
    # 1. Extend payments table using batch_alter_table (safe for SQLite and MySQL)
    if 'payments' in existing_tables:
        existing_cols = [c['name'] for c in inspector.get_columns('payments')]
        with op.batch_alter_table('payments', schema=None) as batch_op:
            if 'currency' not in existing_cols:
                batch_op.add_column(sa.Column('currency', sa.String(length=10), server_default='INR', nullable=False))
            if 'status' not in existing_cols:
                batch_op.add_column(sa.Column('status', sa.String(length=30), server_default='SUCCESS', nullable=False))
                batch_op.create_index(batch_op.f('ix_payments_status'), ['status'], unique=False)
            if 'provider' not in existing_cols:
                batch_op.add_column(sa.Column('provider', sa.String(length=50), server_default='manual', nullable=False))
                batch_op.create_index(batch_op.f('ix_payments_provider'), ['provider'], unique=False)
            if 'provider_order_id' not in existing_cols:
                batch_op.add_column(sa.Column('provider_order_id', sa.String(length=100), nullable=True))
                batch_op.create_index(batch_op.f('ix_payments_provider_order_id'), ['provider_order_id'], unique=False)
            if 'provider_payment_id' not in existing_cols:
                batch_op.add_column(sa.Column('provider_payment_id', sa.String(length=100), nullable=True))
                batch_op.create_index(batch_op.f('ix_payments_provider_payment_id'), ['provider_payment_id'], unique=False)
            if 'provider_signature' not in existing_cols:
                batch_op.add_column(sa.Column('provider_signature', sa.String(length=255), nullable=True))
            if 'idempotency_key' not in existing_cols:
                batch_op.add_column(sa.Column('idempotency_key', sa.String(length=100), nullable=True))
                batch_op.create_index(batch_op.f('ix_payments_idempotency_key'), ['idempotency_key'], unique=True)
            if 'failure_reason' not in existing_cols:
                batch_op.add_column(sa.Column('failure_reason', sa.Text(), nullable=True))
            if 'paid_at' not in existing_cols:
                batch_op.add_column(sa.Column('paid_at', sa.DateTime(), nullable=True))
            if 'updated_at' not in existing_cols:
                batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))

    # 2. Create payment_webhook_events
    if 'payment_webhook_events' not in existing_tables:
        op.create_table(
            'payment_webhook_events',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('provider', sa.String(length=50), nullable=False),
            sa.Column('event_id', sa.String(length=100), nullable=False),
            sa.Column('event_type', sa.String(length=100), nullable=False),
            sa.Column('status', sa.String(length=30), server_default='processed', nullable=False),
            sa.Column('payload', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_payment_webhook_events_id'), 'payment_webhook_events', ['id'], unique=False)
        op.create_index(op.f('ix_payment_webhook_events_provider'), 'payment_webhook_events', ['provider'], unique=False)
        op.create_index(op.f('ix_payment_webhook_events_event_id'), 'payment_webhook_events', ['event_id'], unique=True)
        op.create_index(op.f('ix_payment_webhook_events_event_type'), 'payment_webhook_events', ['event_type'], unique=False)

    # 3. Create payment_refunds
    if 'payment_refunds' not in existing_tables:
        op.create_table(
            'payment_refunds',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('payment_id', sa.Integer(), nullable=False),
            sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column('currency', sa.String(length=10), server_default='INR', nullable=False),
            sa.Column('provider_refund_id', sa.String(length=100), nullable=True),
            sa.Column('reason', sa.Text(), nullable=True),
            sa.Column('status', sa.String(length=30), server_default='SUCCESS', nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('initiated_by_user_id', sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(['initiated_by_user_id'], ['users.id'], ondelete='SET NULL'),
            sa.ForeignKeyConstraint(['payment_id'], ['payments.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_payment_refunds_id'), 'payment_refunds', ['id'], unique=False)
        op.create_index(op.f('ix_payment_refunds_payment_id'), 'payment_refunds', ['payment_id'], unique=False)
        op.create_index(op.f('ix_payment_refunds_provider_refund_id'), 'payment_refunds', ['provider_refund_id'], unique=False)

def downgrade() -> None:
    op.drop_table('payment_refunds')
    op.drop_table('payment_webhook_events')
    with op.batch_alter_table('payments', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_payments_idempotency_key'))
        batch_op.drop_column('updated_at')
        batch_op.drop_column('paid_at')
        batch_op.drop_column('failure_reason')
        batch_op.drop_column('idempotency_key')
        batch_op.drop_column('provider_signature')
        batch_op.drop_column('provider_payment_id')
        batch_op.drop_column('provider_order_id')
        batch_op.drop_column('provider')
        batch_op.drop_column('status')
        batch_op.drop_column('currency')
