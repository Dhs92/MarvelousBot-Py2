import asyncpg

from utils.config.config import Config


async def db_connect():
    config = Config()
    return await asyncpg.connect(database=config.db_name, user=config.db_user, password=config.db_pass)


async def db_create():

    # create cursor
    with db_connect() as connect:

        # create role table
        await connect.execute('''
            CREATE TABLE IF NOT EXISTS roles(
                role_id bigint PRIMARY KEY NOT NULL 
                );
            ''')

        # create permissions table
        await connect.execute('''
            CREATE TABLE IF NOT EXISTS permissions(
                role_id bigint REFERENCES roles(role_id),
                permission text PRIMARY KEY
                );
            ''')

        # create users database
        await connect.execute('''
            CREATE TABLE IF NOT EXISTS users(
                user_id bigint PRIMARY KEY
                );
            ''')

        # create user_role_association
        await connect.execute('''
            CREATE TABLE IF NOT EXISTS user_role_association(
                role_id bigint REFERENCES roles(role_id),
                user_id bigint PRIMARY KEY
                );
            ''')

# TODO add role to database
# TODO add user to database
# TODO add permission to role
