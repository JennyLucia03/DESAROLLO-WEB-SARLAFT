from .entities.User import User

class ModelUser():

    @classmethod
    def login(self, db, user):
        try:
            cursor=db.connection.cursor()
            sql="""SELECT id,username,password,fullname,empleado_id,id_rol FROM login WHERE username ='{}'""".format(user.username)
            cursor.execute(sql)
            row=cursor.fetchone()
            if row != None:
                user=User(row[0],row[1],User.check_password(row[2],user.password),row[3],row[4],row[5])
                return user
            else:
                return None   
        except Exception as ex:
            raise Exception(ex)
            
    @classmethod
    def get_by_id(self, db, id):
        try:
            cursor = db.connection.cursor()
            sql = "SELECT id, username, fullname, empleado_id, id_rol FROM login WHERE id = {}".format(id)
            cursor.execute(sql)
            row = cursor.fetchone()
            if row != None:
                return User(row[0], row[1], None, row[2],row[3], row[4])
            else:
                return None
        except Exception as ex:
            raise Exception(ex)
        
        
    
