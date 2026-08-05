from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import datetime

class PhotoBase(BaseModel):
    url: str
    is_main: bool = False

class PhotoCreate(PhotoBase):
    pass

class PhotoResponse(PhotoBase):
    id: int
    user_id: int
    is_approved: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Individual Section Schemas for modular updates
class BasicDetailsUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    future_children_plans: Optional[str] = None
    health_or_disabilities: Optional[str] = None
    language: Optional[str] = None
    profile_created_for: Optional[str] = None
    marriage_goals: Optional[str] = None
    marriage_plan: Optional[str] = None
    additional_marriage_plan: Optional[str] = None
    voice_intro_url: Optional[str] = None
    video_intro_url: Optional[str] = None

class ContactDetailsUpdate(BaseModel):
    primary_no: Optional[str] = None
    secondary_no: Optional[str] = None
    email: Optional[str] = None
    preferred_contact_method: Optional[str] = None
    best_time_to_call: Optional[str] = None
    contact_person: Optional[str] = None
    full_address: Optional[str] = None
    whatsapp_no: Optional[str] = None

class EducationProfessionUpdate(BaseModel):
    education: Optional[str] = None
    university_or_college: Optional[str] = None
    profession: Optional[str] = None
    job_title_or_role: Optional[str] = None
    company_name: Optional[str] = None
    job_experience: Optional[str] = None
    profession_type: Optional[str] = None
    annual_income: Optional[float] = None
    education_profession_description: Optional[str] = None

class LocationOriginUpdate(BaseModel):
    present_location: Optional[str] = None
    present_country: Optional[str] = None
    present_state: Optional[str] = None
    residential_location: Optional[str] = None
    willing_to_relocate: Optional[str] = None
    home_location: Optional[str] = None
    grew_up_in: Optional[str] = None
    ethnic_background: Optional[str] = None

class SocioReligiousUpdate(BaseModel):
    religion: Optional[str] = None
    sect: Optional[str] = None
    caste: Optional[str] = None
    sub_caste: Optional[str] = None
    religiousness: Optional[str] = None
    namaz: Optional[str] = None
    quran: Optional[str] = None
    mahallu_name: Optional[str] = None
    madrasa_edu: Optional[str] = None
    religious_services: Optional[str] = None
    view_on_polygamy: Optional[str] = None
    born_or_reverted: Optional[str] = None

class PhysicalAppearanceUpdate(BaseModel):
    height: Optional[float] = None
    weight: Optional[float] = None
    skin_color: Optional[str] = None
    blood_group: Optional[str] = None
    body_type: Optional[str] = None
    hair_color: Optional[str] = None
    hair_type: Optional[str] = None
    facial_color: Optional[str] = None
    eye_color: Optional[str] = None
    eye_wear: Optional[str] = None
    appearance_description: Optional[str] = None

class FamilyLivingUpdate(BaseModel):
    family_type: Optional[str] = None
    financial_status: Optional[str] = None
    home_type: Optional[str] = None
    living_situation: Optional[str] = None
    father_name: Optional[str] = None
    father_status: Optional[str] = None
    mother_name: Optional[str] = None
    mother_status: Optional[str] = None
    father_occupation: Optional[str] = None
    mother_occupation: Optional[str] = None
    no_elder_brothers: Optional[int] = 0
    no_younger_brothers: Optional[int] = 0
    no_married_brothers: Optional[int] = 0
    no_elder_sisters: Optional[int] = 0
    no_younger_sisters: Optional[int] = 0
    no_married_sisters: Optional[int] = 0
    family_values: Optional[str] = None
    family_origin: Optional[str] = None
    family_details: Optional[str] = None

