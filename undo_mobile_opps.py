import re

path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/Opportunities.vue'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Restore db-root and db-header
content = content.replace('padding: 16px !important;', 'padding: 2rem;')
content = content.replace('flex-direction: column !important;', 'flex-direction: row;')

# Remove the media queries I added at the end
content = content.replace("""
@media (min-width: 768px) {
    .db-root { padding: 2rem !important; }
    .db-header { flex-direction: row !important; }
    .greeting-text { font-size: 2rem !important; }
}
@media (max-width: 767px) {
    .greeting-text { font-size: 1.25rem !important; }
    .header-date-box { width: 100%; justify-content: space-between; }
}
""", "")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
