import os
import subprocess

# Make executable
os.chmod('/Users/ianrakow/Desktop/AIVIIZN/fix_directories_now.sh', 0o755)
print("✅ Made fix_directories_now.sh executable")

# Run the fix
result = subprocess.run(
    '/Users/ianrakow/Desktop/AIVIIZN/fix_directories_now.sh',
    shell=True,
    capture_output=True,
    text=True
)

print(result.stdout)
if result.stderr:
    print("Errors:", result.stderr)
