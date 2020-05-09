from django.test import TestCase

# Create your tests here.

from datetime import datetime

list1 = range(1, 10)

for a in enumerate(list1, start=1):
    print(a)


# ORDER_STATUS_CHOICS = (
#         (1, '待支付'),
#         (2, '待发货'),
#         (3, '待收货'),
#         (4, '待评价'),
#         (5, '已完成')
#     )

# print(ORDER_STATUS_CHOICS.keys())

# a = datetime.now().strftime('%Y%m%d%H%M%S')
# print(a)

# print(datetime.now())