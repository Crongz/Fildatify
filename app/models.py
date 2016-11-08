class User:
    def __init__(self, id, name, email, password, birthdate, location, gender="1", interested_in="1"):
        self.id = id
        self.name = name
        self.email = email
        self.birthdate = birthdate
        self.location = location
        self.gender = gender
        self.interested_in = interested_in

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User %r>' % (self.name)
