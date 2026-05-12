path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/AgentChat.vue'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the missing comma after ArrowsPointingInIcon
content = content.replace('ArrowsPointingInIcon\n  ClockIcon,', 'ArrowsPointingInIcon,\n  ClockIcon,')
# Just in case there's a space
content = content.replace('ArrowsPointingInIcon \n  ClockIcon,', 'ArrowsPointingInIcon,\n  ClockIcon,')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
