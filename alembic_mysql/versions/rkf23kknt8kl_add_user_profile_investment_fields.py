"""add user_profile investment fields

Revision ID: rkf23kknt8kl
Revises: f84b02321df9
Create Date: 2026-04-21

추가 컬럼: investment_style, risk_tolerance, preferred_sectors,
           analysis_preference, keywords_of_interest
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'rkf23kknt8kl'
down_revision: Union[str, None] = 'f84b02321df9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # String 컬럼은 server_default='' 사용 가능
    op.add_column('user_profiles',
        sa.Column('investment_style', sa.String(length=20), nullable=False, server_default=''))
    op.add_column('user_profiles',
        sa.Column('risk_tolerance', sa.String(length=20), nullable=False, server_default=''))
    op.add_column('user_profiles',
        sa.Column('analysis_preference', sa.String(length=20), nullable=False, server_default=''))

    # TEXT 컬럼은 MySQL에서 server_default 리터럴 불가 → nullable=True로 추가 후 UPDATE → NOT NULL 변경
    op.add_column('user_profiles',
        sa.Column('preferred_sectors', sa.Text(), nullable=True))
    op.add_column('user_profiles',
        sa.Column('keywords_of_interest', sa.Text(), nullable=True))

    op.execute("UPDATE user_profiles SET preferred_sectors = '' WHERE preferred_sectors IS NULL")
    op.execute("UPDATE user_profiles SET keywords_of_interest = '' WHERE keywords_of_interest IS NULL")

    op.alter_column('user_profiles', 'preferred_sectors',
        existing_type=sa.Text(), nullable=False)
    op.alter_column('user_profiles', 'keywords_of_interest',
        existing_type=sa.Text(), nullable=False)


def downgrade() -> None:
    op.drop_column('user_profiles', 'keywords_of_interest')
    op.drop_column('user_profiles', 'analysis_preference')
    op.drop_column('user_profiles', 'preferred_sectors')
    op.drop_column('user_profiles', 'risk_tolerance')
    op.drop_column('user_profiles', 'investment_style')
