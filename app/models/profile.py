import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, Text, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Header Details
    tagline = Column(String, nullable=True)
    profile_description = Column(Text, nullable=True)
    about = Column(Text, nullable=True)
    
    # Basic Details
    name = Column(String, index=True, nullable=False)
    age = Column(Integer, index=True, nullable=False)
    gender = Column(String, index=True, nullable=False) # Male, Female
    marital_status = Column(String, index=True, nullable=False) # Never Married, Divorced, Widowed, Awaiting Divorce
    future_children_plans = Column(String, nullable=True)
    health_or_disabilities = Column(String, nullable=True)
    language = Column(String, index=True, nullable=True)
    profile_created_for = Column(String, nullable=True) # Self, Parent, Sibling, Friend
    
    # Marriage Goals
    marriage_goals = Column(Text, nullable=True)
    marriage_plan = Column(Text, nullable=True)
    additional_marriage_plan = Column(Text, nullable=True)
    
    # Media Intros
    voice_intro_url = Column(String, nullable=True)
    video_intro_url = Column(String, nullable=True)
    
    # Contact Details
    primary_no = Column(String, nullable=True)
    secondary_no = Column(String, nullable=True)
    email = Column(String, nullable=True)
    preferred_contact_method = Column(String, nullable=True) # Call, WhatsApp, Email, etc.
    best_time_to_call = Column(String, nullable=True)
    contact_person = Column(String, nullable=True)
    full_address = Column(Text, nullable=True)
    whatsapp_no = Column(String, nullable=True)

    # Education and Profession
    education = Column(String, index=True, nullable=True)
    university_or_college = Column(String, nullable=True)
    profession = Column(String, index=True, nullable=True)
    job_title_or_role = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    job_experience = Column(String, nullable=True)
    profession_type = Column(String, nullable=True) # Full-time, Part-time, Self-employed, Business, Not Working
    annual_income = Column(Float, index=True, nullable=True)
    education_profession_description = Column(Text, nullable=True)

    # Location and Origin
    present_location = Column(String, index=True, nullable=True)
    present_country = Column(String, default="India", index=True)
    present_state = Column(String, nullable=True, index=True)
    residential_location = Column(String, nullable=True)
    willing_to_relocate = Column(String, nullable=True) # Yes, No, Maybe
    home_location = Column(String, nullable=True)
    grew_up_in = Column(String, nullable=True)
    ethnic_background = Column(String, nullable=True)

    # Socio Religious
    religion = Column(String, index=True, nullable=True)
    sect = Column(String, index=True, nullable=True)
    caste = Column(String, index=True, nullable=True)
    sub_caste = Column(String, index=True, nullable=True)
    religiousness = Column(String, nullable=True) # Very religious, Moderately religious, Not religious
    namaz = Column(String, nullable=True) # Always, Frequently, Occasionally, Never
    quran = Column(String, nullable=True) # Daily, Weekly, Rarely, Never
    mahallu_name = Column(String, nullable=True)
    madrasa_edu = Column(String, nullable=True)
    religious_services = Column(String, nullable=True)
    view_on_polygamy = Column(String, nullable=True)
    born_or_reverted = Column(String, nullable=True) # Born Muslim, Reverted, etc.

    # Physical and Appearance
    height = Column(Float, index=True, nullable=True) # in cm
    weight = Column(Float, nullable=True) # in kg
    skin_color = Column(String, nullable=True)
    blood_group = Column(String, nullable=True)
    body_type = Column(String, nullable=True) # Slim, Athletic, Average, Heavy
    hair_color = Column(String, nullable=True)
    hair_type = Column(String, nullable=True)
    facial_color = Column(String, nullable=True)
    eye_color = Column(String, nullable=True)
    eye_wear = Column(String, nullable=True)
    appearance_description = Column(Text, nullable=True)

    # Family and Living
    family_type = Column(String, nullable=True) # Joint, Nuclear
    financial_status = Column(String, nullable=True) # Rich, Upper Middle Class, Middle Class, Lower Middle Class, Poor
    home_type = Column(String, nullable=True)
    living_situation = Column(String, nullable=True)
    father_name = Column(String, nullable=True)
    father_status = Column(String, nullable=True) # Alive, Deceased
    mother_name = Column(String, nullable=True)
    mother_status = Column(String, nullable=True)
    father_occupation = Column(String, nullable=True)
    mother_occupation = Column(String, nullable=True)
    no_elder_brothers = Column(Integer, default=0)
    no_younger_brothers = Column(Integer, default=0)
    no_married_brothers = Column(Integer, default=0)
    no_elder_sisters = Column(Integer, default=0)
    no_younger_sisters = Column(Integer, default=0)
    no_married_sisters = Column(Integer, default=0)
    family_values = Column(String, nullable=True) # Traditional, Moderate, Liberal
    family_origin = Column(String, nullable=True)
    family_details = Column(Text, nullable=True)

    # Interests and Personality
    interests = Column(JSON, nullable=True) # List of interests
    personality = Column(Text, nullable=True)

    # Lifestyle and Preference
    eating_habit = Column(String, nullable=True)
    smoking_habit = Column(String, nullable=True)
    drinking_habit = Column(String, nullable=True)
    pets_details = Column(String, nullable=True)
    favourite_food = Column(String, nullable=True)
    favourite_sports = Column(String, nullable=True)
    favourite_places = Column(String, nullable=True)
    favourite_visited = Column(String, nullable=True)
    favourite_books = Column(String, nullable=True)
    body_art = Column(String, nullable=True)
    cooking = Column(String, nullable=True)
    workout = Column(String, nullable=True)

    # Special Categories (from Matches List requirements)
    differently_abled = Column(Boolean, default=False, index=True)
    orphan_poor_girl = Column(Boolean, default=False, index=True)

    # Partner Preferences
    partner_age_min = Column(Integer, default=18)
    partner_age_max = Column(Integer, default=70)
    partner_height_min = Column(Float, nullable=True)
    partner_height_max = Column(Float, nullable=True)
    partner_religion = Column(JSON, nullable=True) # List of acceptable religions
    partner_caste = Column(JSON, nullable=True) # List of acceptable castes/sects
    partner_sub_caste = Column(JSON, nullable=True) # List of acceptable subcastes
    partner_marital_status = Column(JSON, nullable=True) # List of acceptable statuses
    partner_physical_status = Column(String, nullable=True)
    partner_eating_habit = Column(String, nullable=True)
    partner_smoking_habit = Column(String, nullable=True)
    partner_drinking_habit = Column(String, nullable=True)
    partner_financial_status = Column(String, nullable=True)
    partner_language_known = Column(JSON, nullable=True) # List of languages
    partner_education = Column(String, nullable=True)
    partner_profession = Column(String, nullable=True)
    partner_native_district = Column(String, nullable=True)
    partner_country_pref = Column(JSON, default=lambda: ["All"])
    partner_state_pref = Column(JSON, default=lambda: ["All"])
    partner_expectation = Column(Text, nullable=True)

    # Questionnaires
    questionnaires = Column(JSON, nullable=True) # Format: [{"question": "...", "answer": "...", "options": [...]}]

    # Relationships
    user = relationship("User", back_populates="profile")

    @property
    def photos(self):
        return self.user.photos if self.user else []

class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    url = Column(String, nullable=False)
    is_main = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow) # we need datetime import here

    # Relationships
    user = relationship("User", back_populates="photos")


