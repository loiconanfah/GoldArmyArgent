<script setup>
import { useRouter } from 'vue-router'
import {
  RocketLaunchIcon,
  ShieldCheckIcon,
  SparklesIcon,
  ChartBarIcon,
  BriefcaseIcon,
  CpuChipIcon,
  CheckCircleIcon,
  UserGroupIcon,
  ArrowTrendingUpIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()

const features = [
  {
    name: 'Sniper IA',
    description: 'Notre IA analyse le marché en temps réel pour dénicher les offres cachées et sur-mesure pour votre profil.',
    icon: RocketLaunchIcon,
  },
  {
    name: 'CRM Intelligent',
    description: 'Suivez vos candidatures avec un Kanban automatisé qui qualifie et score vos chances de succès.',
    icon: ChartBarIcon,
  },
  {
    name: 'Générateur de Réseau',
    description: 'Identifiez les décideurs clés et générez des messages d\'accroche hyper-personnalisés en un clic.',
    icon: BriefcaseIcon,
  },
  {
    name: 'Mentor IA Pro',
    description: 'Préparez vos entretiens avec un coach virtuel expert qui s\'adapte à l\'entreprise ciblée.',
    icon: CpuChipIcon,
  },
]
</script>

<template>
  <div class="min-h-screen bg-surface-950 text-slate-200 selection:bg-indigo-500/30 font-sans overflow-x-hidden">
    
    <!-- Navbar (Public) -->
    <header class="absolute inset-x-0 top-0 z-50">
      <nav class="flex items-center justify-between p-6 lg:px-12" aria-label="Global">
        <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-indigo-700 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                <SparklesIcon class="w-6 h-6 text-white" />
            </div>
            <span class="text-xl font-display font-bold text-white tracking-tight">GoldArmy</span>
        </div>
        <div class="flex flex-1 justify-end gap-4 items-center">
          <router-link to="/login" class="text-sm font-semibold leading-6 text-slate-300 hover:text-white transition-colors">Connexion</router-link>
          <router-link to="/register" class="rounded-lg bg-indigo-500 hover:bg-indigo-400 px-4 py-2.5 text-sm font-bold text-white shadow-sm shadow-indigo-500/20 transition-all border border-indigo-400/20">Créer un compte</router-link>
        </div>
      </nav>
    </header>

    <main>
      <!-- Hero section -->
      <div class="relative isolate pt-14">
        <div class="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/20 via-surface-950 to-surface-950"></div>
        <div class="absolute inset-y-0 right-1/2 -z-10 -mr-96 w-[200%] origin-top-right skew-x-[-30deg] bg-surface-950 shadow-xl shadow-indigo-900/10 ring-1 ring-surface-800 sm:-mr-80 lg:-mr-96" aria-hidden="true"></div>
        
        <div class="mx-auto max-w-7xl px-6 py-24 sm:py-32 lg:px-8">
          <div class="mx-auto max-w-2xl lg:mx-0 lg:max-w-xl">
            <div class="mb-8 flex">
              <div class="relative rounded-full px-3 py-1 text-sm leading-6 text-indigo-300 ring-1 ring-white/10 hover:ring-white/20">
                Lancement de la version 2.0. <router-link to="/register" class="font-semibold text-indigo-400"><span class="absolute inset-0" aria-hidden="true"></span>En savoir plus <span aria-hidden="true">&rarr;</span></router-link>
              </div>
            </div>
            <h1 class="text-4xl font-display font-bold tracking-tight text-white sm:text-6xl mb-6">
              Votre carrière propulsée par l'Intelligence Artificielle.
            </h1>
            <p class="mt-6 text-lg leading-8 text-slate-400">
              Automatisez votre recherche d'emploi. De l'identification des offres cachées à la préparation de vos entretiens, GoldArmy est l'agent IA qui travaille pour vous, 24/7.
            </p>
            <div class="mt-10 flex items-center gap-x-6">
              <router-link to="/register" class="rounded-xl bg-gradient-to-r from-indigo-500 to-indigo-600 px-6 py-3.5 text-sm font-bold text-white shadow-lg shadow-indigo-500/30 hover:shadow-indigo-500/50 hover:from-indigo-400 hover:to-indigo-500 transition-all focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-400">
                Commencer gratuitement
              </router-link>
              <a href="#features" class="text-sm font-semibold leading-6 text-slate-300 hover:text-white transition-colors">Découvrir les workflows <span aria-hidden="true">↓</span></a>
            </div>
          </div>
          
          <!-- Mockup graphic -->
          <div class="mx-auto mt-16 flex max-w-2xl sm:mt-24 lg:ml-10 lg:mr-0 lg:mt-0 lg:max-w-none lg:flex-none xl:ml-32">
            <div class="max-w-3xl flex-none sm:max-w-5xl lg:max-w-none">
              <div class="rounded-xl bg-surface-900/50 p-2 ring-1 ring-white/10 lg:rounded-2xl shadow-2xl backdrop-blur-sm -rotate-2 hover:rotate-0 transition-transform duration-700">
                <div class="rounded-md bg-surface-950 p-4 ring-1 ring-white/10 aspect-[16/9] w-[800px] flex flex-col relative overflow-hidden">
                    
                    <!-- Fake SaaS UI inside Mockup -->
                    <div class="w-full h-8 border-b border-surface-800 flex items-center gap-2 px-4 shrink-0">
                        <div class="w-3 h-3 rounded-full bg-rose-500"></div><div class="w-3 h-3 rounded-full bg-amber-500"></div><div class="w-3 h-3 rounded-full bg-emerald-500"></div>
                    </div>
                    <div class="flex-1 p-6 grid grid-cols-3 gap-6 relative z-10">
                        <div class="col-span-2 space-y-4">
                            <div class="w-1/3 h-6 bg-surface-800 rounded-md"></div>
                            <div class="grid grid-cols-2 gap-4">
                                <div class="h-24 bg-surface-800/50 border border-surface-700 rounded-lg p-3">
                                    <div class="w-8 h-8 rounded-md bg-indigo-500/20 mb-2"></div>
                                    <div class="w-1/2 h-3 bg-surface-700 rounded mb-1"></div><div class="w-1/4 h-5 bg-indigo-500 rounded"></div>
                                </div>
                                <div class="h-24 bg-surface-800/50 border border-surface-700 rounded-lg p-3">
                                    <div class="w-8 h-8 rounded-md bg-rose-500/20 mb-2"></div>
                                    <div class="w-1/2 h-3 bg-surface-700 rounded mb-1"></div><div class="w-1/4 h-5 bg-rose-500 rounded"></div>
                                </div>
                            </div>
                            <div class="h-32 bg-surface-800/30 border border-surface-700 rounded-lg relative overflow-hidden">
                                <div class="absolute bottom-0 w-full h-1/2 bg-gradient-to-t from-indigo-500/20 to-transparent"></div>
                                <div class="absolute bottom-0 left-0 w-1/4 h-full bg-indigo-500/40 border-t border-r border-indigo-400/50" style="border-radius: 0 4px 0 0;"></div>
                                <div class="absolute bottom-0 left-1/4 w-1/4 h-2/3 bg-indigo-500/60 border-t border-r border-indigo-400/50" style="border-radius: 0 4px 0 0;"></div>
                                <div class="absolute bottom-0 left-2/4 w-1/4 h-1/3 bg-indigo-500/80 border-t border-r border-indigo-400/50" style="border-radius: 0 4px 0 0;"></div>
                                <div class="absolute bottom-0 left-3/4 w-1/4 h-[80%] bg-indigo-500 border-t border-r border-indigo-400/50" style="border-radius: 0 4px 0 0;"></div>
                            </div>
                        </div>
                        <div class="col-span-1 space-y-4">
                            <div class="h-full bg-surface-800/50 border border-surface-700 rounded-lg p-4 space-y-3">
                                <div class="w-1/2 h-4 bg-surface-700 rounded"></div>
                                <div class="flex gap-2 items-center"><div class="w-6 h-6 rounded-full bg-surface-600"></div><div class="w-3/4 h-3 bg-surface-700 rounded"></div></div>
                                <div class="flex gap-2 items-center"><div class="w-6 h-6 rounded-full bg-surface-600"></div><div class="w-3/4 h-3 bg-surface-700 rounded"></div></div>
                                <div class="flex gap-2 items-center"><div class="w-6 h-6 rounded-full bg-surface-600"></div><div class="w-3/4 h-3 bg-surface-700 rounded"></div></div>
                            </div>
                        </div>
                    </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Workflows / Agents Detailed Sections -->
      <div id="workflows" class="py-24 sm:py-32 overflow-hidden">
        <div class="mx-auto max-w-7xl px-6 lg:px-8">
          
          <!-- Sniper IA -->
          <div class="mx-auto grid max-w-2xl grid-cols-1 gap-x-12 gap-y-16 lg:mx-0 lg:max-w-none lg:grid-cols-2 items-center mb-32">
            <div class="lg:pr-8">
              <div class="flex items-center gap-3 mb-6">
                <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-500/10 border border-indigo-500/20">
                    <RocketLaunchIcon class="h-6 w-6 text-indigo-400" />
                </div>
                <h2 class="text-base font-semibold leading-7 text-indigo-400">Agent Sourcing</h2>
              </div>
              <p class="mt-2 text-3xl font-display font-bold tracking-tight text-white sm:text-4xl">Sniper IA</p>
              <p class="mt-6 text-lg leading-8 text-slate-400">Le marché de l'emploi est asymétrique. Notre agent IA parcourt le web profond, déjoue les algorithmes classiques et vous rapporte les opportunités en or avant même qu'elles ne soient publiques.</p>
              <ul role="list" class="mt-8 space-y-4 text-sm leading-6 text-slate-300">
                <li class="flex gap-x-3"><CheckCircleIcon class="mt-1 h-5 w-5 flex-none text-indigo-400" /> Scraping multi-sources intelligent</li>
                <li class="flex gap-x-3"><CheckCircleIcon class="mt-1 h-5 w-5 flex-none text-indigo-400" /> Contournement anti-bot automatisé</li>
                <li class="flex gap-x-3"><CheckCircleIcon class="mt-1 h-5 w-5 flex-none text-indigo-400" /> Scoring d'affinité avec votre profil CV</li>
              </ul>
            </div>
            <div class="rounded-2xl bg-surface-900 border border-surface-800 p-8 shadow-2xl relative">
              <div class="absolute inset-0 bg-gradient-to-tr from-indigo-500/10 to-transparent rounded-2xl pointer-events-none"></div>
              <div class="space-y-4 relative z-10 w-full mb-4">
                <div class="h-10 w-3/4 bg-surface-800 rounded-lg flex items-center px-4"><div class="w-1/2 h-3 bg-surface-600 rounded"></div></div>
                <div class="h-16 w-full bg-surface-800 border-l-2 border-indigo-500 rounded-r-lg p-3 flex flex-col justify-center"><div class="w-3/4 h-3 bg-surface-600 rounded mb-2"></div><div class="flex gap-2"><div class="w-16 h-4 bg-emerald-500/20 text-emerald-500 text-[10px] font-bold flex items-center justify-center rounded">98% Match</div></div></div>
                <div class="h-16 w-full bg-surface-800 border-l-2 border-amber-500 rounded-r-lg p-3 flex flex-col justify-center"><div class="w-2/3 h-3 bg-surface-600 rounded mb-2"></div><div class="flex gap-2"><div class="w-16 h-4 bg-amber-500/20 text-amber-500 text-[10px] font-bold flex items-center justify-center rounded">64% Match</div></div></div>
              </div>
            </div>
          </div>

          <!-- CRM -->
          <div class="mx-auto grid max-w-2xl grid-cols-1 gap-x-12 gap-y-16 lg:mx-0 lg:max-w-none lg:grid-cols-2 items-center mb-32">
             <div class="lg:col-start-2 lg:pl-8">
              <div class="flex items-center gap-3 mb-6">
                <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-purple-500/10 border border-purple-500/20">
                    <ChartBarIcon class="h-6 w-6 text-purple-400" />
                </div>
                <h2 class="text-base font-semibold leading-7 text-purple-400">Tableau de Bord</h2>
              </div>
              <p class="mt-2 text-3xl font-display font-bold tracking-tight text-white sm:text-4xl">CRM Intelligent</p>
              <p class="mt-6 text-lg leading-8 text-slate-400">Transformez votre recherche d'emploi en une machine de guerre. Suivez visuellement chaque étape, sachez précisément quand relancer et gardez une trace de toutes vos interactions.</p>
               <ul role="list" class="mt-8 space-y-4 text-sm leading-6 text-slate-300">
                <li class="flex gap-x-3"><CheckCircleIcon class="mt-1 h-5 w-5 flex-none text-purple-400" /> Kanban drag & drop fluide</li>
                <li class="flex gap-x-3"><CheckCircleIcon class="mt-1 h-5 w-5 flex-none text-purple-400" /> Rappels automatiques de relance</li>
                <li class="flex gap-x-3"><CheckCircleIcon class="mt-1 h-5 w-5 flex-none text-purple-400" /> Historisation des échanges</li>
              </ul>
            </div>
            <div class="lg:col-start-1 lg:row-start-1 rounded-2xl bg-surface-900 border border-surface-800 p-8 shadow-2xl relative flex gap-4">
                <div class="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-transparent rounded-2xl pointer-events-none"></div>
                <div class="flex-1 space-y-3 relative z-10 w-full mb-4">
                    <div class="h-4 w-1/2 bg-surface-700 rounded mb-4"></div>
                    <div class="h-12 w-full bg-surface-800 rounded-lg"></div>
                    <div class="h-12 w-full bg-surface-800 rounded-lg"></div>
                     <div class="h-12 w-full bg-surface-800 rounded-lg opacity-50"></div>
                </div>
                 <div class="flex-1 space-y-3 relative z-10 w-full mb-4">
                    <div class="h-4 w-2/3 bg-surface-700 rounded mb-4"></div>
                    <div class="h-20 w-full bg-surface-800 rounded-lg border border-purple-500/30"></div>
                    <div class="h-12 w-full bg-surface-800 rounded-lg"></div>
                </div>
            </div>
          </div>

          <!-- Network -->
          <div class="mx-auto grid max-w-2xl grid-cols-1 gap-x-12 gap-y-16 lg:mx-0 lg:max-w-none lg:grid-cols-2 items-center mb-32">
            <div class="lg:pr-8">
              <div class="flex items-center gap-3 mb-6">
                <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500/10 border border-emerald-500/20">
                    <BriefcaseIcon class="h-6 w-6 text-emerald-400" />
                </div>
                <h2 class="text-base font-semibold leading-7 text-emerald-400">Agent Social</h2>
              </div>
              <p class="mt-2 text-3xl font-display font-bold tracking-tight text-white sm:text-4xl">Générateur de Réseau</p>
              <p class="mt-6 text-lg leading-8 text-slate-400">Postuler ne suffit plus. L'IA scanne l'organigramme cible et rédige des emails d'accroche ultra-personnalisés aux CTOs et recruteurs pour court-circuiter le processus classique.</p>
              <ul role="list" class="mt-8 space-y-4 text-sm leading-6 text-slate-300">
                <li class="flex gap-x-3"><CheckCircleIcon class="mt-1 h-5 w-5 flex-none text-emerald-400" /> Analyse des décideurs cibles</li>
                <li class="flex gap-x-3"><CheckCircleIcon class="mt-1 h-5 w-5 flex-none text-emerald-400" /> Création de messages sur-mesure</li>
                <li class="flex gap-x-3"><CheckCircleIcon class="mt-1 h-5 w-5 flex-none text-emerald-400" /> Gestion du carnet d'adresses réseau</li>
              </ul>
            </div>
            <div class="rounded-2xl bg-surface-900 border border-surface-800 p-8 shadow-2xl relative">
                <div class="absolute inset-0 bg-gradient-to-tr from-emerald-500/10 to-transparent rounded-2xl pointer-events-none"></div>
                <div class="bg-surface-800 rounded-lg p-4 relative z-10 space-y-3 border border-surface-700 w-full mb-4">
                    <div class="flex items-center gap-3 border-b border-surface-700 pb-3">
                        <div class="w-8 h-8 rounded-full bg-surface-600"></div>
                        <div><div class="h-3 w-24 bg-surface-600 rounded mb-1"></div><div class="h-2 w-32 bg-surface-700 rounded"></div></div>
                    </div>
                    <div class="space-y-2 pt-2">
                        <div class="h-2 w-3/4 bg-emerald-500/40 rounded"></div>
                        <div class="h-2 w-full bg-surface-600 rounded"></div>
                        <div class="h-2 w-5/6 bg-surface-600 rounded"></div>
                        <div class="h-2 w-1/2 bg-surface-600 rounded"></div>
                    </div>
                </div>
            </div>
          </div>

          <!-- Mentor -->
           <div class="mx-auto grid max-w-2xl grid-cols-1 gap-x-12 gap-y-16 lg:mx-0 lg:max-w-none lg:grid-cols-2 items-center">
             <div class="lg:col-start-2 lg:pl-8">
              <div class="flex items-center gap-3 mb-6">
                <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-orange-500/10 border border-orange-500/20">
                    <CpuChipIcon class="h-6 w-6 text-orange-400" />
                </div>
                <h2 class="text-base font-semibold leading-7 text-orange-400">Agent Formateur</h2>
              </div>
              <p class="mt-2 text-3xl font-display font-bold tracking-tight text-white sm:text-4xl">Mentor IA Pro</p>
              <p class="mt-6 text-lg leading-8 text-slate-400">Ne soyez jamais pris au dépourvu. Effectuez des simulations d'entretiens techniques ou RH. L'IA joue le rôle du recruteur intransigeant puis débriefe vos réponses en détail.</p>
              <ul role="list" class="mt-8 space-y-4 text-sm leading-6 text-slate-300">
                <li class="flex gap-x-3"><CheckCircleIcon class="mt-1 h-5 w-5 flex-none text-orange-400" /> Simulations d'entretien textuelles réalistes</li>
                <li class="flex gap-x-3"><CheckCircleIcon class="mt-1 h-5 w-5 flex-none text-orange-400" /> Débriefing et axes d'amélioration identifiés</li>
                <li class="flex gap-x-3"><CheckCircleIcon class="mt-1 h-5 w-5 flex-none text-orange-400" /> Historique de la progression</li>
              </ul>
            </div>
            <div class="lg:col-start-1 lg:row-start-1 rounded-2xl bg-surface-900 border border-surface-800 p-8 shadow-2xl relative">
               <div class="absolute inset-0 bg-gradient-to-br from-orange-500/10 to-transparent rounded-2xl pointer-events-none"></div>
               <div class="space-y-4 relative z-10 w-full mb-4">
                   <div class="flex gap-3">
                       <div class="w-8 h-8 rounded-lg bg-orange-500/20 shrink-0"></div>
                       <div class="bg-surface-800 rounded-2xl rounded-tl-none p-4 w-3/4"><div class="h-2 w-full bg-surface-600 rounded mb-2"></div><div class="h-2 w-2/3 bg-surface-600 rounded"></div></div>
                   </div>
                   <div class="flex gap-3 justify-end mt-4">
                       <div class="bg-indigo-500/20 rounded-2xl border border-indigo-500/30 rounded-tr-none p-4 w-3/4"><div class="h-2 w-full bg-indigo-400/50 rounded mb-2"></div><div class="h-2 w-1/2 bg-indigo-400/50 rounded"></div></div>
                       <div class="w-8 h-8 rounded-full bg-indigo-500 shrink-0"></div>
                   </div>
               </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Stats Section -->
      <div class="relative bg-surface-900 border-y border-surface-800 py-16 sm:py-24 overflow-hidden">
        <div class="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-indigo-500/5 via-transparent to-transparent"></div>
        <div class="mx-auto max-w-7xl px-6 lg:px-8 relative z-10">
          <dl class="grid grid-cols-1 gap-x-8 gap-y-16 text-center lg:grid-cols-3">
            <div class="mx-auto flex max-w-xs flex-col gap-y-4">
              <dt class="text-base leading-7 text-slate-400">Heures de recherche économisées</dt>
              <dd class="order-first text-3xl font-display font-semibold tracking-tight text-white sm:text-5xl">40h / mois</dd>
            </div>
            <div class="mx-auto flex max-w-xs flex-col gap-y-4">
              <dt class="text-base leading-7 text-slate-400">Taux de réponse aux candidatures</dt>
              <dd class="order-first text-3xl font-display font-semibold tracking-tight text-white sm:text-5xl"><span class="text-indigo-400">+</span>300%</dd>
            </div>
            <div class="mx-auto flex max-w-xs flex-col gap-y-4">
              <dt class="text-base leading-7 text-slate-400">Entretiens décrochés en moyenne</dt>
              <dd class="order-first text-3xl font-display font-semibold tracking-tight text-white sm:text-5xl">5 / semaine</dd>
            </div>
          </dl>
        </div>
      </div>

      <!-- How it works -->
      <div class="py-24 sm:py-32">
        <div class="mx-auto max-w-7xl px-6 lg:px-8">
          <div class="mx-auto max-w-2xl lg:text-center">
            <h2 class="text-base font-semibold leading-7 text-indigo-400">La méthode GoldArmy</h2>
            <p class="mt-2 text-3xl font-display font-bold tracking-tight text-white sm:text-4xl">Comment l'IA trouve votre prochain job</p>
          </div>
          <div class="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
            <div class="grid grid-cols-1 gap-y-16 lg:grid-cols-3 lg:gap-x-12">
                <div class="relative pl-12">
                    <div class="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500 text-white font-bold shadow-lg shadow-indigo-500/20">1</div>
                    <h3 class="text-xl font-bold text-white mb-2">Configurez votre profil IA</h3>
                    <p class="text-slate-400 leading-relaxed">Importez votre CV et définissez vos critères (salaire, remote, secteur). L'agent apprend à connaître votre parcours dans les moindres détails.</p>
                </div>
                <div class="relative pl-12 lg:-mt-8">
                    <div class="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500 text-white font-bold shadow-lg shadow-indigo-500/20">2</div>
                    <h3 class="text-xl font-bold text-white mb-2">GoldArmy scanne le marché</h3>
                    <p class="text-slate-400 leading-relaxed">Pendant que vous dormez, nos crawlers parcourent des milliers de sources (LinkedIn, Jooble, sites carrières) pour dénicher les offres parfaites.</p>
                </div>
                <div class="relative pl-12">
                    <div class="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500 text-white font-bold shadow-lg shadow-indigo-500/20">3</div>
                    <h3 class="text-xl font-bold text-white mb-2">Passez à l'action</h3>
                    <p class="text-slate-400 leading-relaxed">Recevez une shortlist qualifiée. L'IA rédige vos lettres de motivation sur-mesure et vous prépare aux questions d'entretien spécifiques à l'entreprise.</p>
                </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Testimonials & Form Combined -->
      <div class="bg-surface-900 border-y border-surface-800 py-24 sm:py-32 relative">
        <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-5"></div>
        <div class="mx-auto max-w-7xl px-6 lg:px-8 relative z-10">
          
          <div class="mx-auto max-w-2xl lg:text-center mb-16">
            <h2 class="text-base font-semibold leading-7 text-indigo-400">Ce qu'ils en pensent</h2>
            <p class="mt-2 text-3xl font-display font-bold tracking-tight text-white sm:text-4xl">Adopté par les meilleurs talents</p>
          </div>

          <div class="mx-auto grid max-w-2xl grid-cols-1 gap-x-12 gap-y-16 lg:mx-0 lg:max-w-none lg:grid-cols-2 lg:items-start">
            
            <!-- Left Column: Testimonials -->
            <div class="flex flex-col gap-8">
              <!-- Testimonial 1 -->
              <figure class="rounded-2xl bg-surface-950 p-8 text-sm leading-6 border border-surface-800 shadow-xl shadow-surface-950/50">
                <blockquote class="text-slate-300">
                  <p>“Grâce à GoldArmy, j'ai arrêté d'envoyer des CV dans le vide. L'IA a trouvé une offre cachée sur un petit site carrière, j'ai postulé avec la lettre générée, et j'ai eu l'entretien le lendemain.”</p>
                </blockquote>
                <figcaption class="mt-6 flex items-center gap-x-4">
                  <div class="h-10 w-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-bold text-xs ring-2 ring-surface-900">MR</div>
                  <div>
                    <div class="font-semibold text-white">Marc R.</div>
                    <div class="text-slate-500 text-xs">Développeur Fullstack</div>
                  </div>
                </figcaption>
              </figure>

              <!-- Testimonial 2 -->
              <figure class="rounded-2xl bg-surface-950 p-8 text-sm leading-6 border border-surface-800 shadow-xl shadow-surface-950/50">
                <blockquote class="text-slate-300">
                  <p>“Le module Mentor IA m'a littéralement sauvé la vie pour mon entretien technique chez un GAFAM. Les questions d'anticipation étaient à 80% celles que j'ai eues le jour J.”</p>
                </blockquote>
                <figcaption class="mt-6 flex items-center gap-x-4">
                  <div class="h-10 w-10 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center text-white font-bold text-xs ring-2 ring-surface-900">SL</div>
                  <div>
                    <div class="font-semibold text-white">Sophie L.</div>
                    <div class="text-slate-500 text-xs">Data Scientist</div>
                  </div>
                </figcaption>
              </figure>
              
               <!-- Testimonial 3 -->
              <figure class="rounded-2xl bg-surface-950 p-8 text-sm leading-6 border border-surface-800 shadow-xl shadow-surface-950/50">
                <blockquote class="text-slate-300">
                  <p>“Je n'ai jamais été doué pour le networking. Le Générateur de Réseau m'a permis d'identifier les CTO directement et de leur envoyer des messages pertinents. Mon taux de réponse a explosé.”</p>
                </blockquote>
                <figcaption class="mt-6 flex items-center gap-x-4">
                  <div class="h-10 w-10 rounded-full bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center text-white font-bold text-xs ring-2 ring-surface-900">JD</div>
                  <div>
                    <div class="font-semibold text-white">Julien D.</div>
                    <div class="text-slate-500 text-xs">Product Manager</div>
                  </div>
                </figcaption>
              </figure>
            </div>

            <!-- Right Column: Comment Form -->
            <div class="lg:sticky lg:top-32">
              <div class="bg-surface-950 border border-surface-800 rounded-3xl p-8 shadow-2xl relative overflow-hidden">
                <div class="absolute inset-0 bg-gradient-to-t from-indigo-500/5 to-transparent pointer-events-none"></div>
                <div class="relative z-10">
                    <h3 class="text-xl font-bold text-white mb-2">Partagez votre expérience</h3>
                    <p class="text-sm text-slate-400 mb-6">Avez-vous trouvé votre job de rêve avec GoldArmy ? Racontez-nous !</p>
                    <form class="space-y-4" @submit.prevent>
                        <div class="grid grid-cols-1 gap-4">
                            <input type="text" placeholder="Votre Prénom" class="w-full bg-surface-900 border border-surface-700 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all font-medium" />
                            <input type="text" placeholder="Votre Rôle (ex: Dev SecOps)" class="w-full bg-surface-900 border border-surface-700 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all font-medium" />
                        </div>
                        <textarea rows="4" placeholder="Votre message..." class="w-full bg-surface-900 border border-surface-700 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all resize-none font-medium"></textarea>
                        <button type="submit" class="bg-indigo-500 hover:bg-indigo-400 text-white font-bold text-sm px-6 py-3 rounded-xl transition-colors w-full shadow-lg shadow-indigo-500/20">
                            Soumettre mon témoignage
                        </button>
                        <p class="text-xs text-slate-500 mt-2 text-center">Votre avis sera modéré avant d'être publié publiquement.</p>
                    </form>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>

      <!-- Pricing -->
      <div class="py-24 sm:py-32">
        <div class="mx-auto max-w-7xl px-6 lg:px-8">
          <div class="mx-auto max-w-2xl sm:text-center">
            <h2 class="text-3xl font-display font-bold tracking-tight text-white sm:text-4xl">Un investissement rentable dès le premier salaire</h2>
            <p class="mt-6 text-lg leading-8 text-slate-400">Choisissez le plan adapté à votre niveau d'ambition. Pas d'engagement, annulez quand vous trouvez votre job.</p>
          </div>
          <div class="mx-auto mt-16 max-w-2xl rounded-3xl ring-1 ring-surface-800 sm:mt-20 lg:mx-0 lg:flex lg:max-w-none bg-surface-900">
            <div class="p-8 sm:p-10 lg:flex-auto">
              <h3 class="text-2xl font-bold tracking-tight text-white">Accès Pro Illimité</h3>
              <p class="mt-6 text-base leading-7 text-slate-400">Accédez à l'intégralité des agents IA de GoldArmy. La puissance d'un cabinet de recrutement personnel dans votre poche.</p>
              <div class="mt-10 flex items-center gap-x-4">
                <h4 class="flex-none text-sm font-semibold leading-6 text-indigo-400">Ce qui est inclus</h4>
                <div class="h-px flex-auto bg-surface-800"></div>
              </div>
              <ul role="list" class="mt-8 grid grid-cols-1 gap-4 text-sm leading-6 text-slate-300 sm:grid-cols-2 sm:gap-6">
                <li class="flex gap-x-3"><CheckCircleIcon class="h-6 w-5 flex-none text-indigo-400" />Recherche d'offres automatisée (Sniper)</li>
                <li class="flex gap-x-3"><CheckCircleIcon class="h-6 w-5 flex-none text-indigo-400" />Radar Entreprise (Salaires & Réputation)</li>
                <li class="flex gap-x-3"><CheckCircleIcon class="h-6 w-5 flex-none text-indigo-400" />Mentorat d'entretien illimité</li>
                <li class="flex gap-x-3"><CheckCircleIcon class="h-6 w-5 flex-none text-indigo-400" />Génération de lettres & emails sur-mesure</li>
              </ul>
            </div>
            <div class="-mt-2 p-2 lg:mt-0 lg:w-full lg:max-w-md lg:flex-shrink-0">
              <div class="rounded-2xl bg-surface-950 py-10 text-center ring-1 ring-inset ring-surface-800 lg:flex lg:flex-col lg:justify-center lg:py-16 h-full shadow-inner">
                <div class="mx-auto max-w-xs px-8">
                  <p class="text-base font-semibold text-slate-400">Facturé mensuellement</p>
                  <p class="mt-6 flex items-baseline justify-center gap-x-2">
                    <span class="text-5xl font-display font-bold tracking-tight text-white">49€</span>
                    <span class="text-sm font-semibold leading-6 tracking-wide text-slate-500">/mois</span>
                  </p>
                  <router-link to="/register" class="mt-10 block w-full rounded-xl bg-indigo-500 px-3 py-3 text-center text-sm font-bold text-white shadow-sm hover:bg-indigo-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500 transition-colors">
                    Démarrer mon abonnement
                  </router-link>
                  <p class="mt-6 text-xs leading-5 text-slate-500">Mise en pause possible dès l'embauche.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- CTA Section -->
      <div class="relative isolate -z-10 mt-10">
        <div class="mx-auto max-w-7xl sm:px-6 lg:px-8">
            <div class="mx-auto flex max-w-2xl flex-col gap-16 bg-surface-900 px-6 py-16 ring-1 ring-white/10 sm:rounded-3xl sm:p-8 lg:mx-0 lg:max-w-none lg:flex-row lg:items-center lg:py-20 xl:gap-x-20 xl:px-20 relative overflow-hidden">
                <div class="absolute -top-24 -right-24 w-96 h-96 bg-indigo-500/20 blur-[100px] rounded-full pointer-events-none"></div>
                
                <h2 class="text-3xl font-display font-bold tracking-tight text-white sm:text-4xl">
                    Prêt à décrocher le job de vos rêves ?
                </h2>
                <div class="w-full lg:w-auto lg:flex-auto">
                    <p class="mb-8 text-lg leading-8 text-slate-400">
                        Rejoignez les professionnels qui utilisent l'IA pour prendre l'avantage sur le marché du travail.
                    </p>
                    <div class="flex gap-4">
                        <router-link to="/register" class="rounded-xl bg-white px-6 py-3.5 text-sm font-bold text-surface-950 shadow-sm hover:bg-slate-100 transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white">
                            Créer mon compte
                        </router-link>
                        <router-link to="/login" class="rounded-xl border border-surface-700 bg-transparent px-6 py-3.5 text-sm font-bold text-white shadow-sm hover:bg-surface-800 transition-colors">
                            Se connecter
                        </router-link>
                    </div>
                </div>
            </div>
        </div>
      </div>
      
      <!-- Footer -->
      <footer class="mt-32 border-t border-surface-800 bg-surface-950 sm:mt-40">
        <div class="mx-auto max-w-7xl px-6 py-12 md:flex md:items-center md:justify-between lg:px-8">
          <div class="flex justify-center space-x-6 md:order-2">
            <div class="flex items-center gap-2">
                <ShieldCheckIcon class="w-5 h-5 text-slate-500" />
                <span class="text-xs text-slate-500">Sécurisé & Privé</span>
            </div>
          </div>
          <div class="mt-8 md:order-1 md:mt-0">
            <p class="text-center text-xs leading-5 text-slate-500">&copy; 2026 GoldArmy Agent AI. All rights reserved.</p>
          </div>
        </div>
      </footer>

    </main>
  </div>
</template>
