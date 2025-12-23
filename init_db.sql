-- 创建数据库
CREATE DATABASE IF NOT EXISTS role_auth_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE role_auth_system;

-- 用户表（存储所有角色用户）
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    user_code VARCHAR(20) NOT NULL UNIQUE COMMENT '学号/工号/管理员账号（唯一）',
    password VARCHAR(100) NOT NULL COMMENT 'bcrypt加密后的密码',
    role ENUM('student', 'teacher', 'admin') NOT NULL COMMENT '角色：学生/教师/管理员',
    real_name VARCHAR(50) NOT NULL COMMENT '真实姓名',
    phone VARCHAR(20) DEFAULT NULL COMMENT '手机号',
    email VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT '用户信息表';

-- 权限表
DROP TABLE IF EXISTS permissions;
CREATE TABLE permissions (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    permission_code VARCHAR(50) NOT NULL UNIQUE COMMENT '权限编码（如：user:import,user:manage）',
    permission_name VARCHAR(50) NOT NULL COMMENT '权限名称'
) COMMENT '权限表';

-- 角色-权限关联表
DROP TABLE IF EXISTS role_permissions;
CREATE TABLE role_permissions (
    role ENUM('student', 'teacher', 'admin') NOT NULL COMMENT '角色',
    permission_code VARCHAR(50) NOT NULL COMMENT '权限编码',
    PRIMARY KEY (role, permission_code),
    FOREIGN KEY (permission_code) REFERENCES permissions(permission_code) ON DELETE CASCADE
) COMMENT '角色权限关联表';

-- 初始化权限数据
INSERT INTO permissions (permission_code, permission_name) VALUES
('user:login', '用户登录'),
('user:register', '用户注册'),
('user:import', '批量导入用户'),
('user:manage', '用户管理'),
('student:view', '学生权限'),
('teacher:view', '教师权限');

-- 初始化角色权限
INSERT INTO role_permissions (role, permission_code) VALUES
-- 学生权限
('student', 'user:login'),
('student', 'student:view'),
-- 教师权限
('teacher', 'user:login'),
('teacher', 'teacher:view'),
-- 管理员权限
('admin', 'user:login'),
('admin', 'user:import'),
('admin', 'user:manage');
