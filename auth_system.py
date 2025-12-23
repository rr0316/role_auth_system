import bcrypt
from database import Database

class AuthSystem:
    """用户认证系统（注册、登录、权限控制）"""
    def __init__(self):
        self.db = Database()

    def __del__(self):
        self.db.close()

    def _validate_user_code(self, user_code, role):
        """验证学/工号格式"""
        if role == 'student':
            # 学生：13位数字学号
            if not (len(user_code) == 13 and user_code.isdigit()):
                return False, "学生学号必须为13位数字"
        elif role == 'teacher':
            # 教师：8位数字工号
            if not (len(user_code) == 8 and user_code.isdigit()):
                return False, "教师工号必须为8位数字"
        elif role == 'admin':
            # 管理员：自定义格式（字母+数字，长度4-20）
            if not (4 <= len(user_code) <= 20 and user_code.isalnum()):
                return False, "管理员账号必须为4-20位字母/数字组合"
        return True, ""

    def _encrypt_password(self, password):
        """使用bcrypt加密密码"""
        salt = bcrypt.gensalt()
        hashed_pwd = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_pwd.decode('utf-8')

    def _verify_password(self, plain_pwd, hashed_pwd):
        """验证密码"""
        return bcrypt.checkpw(plain_pwd.encode('utf-8'), hashed_pwd.encode('utf-8'))

    def register(self, user_code, password, role, real_name, phone=None, email=None):
        """
        用户注册
        :param user_code: 学号/工号/管理员账号
        :param password: 明文密码
        :param role: 角色（student/teacher/admin）
        :param real_name: 真实姓名
        :param phone: 手机号（可选）
        :param email: 邮箱（可选）
        :return: 注册结果（bool, 提示信息）
        """
        # 1. 验证角色
        if role not in ['student', 'teacher', 'admin']:
            return False, "角色必须为student/teacher/admin"
        
        # 2. 验证学/工号格式
        valid, msg = self._validate_user_code(user_code, role)
        if not valid:
            return False, msg
        
        # 3. 检查学/工号唯一性
        if self.db.check_user_code_exists(user_code):
            return False, f"{role}账号{user_code}已存在"
        
        # 4. 加密密码
        hashed_pwd = self._encrypt_password(password)
        
        # 5. 插入数据库
        sql = """
        INSERT INTO users (user_code, password, role, real_name, phone, email)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        try:
            self.db.execute(sql, (user_code, hashed_pwd, role, real_name, phone, email))
            return True, f"{role}账号{user_code}注册成功"
        except Exception as e:
            return False, f"注册失败：{str(e)}"

    def login(self, user_code, password):
        """
        用户登录
        :param user_code: 学号/工号/管理员账号
        :param password: 明文密码
        :return: 登录结果（bool, 数据/提示信息）
        """
        # 1. 查询用户
        user = self.db.get_user_by_code(user_code)
        if not user:
            return False, "账号不存在"
        
        # 2. 验证密码
        if not self._verify_password(password, user['password']):
            return False, "密码错误"
        
        # 3. 获取用户权限
        permissions = self.db.get_role_permissions(user['role'])
        
        # 4. 返回用户信息（隐藏密码）
        user.pop('password')
        return True, {
            'user': user,
            'permissions': permissions
        }

    def check_permission(self, role, permission_code):
        """
        检查角色是否拥有指定权限
        :param role: 角色
        :param permission_code: 权限编码
        :return: bool
        """
        permissions = self.db.get_role_permissions(role)
        return permission_code in permissions

# 测试示例
if __name__ == "__main__":
    auth = AuthSystem()
    
    # 注册测试
    # print(auth.register("2025000000001", "123456", "student", "张三", "13800138000", "zhangsan@test.com"))
    # print(auth.register("88888888", "123456", "teacher", "李四", "13900139000", "lisi@test.com"))
    # print(auth.register("admin123", "admin123", "admin", "管理员", "13700137000", "admin@test.com"))
    
    # 登录测试
    # success, data = auth.login("2025000000001", "123456")
    # print(success, data)
    
    # 权限检查
    # print(auth.check_permission("admin", "user:import"))  # True
    # print(auth.check_permission("student", "user:import"))  # False
