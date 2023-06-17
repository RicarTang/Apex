from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `permission` MODIFY COLUMN `description` VARCHAR(50)   COMMENT '权限解释';
        ALTER TABLE `role` MODIFY COLUMN `description` VARCHAR(50)   COMMENT '角色详情';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `role` MODIFY COLUMN `description` VARCHAR(50) NOT NULL  COMMENT '角色详情';
        ALTER TABLE `permission` MODIFY COLUMN `description` VARCHAR(50) NOT NULL  COMMENT '权限解释';"""
