import sqlite3

def get_connection(db_path="data/candidates.db"):
    return sqlite3.connect(db_path)

# TODO: 添加更多数据库操作函数 