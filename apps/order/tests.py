from django.test import TestCase

# Create your tests here.


list1 = range(1, 10)

for a in enumerate(list1, start=1):
    print(a)