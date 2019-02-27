def is_admin(commands, config):
    async def predicate(ctx):
        return ctx.author.id == int(config.adminID) or ctx.author.id == int(config.coAdminID)
    return commands.check(predicate)
