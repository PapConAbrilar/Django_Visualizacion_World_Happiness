from django.test import TestCase

# Create your tests here.
import pandas

df = pandas.read_csv('world_happiness/2015.csv')
print(df.columns)