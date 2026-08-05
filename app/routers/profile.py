from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from typing import List, Optional
import datetime

from app.database import get_db
from app.models.user import User
from app.models.profile import Profile, Photo
from app.models.interaction import ProfileVisit, Block
from app.schemas.profile import ProfileResponse, ProfileUpdate, PhotoResponse, PhotoCreate
from app.utils.deps import get_current_user

router = APIRouter(prefix="/profiles", tags=["Profiles"])

@router.get("/me", response_model=ProfileResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.put("/me", response_model=ProfileResponse)
def update_my_profile(
    profile_in: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
        
    db.commit()
    db.refresh(profile)
    return profile

@router.get("/matches", response_model=List[ProfileResponse])
def get_matches(
    category: Optional[str] = Query(None, description="Category of matches: my_matches, new_matches, location, profession, differently_abled, orphan_poor_girls"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Ensure current user has a profile
    my_profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not my_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Get list of blocked user IDs (both blocked by current user and those who blocked current user)
    blocked_ids = db.query(Block.blocked_id).filter(Block.blocker_id == current_user.id).all()
    blocked_by_ids = db.query(Block.blocker_id).filter(Block.blocked_id == current_user.id).all()
    exclude_ids = [current_user.id] + [b[0] for b in blocked_ids] + [b[0] for b in blocked_by_ids]

    # Base query: matching opposite gender and excluding self/blocked profiles
    opposite_gender = "Female" if my_profile.gender == "Male" else "Male"
    query = db.query(Profile).filter(
        Profile.gender == opposite_gender,
        Profile.user_id.notin_(exclude_ids)
    )

    if category == "new_matches":
        # Matches registered in the last 7 days
        seven_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        query = query.join(User).filter(User.created_at >= seven_days_ago).order_by(desc(User.created_at))
        
    elif category == "location":
        # Same present location
        if my_profile.present_location:
            query = query.filter(Profile.present_location.ilike(f"%{my_profile.present_location}%"))
            
    elif category == "profession":
        # Same profession
        if my_profile.profession:
            query = query.filter(Profile.profession.ilike(f"%{my_profile.profession}%"))
            
    elif category == "differently_abled":
        # Filter differently abled
        query = query.filter(Profile.differently_abled == True)
        
    elif category == "orphan_poor_girls":
        # Filter orphan/poor girls
        query = query.filter(Profile.orphan_poor_girl == True)
        
    else:
        # Default algorithm: Partner Preferences matching
        # 1. Partner Religion Preference
        rel_pref = my_profile.partner_religion
        if rel_pref and isinstance(rel_pref, list) and len(rel_pref) > 0 and "Any" not in rel_pref and "All" not in rel_pref:
            query = query.filter(Profile.religion.in_(rel_pref))
        elif my_profile.religion:
            query = query.filter(Profile.religion == my_profile.religion)

        # 2. Partner Caste / Sect Preference
        caste_pref = my_profile.partner_caste
        if caste_pref and isinstance(caste_pref, list) and len(caste_pref) > 0 and "Any" not in caste_pref and "All" not in caste_pref and "Open to All" not in caste_pref:
            query = query.filter(or_(Profile.caste.in_(caste_pref), Profile.sect.in_(caste_pref)))

        # 3. Partner Sub-Caste Preference
        sub_caste_pref = my_profile.partner_sub_caste
        if sub_caste_pref and isinstance(sub_caste_pref, list) and len(sub_caste_pref) > 0 and "Any" not in sub_caste_pref and "All" not in sub_caste_pref:
            query = query.filter(Profile.sub_caste.in_(sub_caste_pref))

        # 4. Partner Marital Status Preference
        marital_pref = my_profile.partner_marital_status
        if marital_pref and isinstance(marital_pref, list) and len(marital_pref) > 0 and "Any" not in marital_pref and "All" not in marital_pref:
            query = query.filter(Profile.marital_status.in_(marital_pref))

        # 5. Age & Height Filters
        if my_profile.partner_age_min:
            query = query.filter(Profile.age >= my_profile.partner_age_min)
        if my_profile.partner_age_max:
            query = query.filter(Profile.age <= my_profile.partner_age_max)
        if my_profile.partner_height_min:
            query = query.filter(Profile.height >= my_profile.partner_height_min)
        if my_profile.partner_height_max:
            query = query.filter(Profile.height <= my_profile.partner_height_max)

    results = query.limit(50).all()

    # Fallback if category filter yields fewer than 3 profiles: fetch opposite gender profiles
    if len(results) < 3:
        fallback_query = db.query(Profile).filter(
            Profile.gender == opposite_gender,
            Profile.user_id.notin_(exclude_ids)
        ).order_by(desc(Profile.id)).limit(50)
        return fallback_query.all()

    return results

@router.get("/search", response_model=List[ProfileResponse])
def search_profiles(
    gender: Optional[str] = Query(None),
    age_min: Optional[int] = Query(None),
    age_max: Optional[int] = Query(None),
    religion: Optional[str] = Query(None),
    sect: Optional[str] = Query(None),
    marital_status: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    profession: Optional[str] = Query(None),
    differently_abled: Optional[bool] = Query(None),
    orphan_poor_girl: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    blocked_ids = db.query(Block.blocked_id).filter(Block.blocker_id == current_user.id).all()
    blocked_by_ids = db.query(Block.blocker_id).filter(Block.blocked_id == current_user.id).all()
    exclude_ids = [current_user.id] + [b[0] for b in blocked_ids] + [b[0] for b in blocked_by_ids]

    query = db.query(Profile).filter(Profile.user_id.notin_(exclude_ids))

    if gender:
        query = query.filter(Profile.gender == gender)
    if age_min:
        query = query.filter(Profile.age >= age_min)
    if age_max:
        query = query.filter(Profile.age <= age_max)
    if religion:
        query = query.filter(Profile.religion.ilike(f"%{religion}%"))
    if sect:
        query = query.filter(Profile.sect.ilike(f"%{sect}%"))
    if marital_status:
        query = query.filter(Profile.marital_status == marital_status)
    if location:
        query = query.filter(
            or_(
                Profile.present_location.ilike(f"%{location}%"),
                Profile.residential_location.ilike(f"%{location}%"),
                Profile.home_location.ilike(f"%{location}%")
            )
        )
    if country:
        query = query.filter(Profile.present_country == country)
    if state:
        query = query.filter(Profile.present_state == state)
    if profession:
        query = query.filter(Profile.profession.ilike(f"%{profession}%"))
    if differently_abled is not None:
        query = query.filter(Profile.differently_abled == differently_abled)
    if orphan_poor_girl is not None:
        query = query.filter(Profile.orphan_poor_girl == orphan_poor_girl)

    return query.limit(100).all()

# Photo Management (Defined before /{profile_id} to prevent path conflicts)
@router.post("/photos", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
def add_photo(
    photo_in: PhotoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # If this photo is set as main, unset any other main photos
    if photo_in.is_main:
        db.query(Photo).filter(Photo.user_id == current_user.id).update({"is_main": False})
        
    # By default, photo approval requires admin. Let's default to True for mock verification purposes.
    photo = Photo(
        user_id=current_user.id,
        url=photo_in.url,
        is_main=photo_in.is_main,
        is_approved=True 
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo

@router.get("/photos", response_model=List[PhotoResponse])
def get_my_photos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Photo).filter(Photo.user_id == current_user.id).all()

@router.put("/photos/{photo_id}/set-main", response_model=PhotoResponse)
def set_main_photo(
    photo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    target_photo = db.query(Photo).filter(Photo.id == photo_id, Photo.user_id == current_user.id).first()
    if not target_photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    # Unset all other main photos for this user
    db.query(Photo).filter(Photo.user_id == current_user.id).update({"is_main": False})
    
    # Set selected photo as main
    target_photo.is_main = True
    db.commit()
    db.refresh(target_photo)
    return target_photo

@router.delete("/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_photo(
    photo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    photo = db.query(Photo).filter(Photo.id == photo_id, Photo.user_id == current_user.id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
        
    db.delete(photo)
    db.commit()
    return None

@router.get("/{profile_id}", response_model=ProfileResponse)
def get_profile_by_id(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    # Check if blocked
    blocked = db.query(Block).filter(
        or_(
            and_(Block.blocker_id == current_user.id, Block.blocked_id == profile.user_id),
            and_(Block.blocker_id == profile.user_id, Block.blocked_id == current_user.id)
        )
    ).first()
    if blocked:
        raise HTTPException(status_code=403, detail="Access denied. Profile is blocked.")
        
    # Log profile visit (do not log self-visits)
    if profile.user_id != current_user.id:
        visit = ProfileVisit(visitor_id=current_user.id, visited_id=profile.user_id)
        db.add(visit)
        db.commit()
        
    return profile
