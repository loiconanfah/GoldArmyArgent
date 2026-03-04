<script setup>
import { useRouter } from 'vue-router'

const currentYear = new Date().getFullYear()
</script>

<template>
  <footer class="bg-[#0a0a12] border-t border-white/5 pt-16 pb-8 relative z-20 overflow-hidden">
    <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom,_var(--tw-gradient-stops))] from-violet-900/20 via-[#0a0a12] to-transparent pointer-events-none"></div>
    <div class="max-w-7xl mx-auto px-6 relative z-10">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-12 md:gap-8 mb-16">
        
        <!-- Brand -->
        <div class="col-span-1 md:col-span-2">
          <router-link to="/" class="flex items-center gap-3 mb-6">
            <div class="w-8 h-8 rounded-xl overflow-hidden border border-violet-500/30">
              <img src="/logo.png" alt="Logo GoldArmy" class="w-full h-full object-cover" />
            </div>
            <span class="text-xl font-black tracking-tight uppercase text-white">GoldArmy</span>
          </router-link>
          <p class="text-slate-400 text-sm max-w-sm leading-relaxed mb-6">
            L'Intelligence Artificielle au service de votre carrière. Déjouez les algorithmes RH et décrochez les entretiens que vous méritez.
          </p>
          <div class="flex gap-4">
            <a href="#" class="w-10 h-10 rounded-full bg-surface-900 flex items-center justify-center text-slate-400 hover:text-white hover:bg-violet-600 transition-colors border border-white/5">
              <!-- X / Twitter Icon -->
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.007 4.56H5.117z"></path></svg>
            </a>
            <a href="#" class="w-10 h-10 rounded-full bg-surface-900 flex items-center justify-center text-slate-400 hover:text-white hover:bg-violet-600 transition-colors border border-white/5">
              <!-- LinkedIn Icon -->
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path fill-rule="evenodd" d="M19.812 5.418c.861.23 1.538.907 1.768 1.768C21.998 8.746 22 12 22 12s0 3.254-.42 4.814a2.504 2.504 0 01-1.768 1.768c-1.56.419-7.812.419-7.812.419s-6.252 0-7.812-.419a2.505 2.505 0 01-1.768-1.768C2 15.254 2 12 2 12s0-3.254.42-4.814zM8.5 15.518V8.482L14.436 12 8.5 15.518z" clip-rule="evenodd"></path></svg>
            </a>
          </div>
        </div>

        <!-- Links Group 1 -->
        <div>
          <h4 class="text-white font-bold mb-6 tracking-wide">Outils Gratuits</h4>
          <ul class="space-y-4">
            <li><router-link to="/free-cv-roast" class="text-sm text-slate-400 hover:text-violet-400 transition-colors">Audit CV IA</router-link></li>
            <li><router-link to="/free-interview" class="text-sm text-slate-400 hover:text-violet-400 transition-colors">Simulateur Entretien</router-link></li>
          </ul>
        </div>

        <!-- Links Group 2 -->
        <div>
          <h4 class="text-white font-bold mb-6 tracking-wide">Plateforme</h4>
          <ul class="space-y-4">
            <li><router-link to="/login" class="text-sm text-slate-400 hover:text-violet-400 transition-colors">Connexion</router-link></li>
            <li><router-link to="/register" class="text-sm text-slate-400 hover:text-violet-400 transition-colors">Créer un compte</router-link></li>
            <li><router-link to="/blog" class="text-sm text-slate-400 hover:text-violet-400 transition-colors">Le Blog</router-link></li>
          </ul>
        </div>

      </div>

      <!-- Bottom Bar -->
      <div class="pt-8 border-t border-white/10 flex flex-col md:flex-row items-center justify-between gap-4">
        <p class="text-slate-500 text-xs text-center md:text-left">
          © {{ currentYear }} GoldArmy. Tous droits réservés.
        </p>
        <div class="flex items-center gap-6">
          <a href="#" class="text-xs text-slate-500 hover:text-white transition-colors">Politique de confidentialité</a>
          <a href="#" class="text-xs text-slate-500 hover:text-white transition-colors">C.G.V.</a>
        </div>
      </div>
    </div>
  </footer>
</template>
