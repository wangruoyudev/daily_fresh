from django.test import TestCase

# Create your tests here.

dic1 = {b'5': b'3', b'10': b'1', b'1': b'1', b'7': b'2'}

print(type(dic1.items()))

for key, value in dic1.items():
    # print('key: ', key.decode(), '   -value: ', dic1[key].decode())
    print('key: ', key.decode(), '   -value: ', value)