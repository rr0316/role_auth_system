import pymysql
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Database:
    """数据库操作类"""
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        """建立数据库连接"""
        try:
            self.conn = pymysql.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', '123456'),
                database=os.getenv('DB_NAME', 'role_auth_system'),
                charset='utf8mb4'
            )
            self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        except pymysql.MySQLError as e:
            raise Exception(f"数据库连接失败：{e}")

    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def execute(self, sql, params=None):
        """执行单条SQL语句（增删改）"""
        try:
            self.cursor.execute(sql, params or ())
            self.conn.commit()
            return self.cursor.rowcount
        except pymysql.MySQLError as e:
            self.conn.rollback()
            raise Exception(f"SQL执行失败：{e}")

    def query(self, sql, params=None):
        """执行查询SQL"""
        try:
            self.cursor.execute(sql, params or ())
            return self.cursor.fetchall()
        except pymysql.MySQLError as e:
            raise Exception(f"查询失败：{e}")

    def get_one(self, sql, params=None):
        """查询单条数据"""
        try:
            self.cursor.execute(sql, params or ())
            return self.cursor.fetchone()
        except pymysql.MySQLError as e:
            raise Exception(f"查询失败：{e}")

    def check_user_code_exists(self, user_code):
        """检查学/工号是否已存在"""
        sql = "SELECT 1 FROM users WHERE user_code = %s LIMIT 1"
        result = self.get_one(sql, (user_code,))
        return result is not None

    def get_user_by_code(self, user_code):
        """根据学/工号查询用户"""
        sql = "SELECT * FROM users WHERE user_code = %s LIMIT 1"
        return self.get_one(sql, (user_code,))

    def get_role_permissions(self, role):
        """获取角色对应的权限列表"""
        sql = """
        SELECT p.permission_code 
        FROM permissions p
        JOIN role_permissions rp ON p.permission_code = rp.permission_code
        WHERE rp.role = %s
        """
        result = self.query(sql, (role,))
        return [item['permission_code'] for item in result]
