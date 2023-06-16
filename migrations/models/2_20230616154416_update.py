from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `users` MODIFY COLUMN `disabled` SMALLINT NOT NULL  COMMENT '用户活动状态' DEFAULT 0;
        ALTER TABLE `users` MODIFY COLUMN `disabled` SMALLINT NOT NULL  COMMENT '用户活动状态' DEFAULT 0;
        ALTER TABLE `users` MODIFY COLUMN `disabled` SMALLINT NOT NULL  COMMENT '用户活动状态' DEFAULT 0;
        ALTER TABLE `users` MODIFY COLUMN `disabled` SMALLINT NOT NULL  COMMENT '用户活动状态' DEFAULT 0;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `users` MODIFY COLUMN `disabled` VARCHAR(1) NOT NULL  COMMENT '用户活动状态' DEFAULT 0;
        ALTER TABLE `users` MODIFY COLUMN `disabled` VARCHAR(1) NOT NULL  COMMENT '用户活动状态' DEFAULT 0;
        ALTER TABLE `users` MODIFY COLUMN `disabled` VARCHAR(1) NOT NULL  COMMENT '用户活动状态' DEFAULT 0;
        ALTER TABLE `users` MODIFY COLUMN `disabled` VARCHAR(1) NOT NULL  COMMENT '用户活动状态' DEFAULT 0;"""
