import os
os.chmod('/Users/ianrakow/Desktop/AIVIIZN/apply_directory_fix.sh', 0o755)
print("✅ Made apply_directory_fix.sh executable")

# Now run it
import subprocess
result = subprocess.run('/Users/ianrakow/Desktop/AIVIIZN/apply_directory_fix.sh', shell=True, capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("Errors:", result.stderr)