class LifestylePreferenceUpdate(BaseModel):
    eating_habit: Optional[str] = None
    smoking_habit: Optional[str] = None
    drinking_habit: Optional[str] = None
    pets_details: Optional[str] = None
    favourite_food: Optional[str] = None
    favourite_sports: Optional[str] = None
    favourite_places: Optional[str] = None
    favourite_visited: Optional[str] = None
    favourite_books: Optional[str] = None
    body_art: Optional[str] = None
    cooking: Optional[str] = None
    workout: Optional[str] = None

class PartnerPreferencesUpdate(BaseModel):
    partner_age_min: Optional[int] = 18
    partner_age_max: Optional[int] = 70
    partner_height_min: Optional[float] = None
    partner_height_max: Optional[float] = None
    partner_religion: Optional[List[str]] = None
    partner_caste: Optional[List[str]] = None
    partner_sub_caste: Optional[List[str]] = None
    partner_marital_status: Optional[List[str]] = None
    partner_physical_status: Optional[str] = None
    partner_eating_habit: Optional[str] = None
    partner_smoking_habit: Optional[str] = None
    partner_drinking_habit: Optional[str] = None
    partner_financial_status: Optional[str] = None
    partner_language_known: Optional[List[str]] = None
    partner_education: Optional[str] = None
    partner_profession: Optional[str] = None
    partner_native_district: Optional[str] = None
    partner_country_pref: Optional[List[str]] = ["All"]
    partner_state_pref: Optional[List[str]] = ["All"]
    partner_expectation: Optional[str] = None

class QuestionnaireItem(BaseModel):
    question: str
    answer: str
    options: Optional[List[str]] = None

class ProfileCreate(BaseModel):
    name: str
    age: int
    gender: str
    marital_status: str
    differently_abled: Optional[bool] = False
    orphan_poor_girl: Optional[bool] = False

