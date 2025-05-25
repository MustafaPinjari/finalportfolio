import re

# File to process
file_path = 'notifications/views.py'

# Read the file content
with open(file_path, 'r') as file:
    content = file.read()

# Define the pattern to match render calls with 'admin/' paths excluding those that already have 'admin/notifications/'
pattern = r"render\(request,\s*'admin/(?!notifications/)([^']+)'\s*,\s*context\)"

# Replacement function to add the 'notifications/' directory
def replace_path(match):
    template_path = match.group(1)
    return f"render(request, 'admin/notifications/{template_path}', context)"

# Apply the replacement
new_content = re.sub(pattern, replace_path, content)

# Write the updated content back to the file
with open(file_path, 'w') as file:
    file.write(new_content)

print("Template paths updated successfully!")
