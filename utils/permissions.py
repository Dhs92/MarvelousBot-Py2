#import psycopg2

async def perm_check(permission, ctx):
    author = ctx.message.author
