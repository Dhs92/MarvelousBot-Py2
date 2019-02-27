def is_admin(commands, config):
    async def predicate(ctx):
        return ctx.author.id == int(config.adminID) or ctx.author.id == int(config.coAdminID)
    return commands.check(predicate)


def is_owner(commands, config):
    async def predicate(ctx):
        return ctx.author.id == config.Owner
    return commands.check(predicate)
