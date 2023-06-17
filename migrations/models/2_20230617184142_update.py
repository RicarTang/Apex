from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `role` ADD `description` VARCHAR(50) NOT NULL  COMMENT '角色详情';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `role` DROP COLUMN `description`;"""
