import os
os.chmod('/Users/ianrakow/Desktop/AIVIIZN/quick_backup.sh', 0o755)
os.chmod('/Users/ianrakow/Desktop/AIVIIZN/backup_and_clean.sh', 0o755)
print("✅ Made backup scripts executable")
print("\nTo create the backup, run:")
print("  ./quick_backup.sh")
print("\nOr:")
print("  python3 create_backup.py")