class ProfileUpdate(BaseModel):
    tagline: Optional[str] = None
    profile_description: Optional[str] = None
    about: Optional[str] = None
    
    # Basic
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    future_children_plans: Optional[str] = None
    health_or_disabilities: Optional[str] = None
    language: Optional[str] = None
    profile_created_for: Optional[str] = None
    marriage_goals: Optional[str] = None
    marriage_plan: Optional[str] = None
    additional_marriage_plan: Optional[str] = None
    voice_intro_url: Optional[str] = None
    video_intro_url: Optional[str] = None

    # Contact
    primary_no: Optional[str] = None
    secondary_no: Optional[str] = None
    email: Optional[str] = None
    preferred_contact_method: Optional[str] = None
    best_time_to_call: Optional[str] = None
    contact_person: Optional[str] = None
    full_address: Optional[str] = None
    whatsapp_no: Optional[str] = None

    # Education/Profession
    education: Optional[str] = None
    university_or_college: Optional[str] = None
    profession: Optional[str] = None
    job_title_or_role: Optional[str] = None
    company_name: Optional[str] = None
    job_experience: Optional[str] = None
    profession_type: Optional[str] = None
    annual_income: Optional[float] = None
    education_profession_description: Optional[str] = None

    # Location
    present_location: Optional[str] = None
    present_country: Optional[str] = None
    present_state: Optional[str] = None
    residential_location: Optional[str] = None
    willing_to_relocate: Optional[str] = None
    home_location: Optional[str] = None
    grew_up_in: Optional[str] = None
    ethnic_background: Optional[str] = None

    # Socio-religious
    religion: Optional[str] = None
    sect: Optional[str] = None
    caste: Optional[str] = None
    sub_caste: Optional[str] = None
    religiousness: Optional[str] = None
    namaz: Optional[str] = None
    quran: Optional[str] = None
    mahallu_name: Optional[str] = None
    madrasa_edu: Optional[str] = None
    religious_services: Optional[str] = None
    view_on_polygamy: Optional[str] = None
    born_or_reverted: Optional[str] = None

    # Physical
    height: Optional[float] = None
    weight: Optional[float] = None
    skin_color: Optional[str] = None
    blood_group: Optional[str] = None
    body_type: Optional[str] = None
    hair_color: Optional[str] = None
    hair_type: Optional[str] = None
    facial_color: Optional[str] = None
    eye_color: Optional[str] = None
    eye_wear: Optional[str] = None
    appearance_description: Optional[str] = None

    # Family
    family_type: Optional[str] = None
    financial_status: Optional[str] = None
    home_type: Optional[str] = None
    living_situation: Optional[str] = None
    father_name: Optional[str] = None
    father_status: Optional[str] = None
    mother_name: Optional[str] = None
    mother_status: Optional[str] = None
    father_occupation: Optional[str] = None
    mother_occupation: Optional[str] = None
    no_elder_brothers: Optional[int] = None
    no_younger_brothers: Optional[int] = None
    no_married_brothers: Optional[int] = None
    no_elder_sisters: Optional[int] = None
    no_younger_sisters: Optional[int] = None
    no_married_sisters: Optional[int] = None
    family_values: Optional[str] = None
    family_origin: Optional[str] = None
    family_details: Optional[str] = None

    # Interests/Lifestyle/Special
    interests: Optional[List[str]] = None
    personality: Optional[str] = None
    eating_habit: Optional[str] = None
    smoking_habit: Optional[str] = None
    drinking_habit: Optional[str] = None
    pets_details: Optional[str] = None
    favourite_food: Optional[str] = None
    favourite_sports: Optional[str] = None
    favourite_places: Optional[str] = None
    favourite_visited: Optional[str] = None
    favourite_books: Optional[str] = None
    body_art: Optional[str] = None
    cooking: Optional[str] = None
    workout: Optional[str] = None
    differently_abled: Optional[bool] = None
    orphan_poor_girl: Optional[bool] = None

    # Partner Prefs
    partner_age_min: Optional[int] = None
    partner_age_max: Optional[int] = None
    partner_height_min: Optional[float] = None
    partner_height_max: Optional[float] = None
    partner_religion: Optional[List[str]] = None
    partner_caste: Optional[List[str]] = None
    partner_sub_caste: Optional[List[str]] = None
    partner_marital_status: Optional[List[str]] = None
    partner_physical_status: Optional[str] = None
    partner_eating_habit: Optional[str] = None
    partner_smoking_habit: Optional[str] = None
    partner_drinking_habit: Optional[str] = None
    partner_financial_status: Optional[str] = None
    partner_language_known: Optional[List[str]] = None
    partner_education: Optional[str] = None
    partner_profession: Optional[str] = None
    partner_native_district: Optional[str] = None
    partner_country_pref: Optional[List[str]] = None
    partner_state_pref: Optional[List[str]] = None
    partner_expectation: Optional[str] = None

    # Questionnaires
    questionnaires: Optional[List[QuestionnaireItem]] = None

