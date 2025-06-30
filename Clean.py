import os
import shutil

def delete_pycache_folders(base_path):
    """
    Recursively search and delete all '__pycache__' folders under base_path.
    """
    deleted_folders = []

    for root, dirs, files in os.walk(base_path):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                folder_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(folder_path)
                    print(f"✅ Deleted __pycache__: {folder_path}")
                    deleted_folders.append(folder_path)
                except Exception as e:
                    print(f"❌ Failed to delete {folder_path}: {e}")
    
    if not deleted_folders:
        print("No __pycache__ folders found.")
    else:
        print(f"\nTotal __pycache__ folders deleted: {len(deleted_folders)}")


def clear_logs_folder(logs_path):
    """
    Deletes all files and subfolders in the given logs folder.
    """
    if not os.path.exists(logs_path):
        print(f"⚠️ Logs folder does not exist: {logs_path}")
        return

    print(f"\nCleaning logs directory: {logs_path}")
    for item in os.listdir(logs_path):
        item_path = os.path.join(logs_path, item)
        try:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"🗑️ Deleted folder: {item_path}")
            else:
                os.remove(item_path)
                print(f"🗑️ Deleted file: {item_path}")
        except Exception as e:
            print(f"❌ Failed to delete {item_path}: {e}")


if __name__ == "__main__":
    base_dir = os.path.abspath(".")
    logs_dir = os.path.join(base_dir, "logs")

    print(f"📁 Scanning: {base_dir}")
    delete_pycache_folders(base_dir)
    clear_logs_folder(logs_dir)
