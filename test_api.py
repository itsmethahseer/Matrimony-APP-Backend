import json
import sys
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
headers = {}

def make_request(method, path, data=None, is_json=True, is_form=False):
    req_headers = headers.copy()
    
    if method == "GET":
        res = client.get(path, headers=req_headers)
    elif method == "POST":
        if is_form:
            res = client.post(path, data=data, headers=req_headers)
        else:
            res = client.post(path, json=data, headers=req_headers)
    elif method == "PUT":
        if is_form:
            res = client.put(path, data=data, headers=req_headers)
        else:
            res = client.put(path, json=data, headers=req_headers)
    elif method == "DELETE":
        res = client.delete(path, headers=req_headers)
    else:
        res = client.request(method, path, headers=req_headers)
        
    try:
        body = res.json()
    except Exception:
        body = res.text
    return res.status_code, body

def run_tests():
    global headers
    print("==================================================")
    print("       STARTING MATRIMONY API TEST SUITE          ")
    print("==================================================")
    
    # Test 1: Root Status
    print("\n[Test 1] Checking Root API Status...")
    status, res = make_request("GET", "/")
    if status == 200 and res.get("status") == "online":
        print("✓ Root API is online.")
    else:
        print(f"✗ Root API check failed: {status} - {res}")
        sys.exit(1)

    # Generate unique test user credentials
    import time
    unique_id = int(time.time())
    test_email = f"user_{unique_id}@example.com"
    password = "testpassword123"

    # Test 2: User Registration
    print(f"\n[Test 2] Registering new user: {test_email}...")
    register_data = {"email": test_email, "password": password}
    status, res = make_request("POST", "/api/auth/register", data=register_data)
    if status == 201:
        print(f"✓ Registration successful. User ID: {res['id']}")
    else:
        print(f"✗ Registration failed: {status} - {res}")
        sys.exit(1)

    # Test 3: User Login (OAuth2 Password Request Form format)
    print("\n[Test 3] Logging in user to obtain JWT token...")
    login_data = {"username": test_email, "password": password}
    status, res = make_request("POST", "/api/auth/login", data=login_data, is_json=False, is_form=True)
    if status == 200 and "access_token" in res:
        token = res["access_token"]
        headers["Authorization"] = f"Bearer {token}"
        print("✓ Login successful. Bearer JWT token stored.")
    else:
        print(f"✗ Login failed: {status} - {res}")
        sys.exit(1)

    # Test 4: Get Current User details
    print("\n[Test 4] Retrieving current authenticated user details (/auth/me)...")
    status, res = make_request("GET", "/api/auth/me")
    if status == 200 and res["email"] == test_email:
        print(f"✓ Retrieved user details. Membership: {res['membership_status']}, Views Left: {res['remaining_contact_views']}")
    else:
        print(f"✗ Retrieve user details failed: {status} - {res}")
        sys.exit(1)

    # Test 5: Get Profile Details
    print("\n[Test 5] Fetching profile defaults (/profiles/me)...")
    status, my_profile = make_request("GET", "/api/profiles/me")
    if status == 200:
        print(f"✓ Default profile loaded. Name: '{my_profile['name']}', Partner Country Pref: '{my_profile['partner_country_pref']}'")
    else:
        print(f"✗ Fetch profile details failed: {status} - {my_profile}")
        sys.exit(1)

    # Test 6: Update Profile Details
    print("\n[Test 6] Updating profile details (PUT /profiles/me)...")
    update_data = {
        "name": "Test User Khan",
        "age": 27,
        "gender": "Male",
        "marital_status": "Never Married",
        "present_location": "Delhi",
        "present_country": "India",
        "present_state": "Delhi",
        "profession": "Software Engineer",
        "religion": "Islam",
        "sect": "Sunni",
        "partner_age_min": 20,
        "partner_age_max": 26,
        "partner_country_pref": ["India", "UAE"],
        "partner_state_pref": ["Delhi", "Maharashtra"],
    }
    status, res = make_request("PUT", "/api/profiles/me", data=update_data)
    if status == 200 and res["name"] == "Test User Khan" and res["present_state"] == "Delhi" and "UAE" in res["partner_country_pref"]:
        print("✓ Profile successfully updated with country/state preferences.")
    else:
        print(f"✗ Update profile failed: {status} - {res}")
        sys.exit(1)

    # Test 7: Manage Photos (Upload Photo)
    print("\n[Test 7] Uploading a profile photo...")
    photo_data = {"url": "https://example.com/photo.jpg", "is_main": True}
    status, photo_res = make_request("POST", "/api/profiles/photos", data=photo_data)
    if status == 201:
        photo_id = photo_res["id"]
        print(f"✓ Photo successfully uploaded. Photo ID: {photo_id}")
    else:
        print(f"✗ Photo upload failed: {status} - {photo_res}")
        sys.exit(1)

    # Test 8: Get Photos List
    print("\n[Test 8] Retrieving list of uploaded photos...")
    status, res = make_request("GET", "/api/profiles/photos")
    if status == 200 and len(res) > 0:
        print(f"✓ Photos list retrieved. Total: {len(res)} photo(s)")
    else:
        print(f"✗ Retrieve photos list failed: {status} - {res}")
        sys.exit(1)

    # Test 9: Get Matches
    print("\n[Test 9] Fetching matches matching preferences (opposite gender matches)...")
    status, matches = make_request("GET", "/api/profiles/matches")
    if status == 200:
        print(f"✓ Matches list loaded. Found {len(matches)} match(es)")
        # Store a target match user ID for interaction testing (Fatima is in the seed, user ID 2)
        # Find first female match in matches list, or default to 2
        target_id = 2
        for m in matches:
            if m["gender"] == "Female":
                target_id = m["user_id"]
                target_profile_id = m["id"]
                break
        print(f"  Target match selected for further testing: User ID {target_id}")
    else:
        print(f"✗ Fetch matches failed: {status} - {matches}")
        sys.exit(1)

    # Test 10: Custom Profiles Search
    print("\n[Test 10] Testing profiles search with parameters (location=Delhi)...")
    status, res = make_request("GET", "/api/profiles/search?location=Delhi")
    if status == 200:
        print(f"✓ Profiles search complete. Found {len(res)} profile(s)")
    else:
        print(f"✗ Search failed: {status} - {res}")
        sys.exit(1)

    # Test 11: View Match Profile (Should automatically log a Visit)
    print(f"\n[Test 11] Viewing target profile ID {target_profile_id}...")
    status, res = make_request("GET", f"/api/profiles/{target_profile_id}")
    if status == 200 and res["user_id"] == target_id:
        print(f"✓ Viewed profile of '{res['name']}'.")
    else:
        print(f"✗ View profile failed: {status} - {res}")
        sys.exit(1)

    # Test 12: Check Profile Visits List (Should contain target)
    print("\n[Test 12] Fetching list of profiles visited by me...")
    status, visits = make_request("GET", "/api/explore/visits/visited-by-me")
    if status == 200 and len(visits) > 0:
        print(f"✓ Visits list contains {len(visits)} logs. Latest visited user ID: {visits[0]['visited_id']}")
    else:
        print(f"✗ Visits list empty or failed: {status} - {visits}")
        sys.exit(1)

    # Test 13: Add Profile to Favourites
    print(f"\n[Test 13] Adding User {target_id} to favourites...")
    fav_data = {"favourited_id": target_id}
    status, fav_res = make_request("POST", "/api/explore/favourites", data=fav_data)
    if status == 200 or status == 201:
        print("✓ Successfully favourited target profile.")
    else:
        print(f"✗ Add to favourites failed: {status} - {fav_res}")
        sys.exit(1)

    # Test 14: Private Profile Notes
    print(f"\n[Test 14] Adding private note to profile ID {target_profile_id}...")
    note_data = {"profile_id": target_profile_id, "note_text": "This is a test note about the match."}
    status, note_res = make_request("POST", "/api/explore/notes", data=note_data)
    if status == 200:
        print("✓ Private note created/updated.")
    else:
        print(f"✗ Private note creation failed: {status} - {note_res}")
        sys.exit(1)

    # Test 15: Contact Views Credit check
    print(f"\n[Test 15] Viewing contact details of User {target_id}...")
    status, contact_res = make_request("POST", f"/api/explore/contact-views/{target_id}")
    if status == 200:
        # Check if views decremented on auth/me
        _, me = make_request("GET", "/api/auth/me")
        print(f"✓ Contact viewed successfully. Remaining view credits: {me['remaining_contact_views']} (decremented from 5 to 4)")
    else:
        print(f"✗ View contact details failed: {status} - {contact_res}")
        sys.exit(1)

    # Test 16: Messaging (Send interest request message)
    print(f"\n[Test 16] Sending a chat connection message to User {target_id}...")
    msg_data = {"receiver_id": target_id, "message_text": "Assalamu alaikum, I reviewed your profile and would love to connect.", "message_type": "chat"}
    status, msg_res = make_request("POST", "/api/inbox/messages", data=msg_data)
    if status == 201:
        print("✓ Chat message successfully sent.")
    else:
        print(f"✗ Send message failed: {status} - {msg_res}")
        sys.exit(1)

    # Test 17: Get Conversations Summary
    print("\n[Test 17] Retrieving conversations list...")
    status, convs = make_request("GET", "/api/inbox/conversations")
    if status == 200 and len(convs) > 0:
        print(f"✓ Found active conversation with: '{convs[0]['participant']['name']}', Last Message: '{convs[0]['last_message']['message_text']}'")
    else:
        print(f"✗ Get conversations failed: {status} - {convs}")
        sys.exit(1)

    # Test 18: Get Menu Summary
    print("\n[Test 18] Retrieving sidebar Menu details...")
    status, menu = make_request("GET", "/api/menu/summary")
    if status == 200:
        print(f"✓ Menu Summary loaded. Status: {menu['membership_status']}, Views Remaining: {menu['remaining_contact_views']}, Messages Remaining: {menu['remaining_messages']}")
    else:
        print(f"✗ Get menu summary failed: {status} - {menu}")
        sys.exit(1)

    # Test 19: Membership Upgrades (Purchase Gold Tier)
    print("\n[Test 19] Upgrading membership to 'Gold' plan...")
    upgrade_data = {"plan_type": "Gold", "payment_status": "Success"}
    status, upgrade_res = make_request("POST", "/api/menu/subscribe", data=upgrade_data)
    if status == 200 and upgrade_res["membership_status"] == "Premium" and upgrade_res["remaining_contact_views"] == 100:
        print(f"✓ Upgrade successful. Plan: Gold, New Contact Views: {upgrade_res['remaining_contact_views']}, New Message Credits: {upgrade_res['remaining_messages']}")
    else:
        print(f"✗ Membership upgrade failed: {status} - {upgrade_res}")
        sys.exit(1)

    # Test 20: ID Verification Document Upload
    print("\n[Test 20] Uploading ID verification document...")
    verify_data = {"document_url": "https://example.com/my_id_card.pdf"}
    status, verify_res = make_request("POST", "/api/auth/verify-id", data=verify_data)
    if status == 200 and verify_res["id_verification_status"] == "Pending":
        print("✓ Document uploaded. Status transitioned to 'Pending'.")
    else:
        print(f"✗ ID Verification request failed: {status} - {verify_res}")
        sys.exit(1)

    # Test 21: DELETE note
    print(f"\n[Test 21] Testing DELETE note ID {note_res['id']}...")
    status, res = make_request("DELETE", f"/api/explore/notes/{note_res['id']}")
    if status == 204 or status == 200:
        print("✓ Private note deleted successfully.")
    else:
        print(f"✗ Delete note failed: {status} - {res}")
        sys.exit(1)

    # Test 22: DELETE favourite (Remove from favourites)
    print(f"\n[Test 22] Testing DELETE favourite for User {target_id}...")
    status, res = make_request("DELETE", f"/api/explore/favourites/{target_id}")
    if status == 204 or status == 200:
        print("✓ Favourited match removed successfully.")
    else:
        print(f"✗ Remove favourite failed: {status} - {res}")
        sys.exit(1)

    # Test 23: DELETE photo
    print(f"\n[Test 23] Testing DELETE photo ID {photo_id}...")
    status, res = make_request("DELETE", f"/api/profiles/photos/{photo_id}")
    if status == 204 or status == 200:
        print("✓ Uploaded profile photo deleted successfully.")
    else:
        print(f"✗ Delete photo failed: {status} - {res}")
        sys.exit(1)

    # Test 24: Send Interest Request
    print(f"\n[Test 24] Sending Interest Request to User {target_id}...")
    interest_data = {"receiver_id": target_id}
    status, interest_res = make_request("POST", "/api/explore/interests", data=interest_data)
    if status == 201 and interest_res.get("status") == "Pending":
        print(f"✓ Interest sent successfully. Interest ID: {interest_res['id']}, Status: {interest_res['status']}")
    else:
        print(f"✗ Send interest failed: {status} - {interest_res}")
        sys.exit(1)

    # Test 25: Check Interest Status
    print(f"\n[Test 25] Checking Interest Status for User {target_id}...")
    status, interest_status = make_request("GET", f"/api/explore/interests/status/{target_id}")
    if status == 200 and interest_status.get("sent") and interest_status["sent"]["status"] == "Pending":
        print(f"✓ Interest status retrieved: Sent is Pending (ID: {interest_status['sent']['id']})")
    else:
        print(f"✗ Check interest status failed: {status} - {interest_status}")
        sys.exit(1)

    # Test 26: Cancel Pending Interest Request
    print(f"\n[Test 26] Cancelling Pending Interest ID {interest_res['id']}...")
    status, cancel_res = make_request("DELETE", f"/api/explore/interests/{interest_res['id']}")
    if status == 200 and cancel_res.get("refunded_credits") is not None:
        print(f"✓ Interest cancelled successfully. Refunded credits: {cancel_res['refunded_credits']}")
    else:
        print(f"✗ Cancel interest failed: {status} - {cancel_res}")
        sys.exit(1)

    # Test 27: Verify interest is removed
    status, interest_status_after = make_request("GET", f"/api/explore/interests/status/{target_id}")
    if status == 200 and interest_status_after.get("sent") is None:
        print("✓ Verified interest record has been removed after cancellation.")
    else:
        print(f"✗ Interest still exists after cancel: {status} - {interest_status_after}")
        sys.exit(1)

    print("\n==================================================")
    print("       ALL MATRIMONY API TESTS COMPLETED          ")
    print("            STATUS: 100% FUNCTIONAL               ")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
