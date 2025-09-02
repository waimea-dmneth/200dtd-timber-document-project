from app.helpers.db      import connect_db

DEFAULT = "None"

class dbForm:
    def __init__(self):
        self.species = DEFAULT
        self.profile = DEFAULT
        
    def getDBForm(self):
        return self

    def updateDBForm(self, field, newValue):
        setattr(self, field, newValue)

    def pushForm(self):
        with connect_db() as client:
            sql = "INSERT INTO Requests VALUES"
            params = [self.species, self.profile]
            client.execute(sql, params)