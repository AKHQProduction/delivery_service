from infrastructure.persistence.models.employee import map_employee_table
from infrastructure.persistence.models.goods import map_goods_table
from infrastructure.persistence.models.shop import map_shops_table
from infrastructure.persistence.models.user import map_users_table


def map_tables():
    map_users_table()
    map_shops_table()
    map_employee_table()
    map_goods_table()
