import json


class Config:

    def __init__(self, filename='utils/config/config.json'):

        self.token: str = ''
        self.shards: int = 0
        self.channel: int = 0
        self.adminID: int = 0
        self.coAdminID: int = 0
        self.Owner: int = 0
        self.db_user: str = ''
        self.db_pass: str = ''
        self.db_name: str = ''

        try:
            file = open(filename, 'x')
            self.write_conf(file)
        except FileExistsError:
            file = open(filename, 'r')
            self.read_conf(file)

        file.close()

    def write_conf(self, file):
        output = {
            'token': '$YOURTOKENHERE\n',
            'shards': '5',
            'channel': '$YOURCHANNELIDHERE\n',
            'admin': '$ADMINID\n',
            'co-admin': '$COADAMINID\n',
            'owner': '$YOURIDHERE\n',
            'db_user': 'default\n',
            'db_password': 'pass\n',
            'db_name': 'db'
        }
        file.write(json.dumps(output))

    def read_conf(self, file):
        config_in = file.read()
        config_parsed = json.loads(config_in)
        self.token = config_parsed['token']
        self.shards = int(config_parsed['shards'])
        self.channel = int(config_parsed['channel'])
        self.adminID = int(config_parsed['admin'])
        self.coAdminID = int(config_parsed['co-admin'])
        self.Owner = int(config_parsed['owner'])
        self.db_user = config_parsed['db_user']
        self.db_pass = config_parsed['db_pass']
        self.db_name = config_parsed['db_name']