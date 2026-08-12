# YOUNG STAR ITC — Authentication Module Baseline

class AuthManager:
    def __init__(self):
        self.users = {
            "admin@youngstar.itc": "securepass123"
        }

    def authenticate(self, email: str, password: str):
        if email in self.users and self.users[email] == password:
            return {"status": "SUCCESS", "token": "youngstar_jwt_token_valid_2026", "user": email}
        return {"status": "FAILED", "message": "Invalid email or password"}
