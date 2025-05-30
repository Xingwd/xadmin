"""initialize models

Revision ID: 638939984ef6
Revises: 
Create Date: 2025-03-21 15:21:24.864299

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '638939984ef6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('operationlog',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('username', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('request_method', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('request_path', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('request_query_params', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('response_status_code', sa.Integer(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_operationlog_created_at'), 'operationlog', ['created_at'], unique=False)
    op.create_index(op.f('ix_operationlog_title'), 'operationlog', ['title'], unique=False)
    op.create_index(op.f('ix_operationlog_user_id'), 'operationlog', ['user_id'], unique=False)
    op.create_index(op.f('ix_operationlog_username'), 'operationlog', ['username'], unique=False)
    op.create_table('role',
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_role_name'), 'role', ['name'], unique=True)
    op.create_table('rule',
    sa.Column('type', sa.Enum('menu_dir', 'menu_item', 'permission', name='ruletype'), nullable=False),
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('path', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('icon', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('menu_item_type', sa.Enum('tab', 'link', 'iframe', name='menuitemtype'), nullable=True),
    sa.Column('url', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('component', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('remark', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('cache', sa.Boolean(), nullable=False),
    sa.Column('weight', sa.Integer(), nullable=False),
    sa.Column('status', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['rule.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_rule_title'), 'rule', ['title'], unique=False)
    op.create_table('user',
    sa.Column('username', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('full_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('source', sa.Enum('system', 'signup', name='usersource'), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('hashed_password', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('last_login_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_full_name'), 'user', ['full_name'], unique=False)
    op.create_index(op.f('ix_user_is_active'), 'user', ['is_active'], unique=False)
    op.create_index(op.f('ix_user_is_superuser'), 'user', ['is_superuser'], unique=False)
    op.create_index(op.f('ix_user_last_login_at'), 'user', ['last_login_at'], unique=False)
    op.create_table('rolerulelink',
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('rule_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.ForeignKeyConstraint(['rule_id'], ['rule.id'], ),
    sa.PrimaryKeyConstraint('role_id', 'rule_id')
    )
    op.create_table('userrolelink',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'role_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('userrolelink')
    op.drop_table('rolerulelink')
    op.drop_index(op.f('ix_user_last_login_at'), table_name='user')
    op.drop_index(op.f('ix_user_is_superuser'), table_name='user')
    op.drop_index(op.f('ix_user_is_active'), table_name='user')
    op.drop_index(op.f('ix_user_full_name'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_rule_title'), table_name='rule')
    op.drop_table('rule')
    op.drop_index(op.f('ix_role_name'), table_name='role')
    op.drop_table('role')
    op.drop_index(op.f('ix_operationlog_username'), table_name='operationlog')
    op.drop_index(op.f('ix_operationlog_user_id'), table_name='operationlog')
    op.drop_index(op.f('ix_operationlog_title'), table_name='operationlog')
    op.drop_index(op.f('ix_operationlog_created_at'), table_name='operationlog')
    op.drop_table('operationlog')
    # ### end Alembic commands ###