class ProfileResponse(BaseModel):
    id: int
    user_id: int
    
    tagline: Optional[str] = None
    profile_description: Optional[str] = None
    about: Optional[str] = None

    # Basic
    name: str
    age: int
    gender: str
    marital_status: str
    future_children_plans: Optional[str] = None
    health_or_disabilities: Optional[str] = None
    language: Optional[str] = None
    profile_created_for: Optional[str] = None
    marriage_goals: Optional[str] = None
    marriage_plan: Optional[str] = None
    additional_marriage_plan: Optional[str] = None
    voice_intro_url: Optional[str] = None
    video_intro_url: Optional[str] = None

    # Contact (Only visible to certain matches / after view checks)
    primary_no: Optional[str] = None
    secondary_no: Optional[str] = None
    email: Optional[str] = None
    preferred_contact_method: Optional[str] = None
    best_time_to_call: Optional[str] = None
    contact_person: Optional[str] = None
    full_address: Optional[str] = None
    whatsapp_no: Optional[str] = None

    # Education/Profession
    education: Optional[str] = None
    university_or_college: Optional[str] = None
    profession: Optional[str] = None
    job_title_or_role: Optional[str] = None
    company_name: Optional[str] = None
    job_experience: Optional[str] = None
    profession_type: Optional[str] = None
    annual_income: Optional[float] = None
    education_profession_description: Optional[str] = None

    # Location
    present_location: Optional[str] = None
    present_country: Optional[str] = "India"
    present_state: Optional[str] = None
    residential_location: Optional[str] = None
    willing_to_relocate: Optional[str] = None
    home_location: Optional[str] = None
    grew_up_in: Optional[str] = None
    ethnic_background: Optional[str] = None

    # Socio-religious
    religion: Optional[str] = None
    sect: Optional[str] = None
    caste: Optional[str] = None
    sub_caste: Optional[str] = None
    religiousness: Optional[str] = None
    namaz: Optional[str] = None
    quran: Optional[str] = None
    mahallu_name: Optional[str] = None
    madrasa_edu: Optional[str] = None
    religious_services: Optional[str] = None
    view_on_polygamy: Optional[str] = None
    born_or_reverted: Optional[str] = None

    # Physical
    height: Optional[float] = None
    weight: Optional[float] = None
    skin_color: Optional[str] = None
    blood_group: Optional[str] = None
    body_type: Optional[str] = None
    hair_color: Optional[str] = None
    hair_type: Optional[str] = None
    facial_color: Optional[str] = None
    eye_color: Optional[str] = None
    eye_wear: Optional[str] = None
    appearance_description: Optional[str] = None

    # Family
    family_type: Optional[str] = None
    financial_status: Optional[str] = None
    home_type: Optional[str] = None
    living_situation: Optional[str] = None
    father_name: Optional[str] = None
    father_status: Optional[str] = None
    mother_name: Optional[str] = None
    mother_status: Optional[str] = None
    father_occupation: Optional[str] = None
    mother_occupation: Optional[str] = None
    no_elder_brothers: int
    no_younger_brothers: int
    no_married_brothers: int
    no_elder_sisters: int
    no_younger_sisters: int
    no_married_sisters: int
    family_values: Optional[str] = None
    family_origin: Optional[str] = None
    family_details: Optional[str] = None

    # Interests/Lifestyle/Special
    interests: Optional[List[str]] = None
    personality: Optional[str] = None
    eating_habit: Optional[str] = None
    smoking_habit: Optional[str] = None
    drinking_habit: Optional[str] = None
    pets_details: Optional[str] = None
    favourite_food: Optional[str] = None
    favourite_sports: Optional[str] = None
    favourite_places: Optional[str] = None
    favourite_visited: Optional[str] = None
    favourite_books: Optional[str] = None
    body_art: Optional[str] = None
    cooking: Optional[str] = None
    workout: Optional[str] = None
    differently_abled: bool
    orphan_poor_girl: bool

    # Partner Preferences
    partner_age_min: int
    partner_age_max: int
    partner_height_min: Optional[float] = None
    partner_height_max: Optional[float] = None
    partner_religion: Optional[List[str]] = None
    partner_caste: Optional[List[str]] = None
    partner_sub_caste: Optional[List[str]] = None
    partner_marital_status: Optional[List[str]] = None
    partner_physical_status: Optional[str] = None
    partner_eating_habit: Optional[str] = None
    partner_smoking_habit: Optional[str] = None
    partner_drinking_habit: Optional[str] = None
    partner_financial_status: Optional[str] = None
    partner_language_known: Optional[List[str]] = None
    partner_education: Optional[str] = None
    partner_profession: Optional[str] = None
    partner_native_district: Optional[str] = None
    partner_country_pref: Optional[List[str]] = ["All"]
    partner_state_pref: Optional[List[str]] = ["All"]
    partner_expectation: Optional[str] = None

    # Questionnaires
    questionnaires: Optional[List[QuestionnaireItem]] = None

    photos: Optional[List[PhotoResponse]] = None

    class Config:
        from_attributes = True
