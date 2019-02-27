import json


class Config:

    def __init__(self, filename='config/config.json'):

        self.token = int()
        self.shards = int()
        self.channel = int()
        self.adminID = int()
        self.coAdminID = int()

        try:
            file = open(filename, 'x')
            self.writeconf(file)
        except:
            file = open(filename, 'r')
            self.readconf(file)

        file.close()

    def writeconf(self, file):
        output = {
            'token': '$YOURTOKENHERE',
            'shards': '5',
            'channel': '$YOURCHANNELIDHERE',
            'admin': '$ADMINID',
            'co-admin': '$COADAMINID',
        }
        file.write(json.dumps(output))

    def readconf(self, file):
        configIn = file.read()
        configParsed = json.loads(configIn)
        self.token = configParsed['token']
        self.shards = configParsed['shards']
        self.channel = configParsed['channel']
        self.adminID = configParsed['admin']
        self.coAdminID = configParsed['co-admin']