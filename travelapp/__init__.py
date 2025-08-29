try:
    import pymysql
    pymysql.install_as_MySQLdb()
except Exception:
    # PyMySQL not installed; ignore during non-MySQL setups
    pass

