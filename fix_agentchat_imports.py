import re

path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/AgentChat.vue'

with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Professional way to fix: collect all icons and put them in the heroicons import
icons_to_move = ['MapPinIcon', 'CpuChipIcon', 'IdentificationIcon', 'AcademicCapIcon']
heroicons_import_line_index = -1
for i, line in enumerate(lines):
    if '@heroicons/vue/24/solid' in line:
        heroicons_import_line_index = i
        break

new_lines = []
for i, line in enumerate(lines):
    cleaned_line = line
    for icon in icons_to_move:
        if icon in cleaned_line and '@heroicons/vue/24/solid' not in cleaned_line:
            # Remove from this line
            cleaned_line = cleaned_line.replace(f'{icon},', '').replace(f'{icon}', '')
            # Clean up potential artifacts like "{ ," or ", }"
            cleaned_line = cleaned_line.replace('{ ,', '{').replace(', }', '}').replace('{  }', '{}')
    
    # If the line is an import that became empty or just whitespace, skip it?
    # No, just keep it, we'll clean up heroicons line specifically
    new_lines.append(cleaned_line)

# Now add to heroicons line
if heroicons_import_line_index != -1:
    h_line = new_lines[heroicons_import_line_index]
    # Find the closing brace of the import
    # This might span multiple lines, let's just do a string replacement if it's the standard format
    for icon in icons_to_move:
        if icon not in h_line:
            h_line = h_line.replace('}', f'  {icon},\n}}')
    new_lines[heroicons_import_line_index] = h_line

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("done")
