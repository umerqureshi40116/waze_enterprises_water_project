from app.db.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash


def upsert_user(user_id: str, username: str, email: str, password: str, role: str) -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.username = username
            user.email = email
            user.password_hash = get_password_hash(password)
            user.role = role
            action = "updated"
        else:
            user = User(
                id=user_id,
                username=username,
                email=email,
                password_hash=get_password_hash(password),
                role=role,
            )
            db.add(user)
            action = "created"
        db.commit()
        print(f"{action.capitalize()} user: {username} ({role})")
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


def run():
    # Set test users with specific passwords
    # waheed: admin / password: admin123
    # umer: umer / password: user123
    upsert_user("waheed", "Waheed", "waheed@example.com", "admin123", "admin")
    upsert_user("umer", "Umer", "umer@example.com", "user123", "user")


if __name__ == "__main__":
    run()
