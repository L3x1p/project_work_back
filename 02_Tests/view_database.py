"""
Script to view current database entries for users, career fields, and skills.
Run this to see what data is stored in the database.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import User, CareerField, UserSkill, RefreshToken

# Database URL - same as in main.py
#DATABASE_URL = os.getenv(
#     "DATABASE_URL",
#    "postgresql://auth_user:Qqwerty1!@localhost:5432/auth_db"
#)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/postgres"
)


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def view_database():
    """View all database entries"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("DATABASE ENTRIES")
        print("=" * 80)
        
        # Users
        users = db.query(User).all()
        print(f"\n? USERS ({len(users)} total):")
        print("-" * 80)
        if users:
            for user in users:
                print(f"  ID: {user.id}")
                print(f"  Username: {user.username}")
                print(f"  Active: {user.is_active}")
                print()
        else:
            print("  No users found")
        
        # Refresh Tokens
        tokens = db.query(RefreshToken).all()
        print(f"\n? REFRESH TOKENS ({len(tokens)} total):")
        print("-" * 80)
        if tokens:
            for token in tokens:
                user = db.query(User).filter(User.id == token.user_id).first()
                print(f"  Token ID: {token.id}")
                print(f"  User: {user.username if user else 'Unknown'} (ID: {token.user_id})")
                print(f"  Expires: {token.expires_at}")
                print(f"  Created: {token.created_at}")
                print()
        else:
            print("  No refresh tokens found")
        
        # Career Fields
        career_fields = db.query(CareerField).all()
        print(f"\n? CAREER FIELDS ({len(career_fields)} total):")
        print("-" * 80)
        if career_fields:
            for field in career_fields:
                user = db.query(User).filter(User.id == field.user_id).first() if field.user_id else None
                skills = db.query(UserSkill).filter(UserSkill.career_field_id == field.id).all()
                print(f"  ID: {field.id}")
                print(f"  User: {user.username if user else 'Anonymous'} (ID: {field.user_id})")
                print(f"  Field: {field.field_name}")
                print(f"  Summary: {field.summary[:100] if field.summary else 'N/A'}...")
                print(f"  Skills in this field: {len(skills)}")
                print(f"  Created: {field.created_at}")
                print()
        else:
            print("  No career fields found")
        
        # User Skills
        skills = db.query(UserSkill).all()
        print(f"\n??  USER SKILLS ({len(skills)} total):")
        print("-" * 80)
        if skills:
            # Group by user
            skills_by_user = {}
            for skill in skills:
                user_id = skill.user_id or "anonymous"
                if user_id not in skills_by_user:
                    skills_by_user[user_id] = []
                skills_by_user[user_id].append(skill)
            
            for user_id, user_skills in skills_by_user.items():
                user = db.query(User).filter(User.id == user_id).first() if user_id != "anonymous" else None
                print(f"  User: {user.username if user else 'Anonymous'} (ID: {user_id})")
                print(f"  Total Skills: {len(user_skills)}")
                print(f"  Skills: {', '.join([s.skill_name for s in user_skills])}")
                print()
        else:
            print("  No skills found")
        
        # Summary Statistics
        print("\n" + "=" * 80)
        print("? SUMMARY STATISTICS")
        print("=" * 80)
        print(f"  Total Users: {len(users)}")
        print(f"  Total Career Fields: {len(career_fields)}")
        print(f"  Total Skills: {len(skills)}")
        from datetime import datetime
        active_tokens = [t for t in tokens if t.expires_at > datetime.utcnow()] if tokens else []
        print(f"  Active Refresh Tokens: {len(active_tokens)}")
        
        # Skills per user
        if skills:
            print(f"\n  Skills per User:")
            for user_id, user_skills in skills_by_user.items():
                user = db.query(User).filter(User.id == user_id).first() if user_id != "anonymous" else None
                username = user.username if user else "Anonymous"
                print(f"    {username}: {len(user_skills)} skills")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"? Error reading database: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    view_database()

