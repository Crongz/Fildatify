from flask_login import UserMixin

class User(UserMixin):

    def __init__(self, data):
        self.id = data[0]
        self.gender = data[1]
        self.interested_in = data[2]
        self.birthdate = data[3]
        self.name = data[4]
        self.location = data[5]
        self.email = data[6]
        
    def __repr__(self):
        return "{}/{}/{}".format(self.id, self.name, self.email)
