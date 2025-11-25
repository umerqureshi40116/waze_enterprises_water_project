from app.db.database import SessionLocal
from app.models.user import User

s=SessionLocal()
users=s.query(User).all()
for u in users:
    print(u.id, u.username, u.email, (u.password_hash[:60] + '...') if u.password_hash else None)
s.close()
