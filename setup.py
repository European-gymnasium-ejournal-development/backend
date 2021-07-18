from setuptools import setup

setup(
    name='European gymnasium',
    version='1.0',
    long_description=__doc__,
    packages=['app', 'app.ApiHandlers', 'app.Database', 'create', 'ManageBackApi'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask', 'Flask-Cors', 'Flask-MySQLdb', 'Flask-RESTful', 'Flask-SQLAlchemy',
                      'SQLAlchemy', 'fpdf', 'google-api-core', 'google-api-python-client',
                      'google-auth', 'google-oauth', 'google-oauth2-tool', 'google-trans-new',
                      'googletrans', 'googletrans2', 'mysql', 'mysqlclient', 'oauth2client']
)