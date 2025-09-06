#!/usr/bin/env python3
"""Migration script to help transition from old to new code structure."""

import os
import shutil
from pathlib import Path


def backup_old_files():
    """Create backup of old files before migration."""
    functions_dir = Path(__file__).parent
    backup_dir = functions_dir / "backup_old_code"
    
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    
    backup_dir.mkdir()
    
    # Files to backup
    old_files = [
        "auth.py",
        "events.py", 
        "reservations.py",
        "email_service.py"
    ]
    
    for file_name in old_files:
        old_file = functions_dir / file_name
        if old_file.exists():
            shutil.copy2(old_file, backup_dir / file_name)
            print(f"Backed up {file_name}")
    
    print(f"Old files backed up to {backup_dir}")


def verify_new_structure():
    """Verify that the new structure is in place."""
    functions_dir = Path(__file__).parent
    src_dir = functions_dir / "src" / "chome_functions"
    
    required_dirs = [
        "config",
        "utils", 
        "auth",
        "events",
        "reservations",
        "email"
    ]
    
    missing_dirs = []
    for dir_name in required_dirs:
        if not (src_dir / dir_name).exists():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"Missing directories: {missing_dirs}")
        return False
    
    print("New structure verified successfully")
    return True


def main():
    """Main migration function."""
    print("Starting migration process...")
    
    # Backup old files
    backup_old_files()
    
    # Verify new structure
    if verify_new_structure():
        print("Migration completed successfully!")
        print("\nNext steps:")
        print("1. Test the new functions locally")
        print("2. Update your deployment process if needed")
        print("3. Deploy to Firebase")
        print("4. Remove old files after confirming everything works")
    else:
        print("Migration failed - please check the structure")


if __name__ == "__main__":
    main()
