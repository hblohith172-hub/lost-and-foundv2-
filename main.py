import uuid
import os
import shutil
from datetime import datetime
from models import Item, Database
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


def main():
    db = Database()
    print("=" * 40)
    print("   LOST & FOUND ITEM TRACKER")
    print("=" * 40)
    
    while True:
        print("\n--- Menu ---")
        print("1. Post Item")
        print("2. View All Items")
        print("3. Exit")
        choice = input("Choice: ").strip()
        
        if choice == "1":
            post_item(db, current_user=None)
        elif choice == "2":
            view_all_items(db)
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
