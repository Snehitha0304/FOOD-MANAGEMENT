"""Initial database schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-21 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_id', 'users', ['id'], unique=False)

    # 2. restaurants
    op.create_table(
        'restaurants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('cuisine', sa.String(length=100), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('address', sa.String(length=255), nullable=False),
        sa.Column('opens_at', sa.Time(), nullable=False),
        sa.Column('closes_at', sa.Time(), nullable=False),
        sa.Column('is_open', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('avg_rating', sa.Numeric(precision=3, scale=2), nullable=False, server_default='0.00'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('owner_id')
    )
    op.create_index('ix_restaurants_city', 'restaurants', ['city'], unique=False)
    op.create_index('ix_restaurants_cuisine', 'restaurants', ['cuisine'], unique=False)
    op.create_index('ix_restaurants_id', 'restaurants', ['id'], unique=False)
    op.create_index('ix_restaurants_name', 'restaurants', ['name'], unique=False)

    # 3. menu_categories
    op.create_table(
        'menu_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('restaurant_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_menu_categories_id', 'menu_categories', ['id'], unique=False)
    op.create_index('ix_menu_categories_restaurant_id', 'menu_categories', ['restaurant_id'], unique=False)

    # 4. menu_items
    op.create_table(
        'menu_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('restaurant_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('is_veg', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_available', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['menu_categories.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_menu_items_id', 'menu_items', ['id'], unique=False)
    op.create_index('ix_menu_items_name', 'menu_items', ['name'], unique=False)
    op.create_index('ix_menu_items_restaurant_id', 'menu_items', ['restaurant_id'], unique=False)

    # 5. addresses
    op.create_table(
        'addresses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('line1', sa.String(length=255), nullable=False),
        sa.Column('line2', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('pincode', sa.String(length=10), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_addresses_id', 'addresses', ['id'], unique=False)
    op.create_index('ix_addresses_user_id', 'addresses', ['user_id'], unique=False)

    # 6. orders
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_no', sa.String(length=50), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('restaurant_id', sa.Integer(), nullable=False),
        sa.Column('address_id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('item_total', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('tax_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('delivery_fee', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('grand_total', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('placed_at', sa.DateTime(), nullable=False),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['address_id'], ['addresses.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['agent_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['customer_id'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_orders_customer_id', 'orders', ['customer_id'], unique=False)
    op.create_index('ix_orders_id', 'orders', ['id'], unique=False)
    op.create_index('ix_orders_order_no', 'orders', ['order_no'], unique=True)
    op.create_index('ix_orders_restaurant_id', 'orders', ['restaurant_id'], unique=False)
    op.create_index('ix_orders_status', 'orders', ['status'], unique=False)

    # 7. order_items
    op.create_table(
        'order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('menu_item_id', sa.Integer(), nullable=False),
        sa.Column('item_name_snapshot', sa.String(length=150), nullable=False),
        sa.Column('unit_price_snapshot', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('line_total', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['menu_item_id'], ['menu_items.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_order_items_id', 'order_items', ['id'], unique=False)
    op.create_index('ix_order_items_order_id', 'order_items', ['order_id'], unique=False)

    # 8. order_status_history
    op.create_table(
        'order_status_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('from_status', sa.String(length=50), nullable=True),
        sa.Column('to_status', sa.String(length=50), nullable=False),
        sa.Column('changed_by', sa.Integer(), nullable=False),
        sa.Column('changed_at', sa.DateTime(), nullable=False),
        sa.Column('remark', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['changed_by'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_order_status_history_id', 'order_status_history', ['id'], unique=False)
    op.create_index('ix_order_status_history_order_id', 'order_status_history', ['order_id'], unique=False)

    # 9. ratings
    op.create_table(
        'ratings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('restaurant_rating', sa.Integer(), nullable=False),
        sa.Column('agent_rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_id')
    )
    op.create_index('ix_ratings_id', 'ratings', ['id'], unique=False)
    op.create_index('ix_ratings_order_id', 'ratings', ['order_id'], unique=True)


def downgrade() -> None:
    op.drop_table('ratings')
    op.drop_table('order_status_history')
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('addresses')
    op.drop_table('menu_items')
    op.drop_table('menu_categories')
    op.drop_table('restaurants')
    op.drop_table('users')
