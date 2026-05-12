with open('api/main.py', encoding='utf-8') as f:
    content = f.read()

old_block = (
    '# Enable CORS (allow_credentials=True exige des origines explicites, pas "*")\n'
    '_cors_origins = [\n'
    '    "http://localhost:5173",\n'
    '    "http://127.0.0.1:5173",\n'
    '    "http://localhost:3000",\n'
    '    "http://127.0.0.1:3000",\n'
    ']\n'
    "# En prod, ajouter l\u2019origine du front (ex. https://ton-site.com) ou la lire depuis .env\n"
    'cors_env = os.getenv("CORS_ORIGIN", "")\n'
    'if cors_env:\n'
    '    _cors_origins.extend([o.strip() for o in cors_env.split(",") if o.strip()])\n'
    '\n'
    'app.add_middleware(\n'
    '    CORSMiddleware,\n'
    '    allow_origins=_cors_origins,\n'
    '    # allow_origin_regex supprim\u00e9 \u2014 il annulait la protection des origines explicites.\n'
    "    # Si un nouveau domaine doit \u00eatre autoris\u00e9, l'ajouter dans CORS_ORIGIN (env var).\n"
    '    allow_credentials=True,\n'
    '    allow_methods=["*"],\n'
    '    allow_headers=["*"],\n'
    ')\n'
)

new_block = (
    '# Enable CORS\n'
    '_cors_origins = [\n'
    '    # Dev local\n'
    '    "http://localhost:5173",\n'
    '    "http://127.0.0.1:5173",\n'
    '    "http://localhost:3000",\n'
    '    "http://127.0.0.1:3000",\n'
    '    # Production GoldArmy\n'
    '    "https://goldarmyai.com",\n'
    '    "https://www.goldarmyai.com",\n'
    '    "https://app.goldarmyai.com",\n'
    '    "https://goldarmyai.onrender.com",\n'
    '    "https://goldarmy.onrender.com",\n'
    ']\n'
    '# Origines supplementaires via CORS_ORIGIN env var (virgule-separees)\n'
    'cors_env = os.getenv("CORS_ORIGIN", "")\n'
    'if cors_env:\n'
    '    _cors_origins.extend([o.strip() for o in cors_env.split(",") if o.strip()])\n'
    '\n'
    'app.add_middleware(\n'
    '    CORSMiddleware,\n'
    '    allow_origins=_cors_origins,\n'
    '    allow_credentials=True,\n'
    '    allow_methods=["*"],\n'
    '    allow_headers=["*"],\n'
    '    expose_headers=["*"],\n'
    ')\n'
)

# Try with the actual apostrophe in the file (curly quote)
idx = content.find('_cors_origins = [')
surroundings = content[idx-100:idx+500]
print("ACTUAL CONTENT:")
print(repr(surroundings))

if old_block in content:
    content = content.replace(old_block, new_block, 1)
    with open('api/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("REPLACED OK")
else:
    print("NOT FOUND with LF either, trying raw replace")
    # Direct line-based approach
    lines = content.split('\n')
    for i, l in enumerate(lines[40:70], start=41):
        print(f"{i}: {repr(l)}")
