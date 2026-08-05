import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import Base
from app.models.user import User
from app.models.profile import Profile, Photo
from app.models.interaction import Interest, ProfileVisit, ContactView, Favourite, Note, Block, Pass
from app.models.chat import ChatMessage
from app.utils.security import get_password_hash

from app.database import engine, SessionLocal, Base

def seed_db():
    print("Recreating database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("Inserting seed data...")
        
        # 1. Create Users
        users_data = [
            # Main Test User (Male, Free)
            {"email": "ahmed@example.com", "password": "password123", "membership_status": "Free", "plan_type": None, "views": 5, "messages": 5, "calls": 0},
            # Main Test User 2 (Female, Premium)
            {"email": "fatima@example.com", "password": "password123", "membership_status": "Premium", "plan_type": "Gold", "views": 100, "messages": 1000, "calls": 300},
            # Other Matches (Females for Ahmed, Males for Fatima)
            {"email": "aisha@example.com", "password": "password123", "membership_status": "Free", "plan_type": None, "views": 5, "messages": 5, "calls": 0},
            {"email": "zainab@example.com", "password": "password123", "membership_status": "Premium", "plan_type": "Silver", "views": 20, "messages": 200, "calls": 60},
            {"email": "yasmin@example.com", "password": "password123", "membership_status": "Free", "plan_type": None, "views": 5, "messages": 5, "calls": 0},
            {"email": "mariam@example.com", "password": "password123", "membership_status": "Free", "plan_type": None, "views": 5, "messages": 5, "calls": 0},
            {"email": "bilal@example.com", "password": "password123", "membership_status": "Free", "plan_type": None, "views": 5, "messages": 5, "calls": 0},
            {"email": "yousef@example.com", "password": "password123", "membership_status": "Premium", "plan_type": "Platinum", "views": 9999, "messages": 9999, "calls": 1000},
        ]
        
        db_users = []
        for ud in users_data:
            user = User(
                email=ud["email"],
                hashed_password=get_password_hash(ud["password"]),
                membership_status=ud["membership_status"],
                plan_type=ud["plan_type"],
                remaining_contact_views=ud["views"],
                remaining_messages=ud["messages"],
                remaining_call_time=ud["calls"],
                plan_validity=datetime.datetime.utcnow() + datetime.timedelta(days=90) if ud["plan_type"] else None,
                id_verification_status="Verified" if ud["email"] in ["ahmed@example.com", "fatima@example.com", "yousef@example.com"] else "Unverified",
                last_active_at=datetime.datetime.utcnow() - datetime.timedelta(minutes=3) if ud["email"] in ["ahmed@example.com", "aisha@example.com", "yousef@example.com"] else datetime.datetime.utcnow() - datetime.timedelta(hours=2)
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            db_users.append(user)
            
        users_dict = {u.email: u for u in db_users}
        
        # 2. Create Profiles
        profiles_data = [
            {
                "user_id": users_dict["ahmed@example.com"].id,
                "name": "Ahmed Khan",
                "age": 28,
                "gender": "Male",
                "marital_status": "Never Married",
                "language": "Urdu",
                "religion": "Islam",
                "sect": "Sunni",
                "present_location": "Mumbai",
                "profession": "Software Engineer",
                "annual_income": 1200000.0,
                "height": 178.0,
                "weight": 74.0,
                "differently_abled": False,
                "orphan_poor_girl": False,
                "education": "B.Tech Computer Science",
                "partner_age_min": 21,
                "partner_age_max": 27,
                "partner_height_min": 155.0,
                "partner_height_max": 170.0,
            },
            {
                "user_id": users_dict["fatima@example.com"].id,
                "name": "Fatima Bi",
                "age": 25,
                "gender": "Female",
                "marital_status": "Never Married",
                "language": "Hindi",
                "religion": "Islam",
                "sect": "Sunni",
                "present_location": "Delhi",
                "profession": "Doctor",
                "annual_income": 1500000.0,
                "height": 162.0,
                "weight": 56.0,
                "differently_abled": False,
                "orphan_poor_girl": False,
                "education": "MBBS, MD",
                "partner_age_min": 25,
                "partner_age_max": 32,
                "partner_height_min": 170.0,
                "partner_height_max": 185.0,
            },
            {
                "user_id": users_dict["aisha@example.com"].id,
                "name": "Aisha Rahman",
                "age": 24,
                "gender": "Female",
                "marital_status": "Never Married",
                "language": "Bengali",
                "religion": "Islam",
                "sect": "Sunni",
                "present_location": "Kolkata",
                "profession": "Graphic Designer",
                "annual_income": 500000.0,
                "height": 158.0,
                "weight": 52.0,
                "differently_abled": False,
                "orphan_poor_girl": True, # Orphan category
                "education": "B.Sc Design",
                "partner_age_min": 25,
                "partner_age_max": 30,
            },
            {
                "user_id": users_dict["zainab@example.com"].id,
                "name": "Zainab Sheikh",
                "age": 26,
                "gender": "Female",
                "marital_status": "Never Married",
                "language": "English",
                "religion": "Islam",
                "sect": "Shia",
                "present_location": "Mumbai",
                "profession": "Financial Analyst",
                "annual_income": 900000.0,
                "height": 165.0,
                "weight": 58.0,
                "differently_abled": False,
                "orphan_poor_girl": False,
                "education": "MBA Finance",
                "partner_age_min": 26,
                "partner_age_max": 32,
            },
            {
                "user_id": users_dict["yasmin@example.com"].id,
                "name": "Yasmin Qureshi",
                "age": 27,
                "gender": "Female",
                "marital_status": "Divorced",
                "language": "Urdu",
                "religion": "Islam",
                "sect": "Sunni",
                "present_location": "Hyderabad",
                "profession": "Teacher",
                "annual_income": 400000.0,
                "height": 160.0,
                "weight": 60.0,
                "differently_abled": True, # Differently abled category
                "health_or_disabilities": "Minor polio in left leg",
                "orphan_poor_girl": False,
                "education": "M.A. Education",
                "partner_age_min": 27,
                "partner_age_max": 34,
            },
            {
                "user_id": users_dict["mariam@example.com"].id,
                "name": "Mariam Ali",
                "age": 23,
                "gender": "Female",
                "marital_status": "Never Married",
                "language": "Malayalam",
                "religion": "Islam",
                "sect": "Sunni",
                "present_location": "Kochi",
                "profession": "HR Coordinator",
                "annual_income": 350000.0,
                "height": 154.0,
                "weight": 50.0,
                "differently_abled": False,
                "orphan_poor_girl": True, # Poor Girls category
                "education": "BBA",
                "partner_age_min": 24,
                "partner_age_max": 29,
            },
            {
                "user_id": users_dict["bilal@example.com"].id,
                "name": "Bilal Siddiqui",
                "age": 29,
                "gender": "Male",
                "marital_status": "Never Married",
                "language": "Urdu",
                "religion": "Islam",
                "sect": "Sunni",
                "present_location": "Lucknow",
                "profession": "Lecturer",
                "annual_income": 700000.0,
                "height": 175.0,
                "weight": 70.0,
                "differently_abled": False,
                "orphan_poor_girl": False,
                "education": "M.Sc Physics",
                "partner_age_min": 22,
                "partner_age_max": 27,
            },
            {
                "user_id": users_dict["yousef@example.com"].id,
                "name": "Yousef Patel",
                "age": 31,
                "gender": "Male",
                "marital_status": "Never Married",
                "language": "Gujarati",
                "religion": "Islam",
                "sect": "Sunni",
                "present_location": "Ahmedabad",
                "profession": "Business Owner",
                "annual_income": 3000000.0,
                "height": 182.0,
                "weight": 80.0,
                "differently_abled": False,
                "orphan_poor_girl": False,
                "education": "Bachelor of Commerce",
                "partner_age_min": 22,
                "partner_age_max": 28,
            }
        ]
        
        for pd in profiles_data:
            profile = Profile(
                user_id=pd["user_id"],
                name=pd["name"],
                age=pd["age"],
                gender=pd["gender"],
                marital_status=pd["marital_status"],
                language=pd["language"],
                religion=pd["religion"],
                sect=pd["sect"],
                present_location=pd["present_location"],
                present_country="India",
                present_state={"Mumbai": "Maharashtra", "Delhi": "Delhi", "Kolkata": "West Bengal", "Hyderabad": "Telangana", "Kochi": "Kerala", "Lucknow": "Uttar Pradesh", "Ahmedabad": "Gujarat"}.get(pd["present_location"], "Delhi"),
                partner_country_pref=["India"],
                partner_state_pref=["All"],
                profession=pd["profession"],
                annual_income=pd["annual_income"],
                height=pd["height"],
                weight=pd["weight"],
                differently_abled=pd["differently_abled"],
                orphan_poor_girl=pd["orphan_poor_girl"],
                education=pd["education"],
                health_or_disabilities=pd.get("health_or_disabilities"),
                tagline=f"Looking for a pious partner who values family.",
                profile_description="A well-settled individual seeking a meaningful marriage connection built on respect and shared values.",
                about="I am simple, religious, and open-minded. I enjoy traveling and reading books.",
                primary_no="+91-9876543210",
                whatsapp_no="+91-9876543210",
                preferred_contact_method="WhatsApp",
                best_time_to_call="Evenings 6 PM to 9 PM",
                contact_person="Self / Parent",
                full_address="Flat 101, Residency Towers, Central Street",
                family_type="Nuclear",
                financial_status="Middle Class" if pd["annual_income"] < 800000 else "Upper Middle Class",
                interests=["Reading", "Cooking", "Travel"],
                partner_age_min=pd.get("partner_age_min", 18),
                partner_age_max=pd.get("partner_age_max", 70),
                partner_height_min=pd.get("partner_height_min", 150.0),
                partner_height_max=pd.get("partner_height_max", 190.0)
            )
            db.add(profile)
            db.commit()
            
        print("Profiles created successfully!")
        
        # 3. Create Photos
        photo_url_base = "https://images.unsplash.com/photo-"
        photos_data = [
            {"user_id": users_dict["ahmed@example.com"].id, "url": f"{photo_url_base}1506794778244-f4e3c50a1018", "is_main": True},
            {"user_id": users_dict["fatima@example.com"].id, "url": f"{photo_url_base}1534528741775-53994a69daeb", "is_main": True},
            {"user_id": users_dict["aisha@example.com"].id, "url": f"{photo_url_base}1524504388940-b1c1722653e1", "is_main": True},
            {"user_id": users_dict["zainab@example.com"].id, "url": f"{photo_url_base}1544005313-94ddf0286df2", "is_main": True},
            {"user_id": users_dict["yasmin@example.com"].id, "url": f"{photo_url_base}1508214751196-bcfd4ca60f91", "is_main": True},
            {"user_id": users_dict["mariam@example.com"].id, "url": f"{photo_url_base}1494790108377-be9c29b29330", "is_main": True},
            {"user_id": users_dict["bilal@example.com"].id, "url": f"{photo_url_base}1500648767791-00dcc994a43e", "is_main": True},
            {"user_id": users_dict["yousef@example.com"].id, "url": f"{photo_url_base}1472099645785-5658abf4ff4e", "is_main": True},
        ]
        
        for p in photos_data:
            photo = Photo(user_id=p["user_id"], url=p["url"], is_main=p["is_main"], is_approved=True)
            db.add(photo)
        db.commit()
        print("Profile photos added!")

        # 4. Create Interactions (Visits, Interests, Favourites, Notes)
        # Ahmed visits Aisha and Fatima
        visit1 = ProfileVisit(visitor_id=users_dict["ahmed@example.com"].id, visited_id=users_dict["fatima@example.com"].id)
        visit2 = ProfileVisit(visitor_id=users_dict["ahmed@example.com"].id, visited_id=users_dict["aisha@example.com"].id)
        # Zainab visits Ahmed
        visit3 = ProfileVisit(visitor_id=users_dict["zainab@example.com"].id, visited_id=users_dict["ahmed@example.com"].id)
        db.add_all([visit1, visit2, visit3])
        
        # Ahmed sends interest to Aisha (Pending) and Fatima (Accepted)
        interest1 = Interest(sender_id=users_dict["ahmed@example.com"].id, receiver_id=users_dict["aisha@example.com"].id, status="Pending")
        interest2 = Interest(sender_id=users_dict["ahmed@example.com"].id, receiver_id=users_dict["fatima@example.com"].id, status="Accepted")
        # Zainab sends interest to Ahmed (Pending)
        interest3 = Interest(sender_id=users_dict["zainab@example.com"].id, receiver_id=users_dict["ahmed@example.com"].id, status="Pending")
        db.add_all([interest1, interest2, interest3])
        
        # Ahmed Favourites Fatima
        fav = Favourite(user_id=users_dict["ahmed@example.com"].id, favourited_id=users_dict["fatima@example.com"].id)
        db.add(fav)

        # Ahmed adds private note on Fatima
        fatima_profile = db.query(Profile).filter(Profile.user_id == users_dict["fatima@example.com"].id).first()
        note = Note(user_id=users_dict["ahmed@example.com"].id, profile_id=fatima_profile.id, note_text="Spoke with her father, seems very polite and well-educated.")
        db.add(note)
        
        db.commit()
        print("Interactions created!")

        # 5. Chat History
        # Chat between Ahmed and Fatima (Interest Accepted)
        msg1 = ChatMessage(sender_id=users_dict["ahmed@example.com"].id, receiver_id=users_dict["fatima@example.com"].id, message_text="Assalamu alaikum Fatima, thanks for accepting my interest request.", message_type="chat")
        msg2 = ChatMessage(sender_id=users_dict["fatima@example.com"].id, receiver_id=users_dict["ahmed@example.com"].id, message_text="Walaikum assalam Ahmed. Glad to connect. Tell me more about your family background.", message_type="chat", is_read=True)
        msg3 = ChatMessage(sender_id=users_dict["ahmed@example.com"].id, receiver_id=users_dict["fatima@example.com"].id, message_text="Sure, we are a nuclear family based in Mumbai. My father is retired, and mother is a homemaker.", message_type="chat")
        
        # Call log between Ahmed and Fatima
        call_msg = ChatMessage(sender_id=users_dict["fatima@example.com"].id, receiver_id=users_dict["ahmed@example.com"].id, message_type="call", call_duration=480) # 8 minutes call
        
        db.add_all([msg1, msg2, msg3, call_msg])
        db.commit()
        print("Chat messages initialized!")
        
        print("Database successfully seeded with matrimony test records!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
