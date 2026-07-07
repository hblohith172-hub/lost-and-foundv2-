import uuid
import os
import shutil
from datetime import datetime
from models import Item, User, Database
from utils import validate_email, validate_phone, hash_password, check_password


def post_item(db, current_user):
    """Prompt user for item details and save to database."""
    print("\n--- Post New Item ---")
    title = input("Title: ").strip()
    description = input("Description: ").strip()
    category = input("Category (electronics/clothing/documents/other): ").strip().lower()
    location = input("Location where lost/found: ").strip()

    item = Item(
        item_id=str(uuid.uuid4())[:8],
        title=title,
        description=description,
        category=category,
        location=location,
        date_posted=datetime.now().isoformat(),
        status="lost",
        image_path=None,
        posted_by=current_user
    )

    item.image_path = _handle_image_upload(db, item.item_id)

    items = db.load_items()
    items.append(item)
    db.save_items(items)
    print(f"Item posted successfully! ID: {item.item_id}")
    return item


def view_all_items(db):
    """Display all items in the database."""
    items = db.load_items()
    if not items:
        print("\nNo items found.")
        return

    print("\n" + "=" * 60)
    print(f"{'ID':<10}{'Title':<20}{'Category':<15}{'Status':<10}{'Location'}")
    print("-" * 60)
    for item in items:
        print(f"{item.item_id:<10}{item.title:<20}{item.category:<15}"
              f"{item.status:<10}{item.location}")
    print("=" * 60)


def _handle_image_upload(db, item_id):
    """Prompt user for image path, copy to data/images/, return saved path."""
    image_path = input("Enter image file path (or press Enter to skip): ").strip()
    if not image_path:
        return None

    if not os.path.exists(image_path):
        print("File not found. Skipping image upload.")
        return None

    ext = os.path.splitext(image_path)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.gif']:
        print("Unsupported file type. Use .jpg, .jpeg, .png, or .gif")
        return None

    dest_dir = os.path.join(db.data_dir, "images")
    dest_filename = f"{item_id}{ext}"
    dest_path = os.path.join(dest_dir, dest_filename)

    try:
        shutil.copy2(image_path, dest_path)
        print(f"Image saved: {dest_path}")
        return dest_path
    except Exception as e:
        print(f"Error saving image: {e}")
        return None


def search_items(db):
    """Search items by keyword, category, or location."""
    print("\n--- Search Items ---")
    print("1. Search by keyword")
    print("2. Search by category")
    print("3. Search by location")
    choice = input("Choice: ").strip()

    items = db.load_items()
    results = []

    if choice == "1":
        keyword = input("Enter keyword: ").strip().lower()
        results = [i for i in items if keyword in i.title.lower()
                   or keyword in i.description.lower()]
    elif choice == "2":
        category = input("Enter category: ").strip().lower()
        results = [i for i in items if i.category.lower() == category]
    elif choice == "3":
        location = input("Enter location: ").strip().lower()
        results = [i for i in items if location in i.location.lower()]
    else:
        print("Invalid choice.")
        return

    if not results:
        print("No matching items found.")
        return

    print(f"\nFound {len(results)} item(s):")
    for item in results:
        print(f"  [{item.item_id}] {item.title} — {item.status}")


def update_status(db):
    """Update the status of an existing item."""
    print("\n--- Update Item Status ---")
    item_id = input("Enter item ID: ").strip()

    items = db.load_items()
    for item in items:
        if item.item_id == item_id:
            print(f"Current status: {item.status}")
            print("1. lost\n2. found\n3. resolved")
            new_status = input("New status: ").strip()
            status_map = {"1": "lost", "2": "found", "3": "resolved"}
            if new_status in status_map:
                item.status = status_map[new_status]
                db.save_items(items)
                print(f"Status updated to '{item.status}'")
                return
            else:
                print("Invalid status.")
                return
    print("Item not found.")


def register_user(db):
    """Register a new user."""
    print("\n--- Register ---")
    username = input("Username: ").strip()
    email = input("Email: ").strip()
    phone = input("Phone: ").strip()
    password = input("Password: ").strip()

    if not validate_email(email):
        print("Invalid email.")
        return None
    if not validate_phone(phone):
        print("Invalid phone number.")
        return None

    users = db.load_users()
    if any(u.email == email for u in users):
        print("Email already registered.")
        return None

    user = User(
        user_id=str(uuid.uuid4())[:8],
        username=username,
        email=email,
        phone=phone,
        password_hash=hash_password(password)
    )
    users.append(user)
    db.save_users(users)
    print("Registration successful!")
    return user


def login_user(db):
    """Log in an existing user."""
    print("\n--- Login ---")
    email = input("Email: ").strip()
    password = input("Password: ").strip()

    users = db.load_users()
    for user in users:
        if user.email == email and check_password(password, user.password_hash):
            print(f"Welcome, {user.username}!")
            return user
    print("Invalid credentials.")
    return None


def login_menu(db):
    """Display login/register menu and return logged-in user."""
    while True:
        print("\n1. Login\n2. Register\n3. Continue as guest")
        choice = input("Choice: ").strip()
        if choice == "1":
            user = login_user(db)
            if user:
                return user
        elif choice == "2":
            user = register_user(db)
            if user:
                return user
        elif choice == "3":
            return None
        else:
            print("Invalid choice.")


def contact_owner(db):
    """Display contact info of the item's owner."""
    print("\n--- Contact Owner ---")
    item_id = input("Enter item ID: ").strip()

    items = db.load_items()
    users = db.load_users()

    for item in items:
        if item.item_id == item_id:
            for user in users:
                if user.user_id == item.posted_by:
                    print(f"\nPosted by: {user.username}")
                    print(f"Email: {user.email}")
                    print(f"Phone: {user.phone}")
                    return
            print("Owner details not found.")
            return
    print("Item not found.")


def main():
    db = Database()
    print("=" * 40)
    print("   LOST & FOUND ITEM TRACKER")
    print("=" * 40)
    
    current_user = login_menu(db)
    
    while True:
        print("\n--- Menu ---")
        print("1. Post Item")
        print("2. View All Items")
        print("3. Search Items")
        print("4. Update Status")
        print("5. Contact Owner")
        print("6. Exit")
        choice = input("Choice: ").strip()
        
        if choice == "1":
            post_item(db, current_user=current_user.user_id if current_user else None)
        elif choice == "2":
            view_all_items(db)
        elif choice == "3":
            search_items(db)
        elif choice == "4":
            update_status(db)
        elif choice == "5":
            contact_owner(db)
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
