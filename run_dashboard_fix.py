import os
os.chmod('/Users/ianrakow/Desktop/AIVIIZN/fix_dashboard_now.sh', 0o755)
print("✅ Made fix_dashboard_now.sh executable")

import subprocess
result = subprocess.run('/Users/ianrakow/Desktop/AIVIIZN/fix_dashboard_now.sh', shell=True, capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("Errors:", result.stderr)
