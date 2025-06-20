"""The domain layer represents the underlying domain, mostly consisting of domain entities and,
in some cases, services.
- Business rules, like invariants and algorithms, should all stay in this layer.


- It is mutually known as the repository (infrastructure).
- Returns an instance of the domain.
- User definition.
"""


class User:
    def __init__(
        self, uuid, name, surname, password, email, status, role, location=None, notification=True, id_biometrico=None
    ):
        # attributes
        self.uuid = uuid
        self.name = name
        self.surname = surname
        self.password = password
        self.email = email
        self.status = status
        self.role = role
        self.location = location
        self.notification = notification
        self.id_biometrico = id_biometrico
        return
