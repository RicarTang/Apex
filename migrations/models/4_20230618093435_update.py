from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `comments` RENAME COLUMN `modified_at` TO `update_at`;
        ALTER TABLE `permission` RENAME COLUMN `modified_at` TO `update_at`;
        ALTER TABLE `role` RENAME COLUMN `modified_at` TO `update_at`;
        ALTER TABLE `users` RENAME COLUMN `modified_at` TO `update_at`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `role` RENAME COLUMN `update_at` TO `modified_at`;
        ALTER TABLE `users` RENAME COLUMN `update_at` TO `modified_at`;
        ALTER TABLE `comments` RENAME COLUMN `update_at` TO `modified_at`;
        ALTER TABLE `permission` RENAME COLUMN `update_at` TO `modified_at`;"""
