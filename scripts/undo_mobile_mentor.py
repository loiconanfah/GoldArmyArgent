import re

path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/Mentor.vue'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Restore style block to fixed padding version
style_block = """
<style scoped>
.db-root {
  min-height: 100vh;
  background-color: #F9FAFB;
  padding: 40px;
}

.db-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 40px;
}

.header-title-box {
  display: flex;
  flex-direction: column;
}

.header-title-box h1 {
  font-size: 32px;
  font-weight: 800;
  color: #111827;
  letter-spacing: -0.02em;
  margin: 0;
}

.header-title-box p {
  color: #6B7280;
  font-size: 16px;
  margin-top: 4px;
}

.header-date-box {
  display: flex;
  align-items: center;
  background: white;
  padding: 8px 16px;
  border-radius: 12px;
  border: 1px solid #E5E7EB;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.date-num {
  font-weight: 800;
  font-size: 20px;
  color: #E85D3E;
  margin-right: 12px;
}

.date-str {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.date-divider {
  width: 1px;
  height: 20px;
  background: #E5E7EB;
  margin: 0 12px;
}

.kpi-card {
  background: white;
  border-radius: 24px;
  padding: 24px;
  border: 1px solid #E5E7EB;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.kpi-card:hover {
  border-color: #E85D3E;
  box-shadow: 0 10px 20px rgba(232, 93, 62, 0.05);
  transform: translateY(-2px);
}

.icon-box {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  transition: transform 0.3s ease;
}

.kpi-card:hover .icon-box {
  transform: scale(1.1) rotate(-5deg);
}

.card-tag {
  position: absolute;
  top: 24px;
  right: 24px;
  font-size: 10px;
  font-weight: 800;
  padding: 4px 8px;
  border-radius: 6px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
</style>
"""

content = re.sub(r'<style scoped>.*</style>', style_block, content, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
