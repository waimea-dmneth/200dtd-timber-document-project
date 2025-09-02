from app.helpers.db      import connect_db

def CreateDBForm():
    with connect_db() as client:
        sql = "INSERT INTO Requests DEFAULT VALUES RETURNING id"
        result = client.execute(sql, []).rows[0]
        return result["id"]
    
def getDBForm():
    