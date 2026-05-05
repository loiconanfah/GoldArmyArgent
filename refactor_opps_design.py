import re

path = 'c:/Users/Utilisateur/PycharmProjects/GoldArmyArgent/frontend/src/views/Opportunities.vue'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Template Root and Header
# Replace the container div and the header
old_header_pattern = r'<div class="px-4 md:px-10 py-8 max-w-\[1400px\] mx-auto w-full animate-fade-in-up">.*?<!-- MAIN SEARCH ENGINE'
new_header = """<div class="db-root animate-fade-in-up">
    
    <!-- HEADER (Uniform with Dashboard) -->
    <div class="db-header">
       <div class="header-date-box">
           <div class="date-num">📡</div>
           <div class="date-str">{{ t('opportunities.tagline') }}</div>
           <div class="date-divider"></div>
           <div class="flex items-center gap-2">
               <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">{{ t('opportunities.max_results') }}</span>
               <select v-model="resultLimit" @change="performSearch" class="bg-slate-100 text-slate-900 focus:outline-none focus:ring-0 cursor-pointer px-2 py-1 rounded-lg font-bold appearance-none text-xs border border-slate-200">
                 <option :value="10">10</option>
                 <option :value="20">20</option>
                 <option :value="50">50</option>
                 <option :value="100">100</option>
                 <option :value="150">150</option>
                 <option :value="200">200</option>
               </select>
           </div>
       </div>
       
       <div class="header-greeting flex-1">
           <div class="greeting-text">
             <div class="flex items-center gap-3">
                 {{ t('opportunities.title_sniper') }} 
                 <span class="text-[#E85D3E]">{{ t('opportunities.title_recruitment') }}</span>
                 <img src="/logo.png" alt="Logo" class="w-10 h-10 animate-float ml-auto md:ml-4" />
             </div>
             <span class="greeting-sub text-sm md:text-lg block mt-1">{{ t('opportunities.description') }}</span>
           </div>
       </div>
    </div>

    <!-- MAIN SEARCH ENGINE"""

content = re.sub(old_header_pattern, new_header, content, flags=re.DOTALL)

# 2. Update Search Bar Design
old_search_pattern = r'<!-- MAIN SEARCH ENGINE \(Hero Bento Solid\) -->.*?<div class="bg-surface-950 rounded-2xl p-4 md:p-6 border border-surface-800 relative z-10">'
if '<!-- MAIN SEARCH ENGINE (Uniform Clean Style) -->' not in content:
    new_search = """<!-- MAIN SEARCH ENGINE (Uniform Clean Style) -->
    <div class="bg-white border border-slate-200 p-4 md:p-6 rounded-[2rem] shadow-sm mb-8 relative overflow-hidden">
        <div class="relative z-10">"""
    content = re.sub(old_search_pattern, new_search, content, flags=re.DOTALL)

# Update Search Inputs classes
content = content.replace('bg-surface-900 border border-surface-700 rounded-2xl focus-within:border-gold-500/50 transition-colors relative', 'bg-slate-50 border border-slate-200 rounded-2xl focus-within:border-[#E85D3E]/50 transition-colors relative')
content = content.replace('border-surface-700', 'border-slate-200')
content = content.replace('text-white focus:outline-none text-lg placeholder-slate-600 font-medium', 'text-slate-900 focus:outline-none text-lg placeholder-slate-400 font-medium')
content = content.replace('text-slate-500 group-focus-within:text-gold-400 transition-colors', 'text-slate-400 group-focus-within:text-[#E85D3E] transition-colors')

# Update Action Buttons in search bar
content = content.replace('bg-surface-800 text-slate-300 border-surface-700 hover:border-slate-500 hover:bg-surface-700', 'bg-white text-slate-600 border-slate-200 hover:border-[#E85D3E] hover:bg-slate-50')
content = content.replace('bg-gradient-to-r from-gold-500 to-amber-600 hover:from-gold-400 hover:to-amber-500', 'bg-[#E85D3E] hover:opacity-90')
content = content.replace('text-surface-950 font-black tracking-tight rounded-2xl transition-all shadow-[0_0_20px_rgba(245,158,11,0.3)] hover:shadow-[0_0_30px_rgba(245,158,11,0.5)]', 'text-white font-bold tracking-tight rounded-2xl transition-all shadow-lg shadow-[#E85D3E]/20')

# Update CV Upload Section
content = content.replace('border-surface-800', 'border-slate-100')
content = content.replace('border-surface-700 hover:border-gold-500/50 bg-gradient-to-b from-surface-900 to-surface-800/50 rounded-2xl p-10', 'border-slate-200 hover:border-[#E85D3E]/50 bg-slate-50 rounded-2xl p-10')
content = content.replace('text-white font-bold text-lg', 'text-slate-900 font-bold text-lg')

# 3. Update Empty State
old_empty_pattern = r'<div v-else-if="jobs.length === 0 && !isLoading" class="flex flex-col items-center justify-center py-24 bg-surface-900/50 rounded-\[2rem\] border-dashed border-2 border-surface-800">.*?</div>'
new_empty = """<div v-else-if="jobs.length === 0 && !isLoading" class="flex flex-col items-center justify-center py-24 bg-white rounded-[2rem] border-dashed border-2 border-slate-200">
        <div class="p-6 bg-slate-50 rounded-full mb-6 ring-1 ring-slate-100">
            <BriefcaseIcon class="w-12 h-12 text-slate-300" />
        </div>
        <h3 class="text-2xl font-display font-bold text-slate-900 mb-2 tracking-tight">{{ t('opportunities.no_opportunities') }}</h3>
        <p class="text-slate-500 text-center max-w-sm">{{ t('opportunities.no_opportunities_desc') }}</p>
    </div>"""
content = re.sub(old_empty_pattern, new_empty, content, flags=re.DOTALL)

# 4. Update Styles
dashboard_styles = """
.db-root { 
    padding: 2rem; 
    max-width: 1500px; 
    margin: 0 auto; 
    display: flex; 
    flex-direction: column; 
    gap: 1.5rem; 
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background-color: #F9FAFB; 
    min-height: 100vh;
}

.db-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 1.5rem;
    background: #FFFFFF;
    padding: 1.5rem;
    border-radius: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02), 0 10px 40px -10px rgba(0,0,0,0.02);
}

.header-date-box {
    display: flex;
    align-items: center;
    background: #F3F4F6;
    padding: 0.5rem 1rem;
    border-radius: 1rem;
    height: 56px;
}

.date-num {
    font-size: 1.5rem;
    font-weight: 800;
    color: #111827;
}

.date-str {
    font-size: 0.85rem;
    font-weight: 600;
    color: #4B5563;
    margin-left: 0.5rem;
}

.date-divider {
    width: 1px;
    height: 30px;
    background-color: #E5E7EB;
    margin: 0 1rem;
}

.header-greeting {
    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.greeting-text {
    font-size: 2rem;
    font-weight: 500;
    color: #111827;
    line-height: 1.1;
    letter-spacing: -0.02em;
}

.greeting-sub {
    color: #9CA3AF;
}

@keyframes floatLogo {
    0%, 100% { transform: translateY(0) scale(1); }
    50% { transform: translateY(-5px) scale(1.05) rotate(3deg); }
}
.animate-float {
    animation: floatLogo 3s ease-in-out infinite;
}
"""

if '.db-root {' not in content:
    content = content.replace('<style scoped>', '<style scoped>\n' + dashboard_styles)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
