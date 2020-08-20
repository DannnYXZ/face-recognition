class Repository:
    """Not thread safe"""
    def __init__(self, data_source):
        self.data_source = data_source
        self.connection = None

    def install_connection(self, connection):
        self.connection = connection

    def remove_connection(self):
        self.connection = None

    def get_connection(self):
        return self.connection if self.connection else self.data_source.begin()