import sys

with open('frontend/src/views/Reseaux.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove the invalid SVG style block
start_svg = '        <!-- SVG Styles for Animation -->\n        <svg width="0" height="0" class="hidden">\n            <style>\n                @keyframes dash {\n                    to { stroke-dashoffset: -20; }\n                }\n                @keyframes pulse-glow {\n                    0%, 100% { filter: drop-shadow(0 0 4px rgba(232, 93, 62, 0.4)); transform: scale(1); }\n                    50% { filter: drop-shadow(0 0 10px rgba(232, 93, 62, 0.8)); transform: scale(1.1); }\n                }\n                @keyframes float-node {\n                    0%, 100% { transform: translateY(0px); }\n                    50% { transform: translateY(-3px); }\n                }\n                .ninja-anim-edge {\n                    stroke-dasharray: 4,4;\n                    animation: dash 2s linear infinite;\n                }\n                .ninja-anim-node {\n                    transform-origin: center;\n                    animation: pulse-glow 3s infinite ease-in-out;\n                }\n                .ninja-float {\n                    animation: float-node 4s infinite ease-in-out;\n                }\n            </style>\n        </svg>'

if start_svg in content:
    content = content.replace(start_svg, '')
else:
    # try flexible replace
    import re
    content = re.sub(r'<!-- SVG Styles for Animation -->\s*<svg width="0" height="0" class="hidden">\s*<style>.*?</style>\s*</svg>', '', content, flags=re.DOTALL)

# 2. Append the styles to the end of the file inside <style>
new_styles = """
/* Ninja Animation Styles */
@keyframes dash-ninja {
  to { stroke-dashoffset: -20; }
}
@keyframes pulse-glow-ninja {
  0%, 100% { filter: drop-shadow(0 0 4px rgba(232, 93, 62, 0.4)); transform: scale(1); }
  50% { filter: drop-shadow(0 0 10px rgba(232, 93, 62, 0.8)); transform: scale(1.1); }
}
@keyframes float-node-ninja {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-3px); }
}
.ninja-anim-edge {
  stroke-dasharray: 4,4;
  animation: dash-ninja 2s linear infinite;
}
.ninja-anim-node {
  transform-origin: center;
  animation: pulse-glow-ninja 3s infinite ease-in-out;
  transform-box: fill-box;
}
.ninja-float {
  animation: float-node-ninja 4s infinite ease-in-out;
}
"""

if '</style>' in content:
    content = content.replace('</style>', new_styles + '\n</style>')
else:
    content += '\n<style scoped>\n' + new_styles + '\n</style>'

with open('frontend/src/views/Reseaux.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print('Patch applied successfully')
