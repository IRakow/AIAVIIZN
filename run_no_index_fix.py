import os
os.chmod('/Users/ianrakow/Desktop/AIVIIZN/apply_no_index_fix.sh', 0o755)
print("✅ Made apply_no_index_fix.sh executable")

# Run the fix
import subprocess
result = subprocess.run('/Users/ianrakow/Desktop/AIVIIZN/apply_no_index_fix.sh', shell=True, capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("Errors:", result.stderr)
