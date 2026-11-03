"""Django project package for the news application.

Importing this package registers PyMySQL as the ``MySQLdb`` driver so Django's
MySQL backend can connect to MySQL or MariaDB without a compiled client.
"""
import pymysql

pymysql.install_as_MySQLdb()
