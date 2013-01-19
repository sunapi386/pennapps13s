from setuptools import setup

setup(name='Marmoset',
    version='0.1',
    description='OpenShift App for PennApps Spring 2013',
    author='Michael Chang',
    author_email='michael.chang@azuresky.ca',
    url='http://marmoset.iterate.ca/',
    install_requires=[
        'Flask>=0.9',
        'SQLAlchemy>=0.8.0b2',
        'Flask-SQLAlchemy>=0.16',
        'psycopg2>=2.4.6',
    ],
)
