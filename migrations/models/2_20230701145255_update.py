from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `permission_role`;
        DROP TABLE IF EXISTS `permission`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE `permission_role` (
    `role_id` INT NOT NULL REFERENCES `role` (`id`) ON DELETE CASCADE,
    `permission_id` INT NOT NULL REFERENCES `permission` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;"""
