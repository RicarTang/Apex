from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `users` ADD `is_active` SMALLINT NOT NULL  COMMENT '用户活动状态,0:disable,1:enabled' DEFAULT 1;
        ALTER TABLE `users` DROP COLUMN `disabled`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `users` ADD `disabled` SMALLINT NOT NULL  COMMENT '用户活动状态,0:enabled,1:disabled' DEFAULT 0;
        ALTER TABLE `users` DROP COLUMN `is_active`;"""
