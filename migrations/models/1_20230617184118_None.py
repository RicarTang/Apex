from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `permission` (
    `created_at` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `modified_at` DATETIME(6) NOT NULL  COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(20) NOT NULL UNIQUE COMMENT '权限名称',
    `description` VARCHAR(50) NOT NULL  COMMENT '权限解释',
    `permission_code` SMALLINT NOT NULL  COMMENT '权限级别代码' DEFAULT 1
) CHARACTER SET utf8mb4 COMMENT='权限表';
CREATE TABLE IF NOT EXISTS `role` (
    `created_at` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `modified_at` DATETIME(6) NOT NULL  COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(20) NOT NULL UNIQUE COMMENT '角色名称'
) CHARACTER SET utf8mb4 COMMENT='角色表';
CREATE TABLE IF NOT EXISTS `users` (
    `created_at` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `modified_at` DATETIME(6) NOT NULL  COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `username` VARCHAR(20) NOT NULL UNIQUE COMMENT '用户名',
    `name` VARCHAR(50)   COMMENT '名',
    `surname` VARCHAR(50)   COMMENT '姓',
    `descriptions` VARCHAR(30)   COMMENT '个人描述',
    `password` VARCHAR(128) NOT NULL  COMMENT '密码',
    `disabled` SMALLINT NOT NULL  COMMENT '用户活动状态' DEFAULT 0
) CHARACTER SET utf8mb4 COMMENT='用户模型';
CREATE TABLE IF NOT EXISTS `comments` (
    `created_at` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `modified_at` DATETIME(6) NOT NULL  COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `comment` LONGTEXT NOT NULL  COMMENT '用户评论',
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_comments_users_24d9ac18` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='用户评论模型';
CREATE TABLE IF NOT EXISTS `permission_role` (
    `permission_id` INT NOT NULL,
    `role_id` INT NOT NULL,
    FOREIGN KEY (`permission_id`) REFERENCES `permission` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`role_id`) REFERENCES `role` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `role_users` (
    `role_id` INT NOT NULL,
    `users_id` INT NOT NULL,
    FOREIGN KEY (`role_id`) REFERENCES `role` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`users_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
