import uuid
import json
import difflib
from datetime import datetime

# In-memory databases
users = []
items = []
current_user = None


def register():
    print("\n--- Register New User ---")
    username = input("Username: ").strip()
    if any(u['username'] == username for u in users):
        print("❌ Username already taken.")
        return
    password = input("Password: ").strip()
    user = {"id": str(uuid.uuid4()), "username": username, "password": password}
    users.append(user)
    print("✅ Registration successful!")

def login():
    global current_user
    print("\n--- Login ---")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    user = next((u for u in users if u['username'] == username and u['password'] == password), None)
    if user:
        current_user = user
        print(f"✅ Logged in as {current_user['username']}")
    else:
        print("❌ Invalid username or password.")

def require_login():
    if not current_user:
        print("❌ You must be logged in to perform this action.")
        return False
    return True

# --------- Item Reporting ---------

def input_item():
    if not require_login(): return
    print("\n--- Report an Item ---")
    item = {
        "id": str(uuid.uuid4()),
        "type": input("Type (lost/found): ").strip().lower(),
        "title": input("Title: "),
        "description": input("Description: "),
        "category": input("Category (e.g., wallet, phone, pet): "),
        "date": input("Date (YYYY-MM-DD): "),
        "location": input("Location: "),
        "reportedBy": current_user['username'],
        "status": "open"
    }
    items.append(item)
    print("✅ Item reported!\n")

def find_matches(lost_item):
    matches = []
    for item in items:
        if item["type"] == "found" and item["category"].lower() == lost_item["category"].lower():
            date_diff = abs((datetime.strptime(lost_item["date"], "%Y-%m-%d") - datetime.strptime(item["date"], "%Y-%m-%d")).days)
            similarity = difflib.SequenceMatcher(None, lost_item["description"].lower(), item["description"].lower()).ratio()
            if date_diff <= 7 and similarity > 0.4:
                matches.append((similarity, item))
    return sorted(matches, reverse=True)

def list_items():
    print("\n--- All Items ---")
    for item in items:
        print(f"{item['id']} | {item['type'].upper()} | {item['title']} | {item['date']} | {item['location']} | by {item['reportedBy']}")

def match_by_id():
    if not require_login(): return
    item_id = input("Enter lost item ID to find matches: ").strip()
    lost_item = next((i for i in items if i["id"] == item_id and i["type"] == "lost" and i["reportedBy"] == current_user['username']), None)
    if not lost_item:
        print("❌ Lost item not found or not yours.")
        return
    matches = find_matches(lost_item)
    print(f"\n🔍 Matches for: {lost_item['title']}")
    if not matches:
        print("No matches found.")
        return
    for score, match in matches:
        print(f"- Found: {match['title']} ({match['location']}) | Score: {round(score, 2)} | by {match['reportedBy']}")

# --------- CLI Menu ---------

def main_menu():
    while True:
        print("\n📋 Main Menu")
        if current_user:
            print(f"👤 Logged in as: {current_user['username']}")
            print("1. Report lost/found item")
            print("2. List all items")
            print("3. Match my lost item")
            print("4. Logout")
        else:
            print("1. Register")
            print("2. Login")

        print("0. Exit")
        choice = input("Choose an option: ")

        if current_user:
            if choice == "1":
                input_item()
            elif choice == "2":
                list_items()
            elif choice == "3":
                match_by_id()
            elif choice == "4":
                global current_user
                print(f"👋 Logged out from {current_user['username']}")
                current_user = None
            elif choice == "0":
                break
            else:
                print("❌ Invalid choice.")
        else:
            if choice == "1":
                register()
            elif choice == "2":
                login()
            elif choice == "0":
                break
            else:
                print("❌ Invalid choice.")

if __name__ == "__main__":
    main_menu()
