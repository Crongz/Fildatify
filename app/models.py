from flask_login import UserMixin

class User(UserMixin):

    def __init__(self):
        self.id = None
        self.gender = None
        self.interested_in = None
        self.birthdate = None
        self.name = None
        self.location = None
        self.email = None
        self.picture_url = None
        self.provided_location = None

    def loadData(self, data):
        self.id = data.id
        self.gender = data.gender
        self.interested_in = data.interested_in
        self.birthdate = data.birthdate
        self.name = data.name
        self.location = data.location
        self.email = data.email
        self.provided_location = data.provided_location
        self.picture_url = data.picture_url

        
    def __repr__(self):
        return "{}/{}/{}".format(self.id, self.name, self.email)
