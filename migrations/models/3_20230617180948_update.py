from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `permission` (
    `created_at` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `modified_at` DATETIME(6) NOT NULL  COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(20) NOT NULL UNIQUE COMMENT '权限名称',
    `description` VARCHAR(50) NOT NULL  COMMENT '权限解释',
    `code` SMALLINT NOT NULL  COMMENT '权限级别代码' DEFAULT 1
) CHARACTER SET utf8mb4 COMMENT='权限表';
        CREATE TABLE IF NOT EXISTS `role` (
    `created_at` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `modified_at` DATETIME(6) NOT NULL  COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(20) NOT NULL UNIQUE COMMENT '角色名称'
) CHARACTER SET utf8mb4 COMMENT='角色表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `role_users`;
        DROP TABLE IF EXISTS `permission`;
        DROP TABLE IF EXISTS `role`;"""
