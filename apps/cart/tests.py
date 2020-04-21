from django.test import TestCase

# Create your tests here.

dic1 = {b'3': b'4', b'2': b'1', b'5': b'7', b'12': b'28'}

for key in dic1:
    print('key: ', key.decode(), '   -value: ', dic1[key].decode())