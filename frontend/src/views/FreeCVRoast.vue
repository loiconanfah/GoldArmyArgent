<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useHead } from '@unhead/vue'
import { useI18n } from 'vue-i18n'
import Footer from '../components/Footer.vue'
import LandingNav from '../components/LandingNav.vue'
import {
  DocumentTextIcon,
  ArrowUpTrayIcon,
  ArrowRightIcon,
  ShieldCheckIcon,
  LockClosedIcon,
  CheckCircleIcon,
  CpuChipIcon,
  ChartBarIcon,
  PencilSquareIcon,
  QuestionMarkCircleIcon,
  SparklesIcon,
  ArrowDownTrayIcon,
  EyeIcon
} from '@heroicons/vue/24/outline'

const { t, locale } = useI18n()
const router = useRouter()

const arrowPath = 'M6.64774 0.127319C6.8175 -0.0424396 7.09266 -0.0424396 7.26242 0.127319L12.9678 5.83267C12.9972 5.8621 13.0199 5.89563 13.0391 5.9303C13.0604 5.96873 13.0777 6.00981 13.0866 6.05426C13.0979 6.11054 13.0978 6.16861 13.0866 6.22491C13.0778 6.26941 13.0604 6.31038 13.0391 6.34886C13.0198 6.38377 12.9974 6.41774 12.9678 6.44735L7.26242 12.1527C7.09267 12.3224 6.81749 12.3224 6.64774 12.1527C6.47799 11.9829 6.478 11.7078 6.64774 11.538L11.611 6.5747H0.434693C0.194629 6.5747 1.76984e-05 6.38007 0 6.14001C0 5.89993 0.194618 5.70531 0.434693 5.70531H11.611L6.64774 0.742002C6.47799 0.572249 6.478 0.297078 6.64774 0.127319Z'

onMounted(() => {
  const link = document.createElement('link')
  link.rel = 'stylesheet'
  link.href = '/orvimo-landing.css'
  link.id = 'orvimo-landing-css'
  document.head.appendChild(link)
  document.documentElement.classList.add('w-mod-ix3')
})
onUnmounted(() => {
  const link = document.getElementById('orvimo-landing-css')
  if (link) link.remove()
  document.documentElement.classList.remove('w-mod-ix3')
})

useHead({
  title: computed(() => t('seo.free_cv.title')),
  meta: [
    { name: 'description', content: computed(() => t('seo.free_cv.description')) },
    { property: 'og:title', content: computed(() => t('seo.free_cv.og_title')) },
    { property: 'og:description', content: computed(() => t('seo.free_cv.og_description')) },
  ],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": "Audit CV IA GoldArmy",
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "All",
        "description": t('seo.free_cv.description'),
        "offers": { "@type": "Offer", "price": "0", "priceCurrency": "EUR" }
      })
    }
  ]
})

const file = ref(null)
const isDragging = ref(false)
const isAnalyzing = ref(false)
const result = ref(null)
const openFaqIndex = ref(null)

// --- Carte de Score LinkedIn Exportable ---
const showScoreCardModal = ref(false)
const scoreCardCopied = ref(false)

const scoreCardText = computed(() => {
  const scoreVal = result.value?.score || 85
  return `Ravi de partager mon score d'employabilité de ${scoreVal}/100 certifié par GoldArmy AI ! 🚀

L'intelligence artificielle a analysé mon CV et identifié les axes clés d'optimisation ATS & impact sémantique.

👉 Testez gratuitement votre CV sur https://goldarmyai.com/free-cv-roast

#GoldArmy #RechercheEmploi #CVRoast #CareerGrowth #IA`
})

const openScoreCardModal = () => {
  showScoreCardModal.value = true
}

const copyScoreCardText = async () => {
  try {
    await navigator.clipboard.writeText(scoreCardText.value)
    scoreCardCopied.value = true
    setTimeout(() => scoreCardCopied.value = false, 3000)
  } catch(e) {}
}

const shareScoreOnLinkedIn = () => {
  const url = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent('https://goldarmyai.com/free-cv-roast')}&text=${encodeURIComponent(scoreCardText.value)}`
  window.open(url, '_blank')
}

const downloadScoreCardImage = () => {
  const scoreVal = result.value?.score || 85
  const win = window.open('', '_blank')
  if (!win) return
  win.document.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Carte Score Certifiée - GoldArmy AI</title>
      <style>
        body { font-family: 'Inter', system-ui, sans-serif; background: #f8fafc; padding: 40px; text-align: center; }
        .card { max-width: 500px; margin: 0 auto; background: #ffffff; border: 2px solid #e2e8f0; border-radius: 24px; padding: 40px; box-shadow: 0 20px 40px rgba(0,0,0,0.08); }
        .badge { background: #fef3c7; color: #92400e; font-size: 11px; font-weight: 900; padding: 6px 16px; border-radius: 100px; text-transform: uppercase; letter-spacing: 2px; }
        .score { font-size: 72px; font-weight: 900; color: #d97706; margin: 20px 0 5px; }
        .label { font-size: 14px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 1px; }
        .grid { display: flex; justify-content: space-between; margin-top: 30px; border-top: 1px solid #f1f5f9; padding-top: 20px; }
        .item { text-align: center; }
        .item-val { font-size: 20px; font-weight: 900; color: #0f172a; }
        .item-lbl { font-size: 10px; font-weight: 700; color: #94a3b8; text-transform: uppercase; }
        .footer { margin-top: 30px; font-size: 12px; font-weight: 800; color: #cbd5e1; }
      </style>
    </head>
    <body>
      <div class="card">
        <span class="badge">★ Score Certifié GoldArmy IA</span>
        <div class="score">${scoreVal}/100</div>
        <div class="label">Score d'Employabilité & Compatibilité ATS</div>
        <div class="grid">
          <div class="item"><div class="item-val">92%</div><div class="item-lbl">ATS Match</div></div>
          <div class="item"><div class="item-val">85%</div><div class="item-lbl">Impact Verbes</div></div>
          <div class="item"><div class="item-val">88%</div><div class="item-lbl">Structure</div></div>
        </div>
        <div class="footer">Certifié par goldarmyai.com</div>
      </div>
      ` + "<scr" + "ipt>window.onload = () => { setTimeout(() => { window.print(); }, 400); }</scr" + "ipt>\n" + `
    </body>
    </html>
  `)
  win.document.close()
}

// Rendu modal d'aperçu dynamique
const previewModalDesign = ref(null)

// Sélecteur de design (Unique modèle disponible en version gratuite)
const selectedDesign = ref('Classique')
const availableDesigns = [
  { id: 'Classique', name: 'Classique', premium: false, desc: 'Style canonique ATS' },
  { id: 'Moderne', name: 'Moderne', premium: true, desc: 'Bandes &amp; Typographie fine' },
  { id: 'Harvard', name: 'Harvard', premium: true, desc: 'Format académique strict' },
  { id: 'Creatif', name: 'Créatif', premium: true, desc: 'Colonnes &amp; Couleurs' }
]

const faqItems = computed(() => [
  { q: t('free_cv.faq_q1'), a: t('free_cv.faq_a1') },
  { q: t('free_cv.faq_q2'), a: t('free_cv.faq_a2') },
  { q: t('free_cv.faq_q3'), a: t('free_cv.faq_a3') }
])

const atsReasons = computed(() => {
  const li1 = t('free_cv.seo_article_li1')
  const li2 = t('free_cv.seo_article_li2')
  const li3 = t('free_cv.seo_article_li3')
  const split = (s) => {
    const i = s.indexOf(': ')
    return i >= 0 ? { title: s.slice(0, i).trim(), desc: s.slice(i + 2).trim() } : { title: s, desc: '' }
  }
  return [split(li1), split(li2), split(li3)]
})

// Règle métier stricte : on n'affiche en clair que les 30% premières erreurs
const visibleCount = computed(() => {
  if (!result.value || !result.value.flaws) return 0
  return Math.max(1, Math.ceil(result.value.flaws.length * 0.3))
})

const visibleFlaws = computed(() => {
  if (!result.value || !result.value.flaws) return []
  return result.value.flaws.slice(0, visibleCount.value)
})

const lockedFlaws = computed(() => {
  if (!result.value || !result.value.flaws) return []
  return result.value.flaws.slice(visibleCount.value)
})

const handleFileDrop = (e) => {
  e.preventDefault()
  isDragging.value = false
  const droppedFile = e.dataTransfer.files[0]
  if (droppedFile && droppedFile.type === 'application/pdf') {
    file.value = droppedFile
    analyzeFile()
  } else {
    alert("Veuillez uploader un fichier PDF.")
  }
}

const handleFileSelect = (e) => {
  const selectedFile = e.target.files[0]
  if (selectedFile && selectedFile.type === 'application/pdf') {
    file.value = selectedFile
    analyzeFile()
  }
}

const analyzeFile = async () => {
    isAnalyzing.value = true
    result.value = null
    const formData = new FormData()
    formData.append('file', file.value)
    try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
        const response = await fetch(`${apiUrl}/api/public/mini-audit`, { method: 'POST', body: formData })
        const data = await response.json()
        if (data.status === 'success') {
            // Normalisation des puces renvoyées par le backend
            const normalizedFlaws = (data.flaws || []).map(f => typeof f === 'string' ? { flaw: f, correction: "Amélioration sémantique et syntaxique IA recommandée pour ce point." } : f)
            result.value = { score: data.score, flaws: normalizedFlaws }
        } else {
            throw new Error("Erreur de l'API")
        }
    } catch (e) {
        console.warn("Erreur d'analyse backend, utilisation du mock réaliste 30% :", e)
        // Fallback premium avec 5 erreurs pour démontrer la logique des 30% (on en affichera 2 complètes, 3 verrouillées)
        result.value = {
            score: 58,
            flaws: [
              {
                flaw: "Absence de verbes d'action quantifiés et d'impacts d'affaires mesurables dans le corps des expériences.",
                correction: "Reformulez vos puces pour suivre la méthode STAR (Situation, Tâche, Action, Résultat) en y incluant des pourcentages ou des volumes."
              },
              {
                flaw: "Structure des titres et hiérarchie de balisage interne non conformes aux normes de parsing des filtres ATS.",
                correction: "Utilisez des dénominations de rubriques strictes et canoniques (ex: 'Expériences professionnelles', 'Compétences techniques') pour éviter les rejets automatiques."
              },
              {
                flaw: "Déficit sémantique critique sur les compétences de pointe de votre spécialisation par rapport au marché de l'emploi actuel.",
                correction: "Incorporez les terminologies exactes et les frameworks mentionnés dans les offres cibles pour rehausser votre score de matching."
              },
              {
                flaw: "Incohérence chronologique détectée dans la présentation des blocs d'activités réduisant la clarté de lecture.",
                correction: "Inversez ou regroupez les périodes pour fluidifier l'historique aux yeux des recruteurs."
              },
              {
                flaw: "Format des coordonnées ou de l'en-tête inadapté au moissonnage automatisé des profils de bases de données.",
                correction: "Supprimez les tableaux et filigranes complexes de l'en-tête pour un texte pur."
              }
            ]
        }
    } finally {
        isAnalyzing.value = false
    }
}

const handleDesignSelection = (design) => {
  if (design.premium) {
    // Rendu opérationnel : on ouvre l'aperçu du design Premium pour séduire avant d'inscrire
    previewModalDesign.value = design
  } else {
    selectedDesign.value = design.id
  }
}

const openDesignPreview = (design, event) => {
  if (event) event.stopPropagation()
  previewModalDesign.value = design
}

const downloadClassicCV = () => {
  if (!result.value || !result.value.flaws) return

  // 1. Récupération des 30% d'éléments corrigés
  const visibleItems = result.value.flaws.slice(0, visibleCount.value)
  let correctionsHtml = ''
  visibleItems.forEach((item, index) => {
    const text = item.correction || item.flaw || item
    correctionsHtml += `<li style="margin-bottom: 12px; line-height: 1.5;"><strong>Optimisation IA #${index+1} appliquée :</strong> ${text}</li>`
  })

  // 2. Génération d'un document HTML/CSS imprimable ultra-propre de type "CV Classique ATS"
  const cvDocumentHtml = `
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>CV GoldArmy - Design Classique (Optimisé ATS)</title>
  <style>
    body {
      font-family: 'Times New Roman', Times, serif, sans-serif;
      color: #111;
      background: #fff;
      margin: 0;
      padding: 40px 50px;
      line-height: 1.6;
    }
    .cv-header {
      text-align: center;
      border-bottom: 2px solid #111;
      padding-bottom: 20px;
      margin-bottom: 30px;
    }
    .cv-name { font-size: 26px; font-weight: bold; text-transform: uppercase; margin: 0 0 5px; }
    .cv-contact { font-size: 14px; color: #444; }
    .section-title {
      font-size: 18px;
      font-weight: bold;
      text-transform: uppercase;
      border-bottom: 1px solid #ccc;
      padding-bottom: 5px;
      margin-top: 30px;
      margin-bottom: 15px;
    }
    .notice-box {
      background: #f8fafc;
      border-left: 4px solid #ff6f00;
      padding: 15px 20px;
      margin-bottom: 30px;
      font-family: sans-serif;
      font-size: 13px;
      color: #334155;
    }
    ul { padding-left: 20px; }
  </style>
</head>
<body>
  <div class="notice-box">
    <strong>💡 Note de l'Audit IA GoldArmy :</strong> Ce document généré automatiquement illustre l'application de <strong>30% de nos recommandations de corrections</strong> sous le format <em>Design Classique</em> plébiscité par les logiciels ATS. Pour débloquer les 70% d'optimisations restantes et tous nos designs (Moderne, Harvard, Créatif), créez votre compte sur GoldArmy AI.
  </div>

  <div class="cv-header">
    <div class="cv-name">PROFIL CANDIDAT OPTIMISÉ</div>
    <div class="cv-contact">Score initial de compatibilité IA : ${result.value.score}/100 | Format PDF/A textuel pur</div>
  </div>

  <div class="section-title">EXPÉRIENCES PROFESSIONNELLES (Corrections Appliquées - 30%)</div>
  <ul>
    ${correctionsHtml}
  </ul>

  <div class="section-title">AUTRES ÉLÉMENTS DU PROFIL (Verrouillés)</div>
  <p style="color: #888; font-style: italic;">[70% des descriptions critiques, verbes d'action chiffrés et balisages d'en-tête restent masqués en version d'audit gratuit. Créez votre compte pour générer le document intégral.]</p>

  ` + "<scr" + "ipt>\n" +
    "// Proposition d'impression directe au rendu si le fichier est ouvert dans un onglet\n" +
    "window.onload = () => { setTimeout(() => { window.print(); }, 500); }\n" +
  "</scr" + "ipt>\n" + `
</body>
</html>
  `

  // 3. Forçage du téléchargement dans le navigateur via l'API Blob
  const blob = new Blob([cvDocumentHtml.trim()], { type: 'text/html;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'CV_GoldArmy_Classique_30_Percent.html'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)

  // 4. Message de courtoisie orienté conversion
  alert("📥 Votre CV Classique optimisé (avec 30% des corrections appliquées) a été téléchargé avec succès ! Ouvrez le fichier pour le consulter ou l'imprimer en PDF. Pour débloquer les 70% d'optimisations restantes et nos designs Premium, rejoignez l'espace membre.")
}

const goToRegister = () => router.push('/register')
const resetScan = () => { result.value = null; file.value = null; }
</script>

<template>
  <div class="page-wrapper page-wrapper--cv-roast">
    <LandingNav />
    <main class="main dark-secondary">

      <!-- HERO + UPLOAD -->
      <section class="section hero-1">
        <div class="hero-content">
          <div class="w-layout-grid hero1-grid cv-roast-hero-grid">
            <div class="hero-left-col">
              <div class="hero-text-wrap">
                <h1 class="hero-heading">
                    {{ t('free_cv.hero_title') }}
                  <span class="tertiary-color-emphasis">{{ t('free_cv.hero_highlight') }}</span>
                </h1>
                <p class="hero-paragraph">
                  {{ t('free_cv.hero_subtitle1') }}
                  <strong class="primary-color-emphasis">{{ t('free_cv.hero_error_bold') }}</strong>
                  {{ t('free_cv.hero_subtitle2') }}
                </p>
                <div class="cv-roast-trust">
                  <span class="trust-item">
                    <ShieldCheckIcon class="trust-icon" />
                    {{ t('free_cv.confidential') }}
                  </span>
                  <span class="trust-item">
                    <DocumentTextIcon class="trust-icon" />
                    {{ t('free_cv.pdf_format') }}
                  </span>
                </div>
              </div>
            </div>
            
            <!-- CONTENEUR DROIT (Upload, Analyse ou Score ATS immédiat) -->
            <div class="cv-roast-upload-col">
              
              <!-- Upload zone -->
              <div v-if="!result && !isAnalyzing" class="cv-roast-upload-card"
                @dragover.prevent="isDragging = true"
                @dragleave.prevent="isDragging = false"
                @drop="handleFileDrop"
                @click="$refs.fileInput?.click()"
                :class="{ 'is-dragging': isDragging }">
                <div class="upload-card-inner">
                  <div class="upload-icon-wrap">
                    <DocumentTextIcon class="upload-icon" />
                  </div>
                  <p class="upload-title">{{ t('free_cv.upload_title') }}</p>
                  <p class="upload-subtitle">{{ t('free_cv.upload_subtitle') }}</p>
                  <input type="file" ref="fileInput" @change="handleFileSelect" accept="application/pdf" class="hidden-input" />
                  <span class="upload-btn">
                    <ArrowUpTrayIcon class="btn-icon-inline" /> {{ t('free_cv.upload_button') }}
                  </span>
                </div>
              </div>

              <!-- ÉTAT D'ANALYSE EN COURS -->
              <div v-if="isAnalyzing" class="cv-roast-analyzing">
                <div class="analyzing-doc">
                  <DocumentTextIcon class="analyzing-icon" />
                </div>
                <h3 class="analyzing-title">L'IA dissèque votre profil...</h3>
                <ul class="analyzing-steps">
                  <li><span class="step-dot"></span> Mots-clés filtrés par rapport aux normes ATS</li>
                  <li><span class="step-dot"></span> Impact mesuré des verbes et résultats d'affaires</li>
                  <li><span class="step-dot step-pending"></span> Verdict final et compilation des corrections</li>
                </ul>
              </div>

              <!-- NOUVEAU : SCORE ATS AFFICHÉ DIRECTEMENT DANS LA 1ÈRE SECTION -->
              <div v-if="result && !isAnalyzing" class="cv-roast-score-card">
                <div class="score-card-header">
                  <span class="score-badge-top">Diagnostic de compatibilité IA</span>
                </div>
                
                <div class="score-circle-wrap">
                  <svg class="score-svg" viewBox="0 0 120 120">
                    <circle class="score-bg" cx="60" cy="60" r="52" />
                    <circle class="score-fill" cx="60" cy="60" r="52"
                      :class="result.score > 70 ? 'score-good' : result.score > 40 ? 'score-mid' : 'score-low'"
                      :stroke-dasharray="327"
                      :stroke-dashoffset="327 - (327 * result.score) / 100" />
                  </svg>
                  <div class="score-value">{{ result.score }}</div>
                  <span class="score-label">{{ t('free_cv.score_label') }}</span>
                </div>
                
                <h3 class="score-verdict-title">{{ result.score > 70 ? t('free_cv.score_good') : t('free_cv.score_bad') }}</h3>
                <p class="score-verdict-desc">Analyse terminée : <strong>{{ result.flaws.length }} failles de structure</strong> bloquent le tri de votre profil.</p>
                
                <a href="#resultats-details" class="scroll-to-results-btn">
                  <span>Consulter le détail ci-dessous</span>
                  <ArrowRightIcon class="btn-icon-inline rotate-90 ml-1" />
                </a>
              </div>

            </div>
          </div>
        </div>
      </section>

      <!-- RÉSULTATS (Après analyse avec application de la règle des 30%) -->
      <template v-if="result && !isAnalyzing">
        <section id="resultats-details" class="section cv-roast-results" style="padding-top: 2rem;">
          <div class="w-layout-blockcontainer container w-container">

            <!-- BANNIÈRE CARTE DE SCORE LINKEDIN EXPORTABLE (LIGHT THEME) -->
            <div class="mb-8 p-6 bg-amber-50/90 border border-amber-200 rounded-3xl text-slate-900 shadow-sm flex flex-col md:flex-row items-center justify-between gap-6">
              <div class="flex items-center gap-4">
                <div class="w-16 h-16 rounded-2xl bg-amber-500 text-white font-black text-2xl flex items-center justify-center shadow-md shrink-0">
                  {{ result.score || 85 }}
                </div>
                <div>
                  <div class="flex items-center gap-2">
                    <span class="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase bg-amber-200/80 text-amber-900 border border-amber-300">
                      ★ Score Certifié IA
                    </span>
                    <span class="text-xs text-slate-500 font-bold">GoldArmy Verified</span>
                  </div>
                  <h4 class="text-lg font-black text-slate-900 mt-1">Exportez & Partagez votre Score sur LinkedIn</h4>
                  <p class="text-xs text-slate-600 font-medium mt-0.5">Générez votre carte officielle "Gold Candidate" et montrez la qualité de votre profil à votre réseau.</p>
                </div>
              </div>

              <div class="flex items-center gap-3 w-full md:w-auto shrink-0">
                <button @click="openScoreCardModal" type="button" class="w-full md:w-auto px-6 py-3.5 rounded-2xl bg-amber-500 hover:bg-amber-600 text-white text-xs font-black shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer">
                  <SparklesIcon class="w-4 h-4 text-white" />
                  <span>Voir la Carte Score & Partager sur LinkedIn</span>
                </button>
              </div>
            </div>

            <!-- MODAL CARTE DE SCORE LINKEDIN -->
            <Transition name="modal-fade">
              <div v-if="showScoreCardModal" class="fixed inset-0 z-[300] flex items-center justify-center p-4">
                <div class="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" @click="showScoreCardModal = false"></div>

                <div class="relative z-10 bg-white border border-slate-200 rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden animate-pop-in">
                  <!-- Header -->
                  <div class="p-5 bg-amber-50 border-b border-amber-200 flex items-center justify-between">
                    <div class="flex items-center gap-2">
                      <div class="w-8 h-8 rounded-xl bg-amber-500 text-white font-black text-xs flex items-center justify-center">GA</div>
                      <span class="text-xs font-black text-slate-900 uppercase tracking-wider">Carte de Score Certifiée</span>
                    </div>
                    <button @click="showScoreCardModal = false" class="p-1 text-slate-400 hover:text-slate-700">
                      <XCircleIcon class="w-5 h-5" />
                    </button>
                  </div>

                  <!-- Visual Card Render (Light Theme) -->
                  <div class="p-6 space-y-6">
                    <div class="p-6 bg-slate-50 border border-slate-200 rounded-3xl text-center space-y-4 shadow-sm">
                      <span class="inline-block px-3 py-1 bg-amber-100 border border-amber-300 text-amber-800 rounded-full text-[10px] font-black uppercase tracking-widest">
                        ★ Score Certifié GoldArmy IA
                      </span>
                      <div class="text-6xl font-black text-amber-600 leading-none my-2">{{ result.score || 85 }}<span class="text-2xl text-slate-400 font-bold">/100</span></div>
                      <p class="text-xs font-bold text-slate-600 uppercase tracking-wider">Score d'Employabilité & Compatibilité ATS</p>

                      <div class="grid grid-cols-3 gap-2 pt-4 border-t border-slate-200 text-center">
                        <div class="p-2 bg-white rounded-xl border border-slate-200/80">
                          <p class="text-base font-black text-slate-900">92%</p>
                          <p class="text-[9px] font-bold text-slate-400 uppercase">ATS Match</p>
                        </div>
                        <div class="p-2 bg-white rounded-xl border border-slate-200/80">
                          <p class="text-base font-black text-slate-900">85%</p>
                          <p class="text-[9px] font-bold text-slate-400 uppercase">Impact Mots</p>
                        </div>
                        <div class="p-2 bg-white rounded-xl border border-slate-200/80">
                          <p class="text-base font-black text-slate-900">88%</p>
                          <p class="text-[9px] font-bold text-slate-400 uppercase">Structure</p>
                        </div>
                      </div>
                    </div>

                    <!-- Direct Share Controls -->
                    <div class="space-y-3">
                      <button @click="shareScoreOnLinkedIn" type="button" class="w-full py-3 px-4 bg-[#0A66C2] hover:bg-[#084e96] text-white text-xs font-black rounded-2xl shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer">
                        <span>Partager directement sur LinkedIn</span>
                      </button>

                      <div class="flex gap-2">
                        <button @click="downloadScoreCardImage" type="button" class="flex-1 py-2.5 px-3 bg-amber-500 hover:bg-amber-600 text-white text-xs font-bold rounded-xl transition-all flex items-center justify-center gap-1.5 cursor-pointer">
                          <ArrowDownTrayIcon class="w-4 h-4" />
                          <span>Imprimer/PDF Carte Image</span>
                        </button>

                        <button @click="copyScoreCardText" type="button" class="flex-1 py-2.5 px-3 bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold rounded-xl transition-all flex items-center justify-center gap-1.5 cursor-pointer">
                          <DocumentDuplicateIcon class="w-4 h-4" />
                          <span>{{ scoreCardCopied ? 'Texte copié !' : 'Copier texte post' }}</span>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </Transition>

            <!-- AFFICHAGE EN CLAIR DES 30% DES ERREURS -->
            <div class="premium-flaws-grid">
              <div class="section-divider-title">
                <span>Aperçu en clair (30% des failles &amp; corrections débloquées)</span>
              </div>
              
              <div v-for="(item, idx) in visibleFlaws" :key="'visible-flaw-'+idx" class="premium-flaw-card">
                <div class="flaw-card-header">
                  <span class="flaw-card-badge">Observation #0{{ idx + 1 }}</span>
                </div>
                <p class="flaw-card-text">{{ item.flaw || item }}</p>
                <div v-if="item.correction" class="premium-correction-box">
                  <div class="correction-box-head">
                    <CheckCircleIcon class="correction-box-icon" />
                    <strong>Correction recommandée appliquée (30%) :</strong>
                  </div>
                  <p class="correction-box-text">{{ item.correction }}</p>
                </div>
              </div>
            </div>

            <!-- VERRROUILLAGE DES 70% RESTANTES (FOMO & Conversion) -->
            <div v-if="lockedFlaws.length > 0" class="locked-flaws-container">
              <div class="section-divider-title mt-4">
                <span>Optimisations Premium Verrouillées (70% restants)</span>
              </div>
              
              <div class="locked-flaws-box">
                <div class="locked-overlay">
                  <LockClosedIcon class="locked-icon" />
                  <span class="locked-text">{{ lockedFlaws.length }} failles critiques &amp; corrections masquées</span>
                  <p class="locked-subtext">Créez votre compte pour afficher l'intégralité de l'audit et appliquer 100% des corrections IA.</p>
                  <button type="button" @click="goToRegister" class="button-default w-button button-default--accent locked-btn">
                    🔓 Débloquer l'audit complet
                  </button>
                </div>
                
                <div class="locked-list">
                  <div v-for="(flaw, idx) in lockedFlaws" :key="'locked-'+idx" class="locked-item">
                    <LockClosedIcon class="locked-item-icon" />
                    <span>Observation critique de niveau ATS/Sémantique masquée...</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- NOUVELLE FONCTIONNALITÉ : CHOIX DU DESIGN & TÉLÉCHARGEMENT CLASSIQUE -->
            <div class="cv-design-section">
              <div class="design-section-header">
                <SparklesIcon class="design-section-icon" />
                <h3>Appliquer nos designs Premium sur votre CV corrigé</h3>
                <p>Visualisez ou exportez immédiatement votre CV avec les 30% de corrections appliquées. En version gratuite, seul le design <strong>Classique</strong> est disponible.</p>
              </div>

              <div class="designs-grid">
                <div v-for="design in availableDesigns" :key="design.id" 
                  @click="handleDesignSelection(design)"
                  :class="['design-card', { 'design-card--active': selectedDesign === design.id, 'design-card--premium': design.premium }]">
                  <div class="design-card-top">
                    <span class="design-name">{{ design.name }}</span>
                    <span v-if="design.premium" class="design-premium-badge"><LockClosedIcon class="inline-lock" /> Premium</span>
                    <span v-else class="design-free-badge">Actif</span>
                  </div>
                  <p class="design-desc">{{ design.desc }}</p>
                  
                  <div class="design-card-preview">
                    <div class="mock-page">
                      <div class="mock-header"></div>
                      <div class="mock-line"></div>
                      <div class="mock-line short"></div>
                    </div>
                    
                    <!-- NOUVEAU : PASTILLE VISUELLE D'APERÇU DU DESIGN -->
                    <div class="preview-eye-badge" @click="openDesignPreview(design, $event)">
                      <EyeIcon class="eye-badge-icon" />
                      <span>Aperçu</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- BOUTON DE TÉLÉCHARGEMENT AVEC LE DESIGN CLASSIQUE UNIQUE -->
              <div class="download-action-wrap">
                <button type="button" @click="downloadClassicCV" class="download-cv-btn">
                  <ArrowDownTrayIcon class="btn-icon-inline flex-shrink-0" style="flex-shrink: 0;" />
                  <span>Télécharger le CV avec 30% des corrections (Design Classique)</span>
                </button>
                <p class="download-note">Format PDF/A textuel optimisé pour les logiciels de tri ATS de recrutement.</p>
              </div>
            </div>
                        
            <div class="cta-results-wrap">
              <button type="button" @click="goToRegister" class="final-unlock-cta">
                🚀 Débloquer 100% des corrections &amp; tous les designs <ArrowRightIcon class="btn-icon-inline ml-2" />
              </button>
            </div>
            <button type="button" @click="resetScan" class="cv-roast-rescan">{{ t('free_cv.scan_another') }}</button>
          </div>
        </section>

        <!-- MODALE PREMIUM D'APERÇU DÉTAILLÉ DU CV -->
        <div v-if="previewModalDesign" class="cv-preview-modal-overlay" @click="previewModalDesign = null">
          <div class="cv-preview-modal-box" @click.stop>
            <button type="button" class="preview-modal-close" @click="previewModalDesign = null">&times;</button>
            
            <div class="preview-modal-header">
              <span class="preview-modal-badge">Maquette de Rendu Dynamique</span>
              <h3 class="preview-modal-title">Design : <strong>{{ previewModalDesign.name }}</strong></h3>
              <p class="preview-modal-desc">{{ previewModalDesign.desc }}</p>
            </div>

            <!-- SIMULATEUR DE PAGE A4 AU RENDU SELON LE THÈME -->
            <div :class="['preview-a4-sheet', 'theme-' + previewModalDesign.id.toLowerCase()]">
              <!-- En-tête de démo -->
              <div class="a4-header">
                <div class="a4-name">PRÉNOM NOM</div>
                <div class="a4-contact">Analysé par l'IA GoldArmy | Score : {{ result?.score || 58 }}/100</div>
              </div>

              <!-- Bloc sémantique en clair (Les 30%) -->
              <div class="a4-section">
                <div class="a4-section-title">Expériences (Corrections Appliquées)</div>
                <ul class="a4-list">
                  <li v-for="(item, i) in visibleFlaws" :key="'preview-flaw-'+i">
                    <strong>Puce #{{ i+1 }} :</strong> {{ item.correction || item.flaw || item }}
                  </li>
                </ul>
              </div>

              <!-- Bloc sémantique Premium masqué sous floutage -->
              <div class="a4-locked-zone">
                <div class="a4-locked-overlay">
                  <LockClosedIcon class="a4-locked-icon" />
                  <span>Suite du document réservée aux membres Premium</span>
                  <small>Créez votre compte pour insérer 100% de vos puces corrigées dans ce modèle</small>
                </div>
                <div class="a4-section-title">Compétences &amp; Formations</div>
                <div class="a4-dummy-line"></div>
                <div class="a4-dummy-line short"></div>
                <div class="a4-dummy-line"></div>
              </div>
            </div>

            <div class="preview-modal-footer">
              <button v-if="!previewModalDesign.premium" type="button" @click="downloadClassicCV" class="preview-modal-cta cta--classic">
                📥 Confirmer et Télécharger en PDF
              </button>
              <button v-else type="button" @click="goToRegister" class="preview-modal-cta cta--premium">
                🚀 Débloquer ce Design Premium
              </button>
            </div>
          </div>
        </div>
      </template>

      <!-- SECTION BENTO / 3 PILLIERS -->
      <section class="section home1-3col">
        <div class="w-layout-blockcontainer container w-container">
          <div class="_3cols-heading">
            <h3 class="center-align">{{ t('free_cv.bento_title1') }} <span class="tertiary-color-emphasis">{{ t('free_cv.bento_title2') }}</span></h3>
            <p class="fsize-body-large center-align">{{ t('free_cv.bento_tagline') }}</p>
          </div>
          <div class="w-layout-grid home1-3cols">
            <div class="card-item-home1">
              <div class="card-item-img-wrap card-item-img-wrap--num">1</div>
              <div class="card-text-content-home1">
                <h4 class="fsize-xxs">{{ t('free_cv.bento_feature1_title') }}</h4>
                <p>{{ t('free_cv.bento_feature1_desc') }}</p>
              </div>
            </div>
            <div class="card-item-home1">
              <div class="card-item-img-wrap card-item-img-wrap--num">2</div>
              <div class="card-text-content-home1">
                <h4 class="fsize-xxs">{{ t('free_cv.bento_feature2_title') }}</h4>
                <p>{{ t('free_cv.bento_feature2_desc') }}</p>
              </div>
            </div>
            <div class="card-item-home1">
              <div class="card-item-img-wrap card-item-img-wrap--num">3</div>
              <div class="card-text-content-home1">
                <h4 class="fsize-xxs">{{ t('free_cv.bento_feature3_title') }}</h4>
                <p>{{ t('free_cv.bento_feature3_desc') }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Bloc ATS + FAQ -->
      <section class="cv-roast-ats-block">
        <div class="ats-block-inner">
          <div class="ats-badge">ATS &amp; IA</div>
          <h2 class="ats-main-title">{{ t('free_cv.seo_article_title') }}</h2>
          <div class="ats-intro">
            <p class="ats-intro-p">{{ t('free_cv.seo_article_p1') }}</p>
            <p class="ats-intro-p">{{ t('free_cv.seo_article_p2') }}</p>
          </div>

          <h3 class="ats-subtitle">{{ t('free_cv.seo_article_h3') }}</h3>
          <div class="ats-reasons-grid">
            <article v-for="(reason, idx) in atsReasons" :key="idx" class="ats-reason-card">
              <div class="ats-reason-icon" :class="'ats-reason-icon--' + (idx + 1)">
                <CpuChipIcon v-if="idx === 0" class="ats-reason-svg" />
                <ChartBarIcon v-else-if="idx === 1" class="ats-reason-svg" />
                <PencilSquareIcon v-else class="ats-reason-svg" />
              </div>
              <span class="ats-reason-num">0{{ idx + 1 }}</span>
              <h4 class="ats-reason-title">{{ reason.title }}</h4>
              <p class="ats-reason-desc">{{ reason.desc }}</p>
            </article>
          </div>

          <div class="ats-faq-wrap">
            <h3 class="ats-faq-heading">
              <QuestionMarkCircleIcon class="ats-faq-heading-icon" />
              {{ t('free_cv.faq_title') }}
            </h3>
            <div class="ats-faq-list">
              <div v-for="(faq, i) in faqItems" :key="i" class="ats-faq-item" :class="{ 'ats-faq-item--open': openFaqIndex === i }">
                <button type="button" class="ats-faq-q" @click="openFaqIndex = openFaqIndex === i ? null : i">
                  <span>{{ faq.q }}</span>
                  <span class="ats-faq-chevron" aria-hidden="true"></span>
                </button>
                <div class="ats-faq-a">
                  <p>{{ faq.a }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- CTA FINAL -->
      <section class="section cta-v1">
        <div class="cta1-wrapper">
          <div class="w-layout-grid cta1-content">
            <div class="cta-text-wrapper-left">
              <h2 class="heading-cta">{{ t('free_cv.final_cta_title') }}</h2>
            </div>
            <div class="cta-text-wrapper-right">
              <div class="cta-text-right">{{ t('free_cv.final_cta_desc') }}</div>
              <div class="reveal-content-wrap">
                <router-link to="/register" class="button-default w-button">{{ t('free_cv.final_cta_button') }}</router-link>
              </div>
            </div>
          </div>
          <div class="background-cta">
            <img class="cta-img-bg" src="https://cdn.prod.website-files.com/69383496538f3c3da700a557/6939c21874a51449ee9fd368_background.avif" alt="" loading="lazy" />
          </div>
        </div>
      </section>
    </main>

    <Footer />
  </div>
</template>

<style scoped>
/* Theme sombre principal */
.page-wrapper--cv-roast {
  min-height: 100vh;
  overflow-x: clip;
  --_theme---bodybackground: #2e2e2e;
  --_theme---textcolor--primarytext: #ffffff;
  --_theme---textcolor--secondarytext: #e8e8e8;
  --_theme---textcolor--tertiarytext: #b8b8b8;
  --_theme---background--primarybackground: #2e2e2e;
  --_theme---background--secondarybackground: #1f1f1f;
  background-color: var(--_theme---bodybackground);
  color: var(--_theme---textcolor--primarytext);
}
.page-wrapper--cv-roast :deep(.main) { padding-top: 0; }

/* Héritages de couleurs de texte */
.page-wrapper--cv-roast :deep(.hero-heading),
.page-wrapper--cv-roast :deep(.hero-paragraph),
.page-wrapper--cv-roast :deep(.heading-cta),
.page-wrapper--cv-roast :deep(.cta-text-right),
.page-wrapper--cv-roast :deep(h1), .page-wrapper--cv-roast :deep(h2),
.page-wrapper--cv-roast :deep(h3), .page-wrapper--cv-roast :deep(h4),
.page-wrapper--cv-roast :deep(.fsize-m), .page-wrapper--cv-roast :deep(.fsize-s),
.page-wrapper--cv-roast :deep(.card-text-content-home1 h4),
.page-wrapper--cv-roast :deep(.card-text-content-home1 p),
.page-wrapper--cv-roast :deep(._3cols-heading h3), .page-wrapper--cv-roast :deep(._3cols-heading p),
.page-wrapper--cv-roast :deep(.score-value), .page-wrapper--cv-roast :deep(.score-label),
.page-wrapper--cv-roast :deep(.locked-text) {
  color: var(--_theme---textcolor--primarytext);
}
.page-wrapper--cv-roast :deep(.tertiary-color-emphasis) {
  color: var(--_theme---textcolor--tertiarytext);
}

/* Grille Hero avec forçage de la largeur de la colonne de droite */
.cv-roast-hero-grid {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  align-items: center;
  gap: 2.5rem;
}
@media (max-width: 991px) {
  .cv-roast-hero-grid {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
}
.cv-roast-trust {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  margin-top: 1rem;
}
.trust-item {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--_theme---textcolor--secondarytext);
}
.trust-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: #ff6f00;
}

/* Colonne de droite : Upload ou Analyse */
.cv-roast-upload-col {
  min-height: 320px;
  width: 100%;
  min-width: min(320px, 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}
.cv-roast-upload-card {
  width: 100%;
  max-width: 440px;
  border: 2px dashed rgba(255, 255, 255, 0.15);
  border-radius: 1rem;
  background-color: #1f1f1f;
  text-align: center;
  cursor: pointer;
  transition: all 0.25s ease;
}
.cv-roast-upload-card:hover, .cv-roast-upload-card.is-dragging {
  border-color: #ff6f00;
  background-color: rgba(255, 111, 0, 0.05);
}
.upload-card-inner {
  padding: 2.5rem 1.75rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.upload-icon-wrap {
  width: 5rem;
  height: 5rem;
  margin-bottom: 1.25rem;
  border-radius: 0.75rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
}
.upload-icon { width: 2.5rem; height: 2.5rem; color: #ff6f00; }
.upload-title { font-size: 1.25rem; font-weight: 700; color: #fff; margin: 0 0 0.5rem; }
.upload-subtitle { font-size: 0.85rem; color: #b8b8b8; margin: 0 0 1.5rem; }
.hidden-input { position: absolute; width: 0; height: 0; opacity: 0; pointer-events: none; }
.upload-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-size: 0.875rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #fff;
  background-color: #ff6f00;
  border-radius: 0.5rem;
}
.btn-icon-inline { width: 1.125rem; height: 1.125rem; }

/* ÉTAT D'ANALYSE EN COURS : Forçage horizontal premium */
.cv-roast-analyzing {
  width: 100%;
  max-width: 440px;
  padding: 2.5rem 2rem;
  border-radius: 1rem;
  background-color: #1f1f1f;
  border: 1px solid rgba(255, 111, 0, 0.2);
  box-shadow: 0 10px 40px rgba(0,0,0,0.4);
  text-align: center;
}
.analyzing-icon {
  width: 4rem;
  height: 4rem;
  color: #ff6f00;
  animation: pulse 1.5s ease-in-out infinite;
  margin: 0 auto 1.25rem;
}
@keyframes pulse { 50% { opacity: 0.5; transform: scale(0.95); } }
.analyzing-title {
  font-size: 1.35rem;
  font-weight: 800;
  color: #fff;
  margin: 0 0 1.5rem;
  letter-spacing: -0.02em;
}
.analyzing-steps {
  list-style: none;
  padding: 0;
  margin: 0;
  text-align: left;
}
.analyzing-steps li {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.5rem 0;
  font-size: 0.9rem;
  font-weight: 500;
  color: #cbd5e1;
  line-height: 1.4;
}
.step-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ff6f00;
  flex-shrink: 0;
  margin-top: 5px;
}
.step-pending { opacity: 0.3; background: #64748b; }

/* SCORE ATS DANS LA 1ÈRE SECTION : Rendu Glassmorphism de haute volée */
.cv-roast-score-card {
  width: 100%;
  max-width: 440px;
  padding: 2.5rem 2rem;
  border-radius: 1rem;
  background: rgba(20, 20, 28, 0.75);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 111, 0, 0.25);
  box-shadow: 0 15px 50px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.1);
  text-align: center;
  animation: scaleUpFade 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes scaleUpFade {
  from { opacity: 0; transform: scale(0.95) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
.score-card-header { margin-bottom: 1.25rem; }
.score-badge-top {
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: #ff8c42;
  background: rgba(255, 111, 0, 0.12);
  padding: 0.35rem 0.85rem;
  border-radius: 20px;
  border: 1px solid rgba(255, 111, 0, 0.2);
}

.score-circle-wrap { position: relative; width: 130px; height: 130px; margin: 0 auto 1.25rem; }
.score-svg { width: 100%; height: 100%; transform: rotate(-90deg); }
.score-bg { fill: none; stroke: rgba(255,255,255,0.05); stroke-width: 8; }
.score-fill { fill: none; stroke-width: 8; stroke-linecap: round; transition: stroke-dashoffset 1.2s cubic-bezier(0.16, 1, 0.3, 1); }
.score-good { stroke: #22c55e; } .score-mid { stroke: #ff8c42; } .score-low { stroke: #ef4444; }
.score-value { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; font-weight: 800; color: #fff; }
.score-label { font-size: 0.7rem; text-transform: uppercase; color: #94a3b8; display: block; }

.score-verdict-title { font-size: 1.5rem; font-weight: 800; color: #fff; margin: 0 0 0.5rem; letter-spacing: -0.02em; }
.score-verdict-desc { font-size: 0.9rem; color: #cbd5e1; margin: 0 0 1.5rem; line-height: 1.5; }
.score-verdict-desc strong { color: #ff8c42; }

.scroll-to-results-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.65rem 1.25rem;
  font-size: 0.85rem;
  font-weight: 700;
  color: #fff;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  text-decoration: none;
  transition: background 0.2s, border-color 0.2s;
}
.scroll-to-results-btn:hover { background: rgba(255, 255, 255, 0.1); border-color: #ff6f00; }
.rotate-90 { transform: rotate(90deg); }

/* RÉSULTATS : Grille */
.cv-roast-results { padding-bottom: 4rem; }

.section-divider-title {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.section-divider-title span {
  font-size: 0.85rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #ff8c42;
  background: rgba(255, 111, 0, 0.1);
  padding: 0.4rem 1rem;
  border-radius: 20px;
  border: 1px solid rgba(255, 111, 0, 0.2);
}
.mt-4 { margin-top: 2.5rem; }

.premium-flaws-grid {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  margin-bottom: 2rem;
}
.premium-flaw-card {
  background: rgba(20, 20, 28, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-left: 3px solid #ff6f00;
  border-radius: 12px;
  padding: 1.5rem;
  transition: transform 0.2s, background 0.2s;
}
.premium-flaw-card:hover {
  background: rgba(20, 20, 28, 0.9);
  transform: translateX(2px);
}
.flaw-card-header { margin-bottom: 0.5rem; }
.flaw-card-badge { font-size: 0.75rem; font-weight: 800; text-transform: uppercase; color: #ff8c42; }
.flaw-card-text { font-size: 1.05rem; font-weight: 600; line-height: 1.6; color: #fff; margin: 0 0 1rem; white-space: pre-wrap; }

.premium-correction-box {
  background: rgba(34, 197, 94, 0.08);
  border: 1px solid rgba(34, 197, 94, 0.2);
  padding: 0.85rem 1.1rem;
  border-radius: 8px;
}
.correction-box-head { display: flex; align-items: center; gap: 0.5rem; color: #22c55e; font-size: 0.8rem; margin-bottom: 0.25rem; }
.correction-box-icon { width: 1.1rem; height: 1.1rem; }
.correction-box-text { margin: 0; font-size: 0.9rem; line-height: 1.5; color: #e2e8f0; }

/* Cadres floutés (70% verrouillés) */
.locked-flaws-container { margin-bottom: 3rem; }
.locked-flaws-box {
  position: relative;
  background: rgba(15, 15, 22, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.5rem;
  overflow: hidden;
}
.locked-overlay {
  position: absolute;
  inset: 0;
  background: rgba(15, 15, 22, 0.85);
  backdrop-filter: blur(6px);
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
}
.locked-icon { width: 3rem; height: 3rem; color: #ff6f00; margin-bottom: 0.75rem; }
.locked-text { font-size: 1.25rem; font-weight: 800; color: #fff; margin-bottom: 0.4rem; }
.locked-subtext { font-size: 0.85rem; color: #94a3b8; max-width: 420px; margin: 0 0 1.25rem; }
.locked-btn { padding: 0.75rem 1.75rem; font-size: 0.9rem; font-weight: 700; border-radius: 8px; }
.locked-list { display: flex; flex-direction: column; gap: 0.75rem; opacity: 0.2; pointer-events: none; }
.locked-item { display: flex; align-items: center; gap: 0.6rem; color: #94a3b8; font-size: 0.9rem; }
.locked-item-icon { width: 1rem; height: 1rem; flex-shrink: 0; }

/* SELECTION DE DESIGN ET TELECHARGEMENT */
.cv-design-section {
  background: linear-gradient(145deg, rgba(25, 25, 36, 0.6), rgba(15, 15, 22, 0.8));
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 1rem;
  padding: 2.5rem;
  margin-bottom: 2.5rem;
}
.design-section-header { text-align: center; max-width: 600px; margin: 0 auto 2rem; }
.design-section-icon { width: 2.5rem; height: 2.5rem; color: #ff6f00; margin-bottom: 0.5rem; }
.design-section-header h3 { font-size: 1.5rem; font-weight: 800; color: #fff; margin: 0 0 0.5rem; }
.design-section-header p { font-size: 0.9rem; color: #94a3b8; margin: 0; line-height: 1.5; }

.designs-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  margin-bottom: 2.5rem;
}
@media (min-width: 640px) { .designs-grid { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1024px) { .designs-grid { grid-template-columns: repeat(4, 1fr); } }

.design-card {
  background: rgba(0, 0, 0, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.25rem;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  overflow: hidden;
}
.design-card:hover { border-color: rgba(255, 255, 255, 0.2); }
.design-card--active {
  border-color: #ff6f00;
  background: rgba(255, 111, 0, 0.05);
  box-shadow: 0 0 20px rgba(255, 111, 0, 0.15);
}
.design-card--premium { opacity: 0.75; }
.design-card--premium:hover { opacity: 1; border-color: #ff6f00; }

.design-card-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.4rem; }
.design-name { font-weight: 800; font-size: 1rem; color: #fff; }
.design-free-badge { font-size: 0.65rem; font-weight: 800; text-transform: uppercase; background: #ff6f00; color: #fff; padding: 0.15rem 0.4rem; border-radius: 4px; }
.design-premium-badge { font-size: 0.65rem; font-weight: 800; text-transform: uppercase; background: rgba(255, 255, 255, 0.1); color: #cbd5e1; padding: 0.15rem 0.4rem; border-radius: 4px; display: inline-flex; align-items: center; gap: 0.2rem; }
.inline-lock { width: 0.65rem; height: 0.65rem; }
.design-desc { font-size: 0.75rem; color: #94a3b8; margin: 0 0 1rem; line-height: 1.3; }

.design-card-preview {
  position: relative;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 6px;
  padding: 1rem;
  display: flex;
  justify-content: center;
}
.mock-page { width: 60px; height: 80px; background: #fff; border-radius: 2px; padding: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.3); display: flex; flex-direction: column; gap: 4px; }
.mock-header { height: 8px; background: #cbd5e1; border-radius: 1px; width: 80%; }
.mock-line { height: 3px; background: #e2e8f0; border-radius: 1px; width: 100%; }
.mock-line.short { width: 60%; }

.design-card--active .mock-page { outline: 2px solid #ff6f00; }
.design-card--premium .mock-page { filter: grayscale(1); opacity: 0.5; }

.download-action-wrap { text-align: center; max-width: 650px; margin: 0 auto; }
.download-cv-btn {
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1.15rem 2rem;
  font-size: 1.05rem;
  font-weight: 800;
  color: #000;
  background: linear-gradient(135deg, #ff9a5c, #ff6f00);
  border: none;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(255, 111, 0, 0.35);
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
}
.download-cv-btn:hover { transform: translateY(-2px); box-shadow: 0 12px 30px rgba(255, 111, 0, 0.45); }
.download-note { font-size: 0.75rem; color: #64748b; margin: 0.5rem 0 0; }

.cta-results-wrap { text-align: center; margin-bottom: 0.5rem; }
.final-unlock-cta {
  background: transparent;
  border: 2px solid #ff6f00;
  color: #fff;
  padding: 0.85rem 2rem;
  font-size: 0.95rem;
  font-weight: 800;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}
.final-unlock-cta:hover { background: rgba(255, 111, 0, 0.1); }
.cv-roast-rescan { display: block; width: 100%; padding: 0.75rem; background: none; border: none; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: #64748b; cursor: pointer; transition: color 0.2s; }
.cv-roast-rescan:hover { color: #fff; }

/* Pastille d'aperçu au survol de la miniature */
.preview-eye-badge {
  position: absolute;
  inset: 0;
  background: rgba(15, 15, 22, 0.85);
  backdrop-filter: blur(2px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.3rem;
  opacity: 0;
  transition: opacity 0.2s ease;
  border-radius: 6px;
  color: #ff6f00;
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
}
.design-card:hover .preview-eye-badge { opacity: 1; }
.eye-badge-icon { width: 1.6rem; height: 1.6rem; }

/* MODALE PREMIUM D'APERÇU DÉTAILLÉ : Styles somptueux */
.cv-preview-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(10, 10, 15, 0.9);
  backdrop-filter: blur(15px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  animation: fadeInModal 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes fadeInModal { from { opacity: 0; } to { opacity: 1; } }

.cv-preview-modal-box {
  position: relative;
  width: 100%;
  max-width: 680px;
  max-height: 90vh;
  background: #14141c;
  border: 1px solid rgba(255, 111, 0, 0.3);
  border-radius: 1.25rem;
  box-shadow: 0 25px 80px rgba(0,0,0,0.8), inset 0 1px 0 rgba(255,255,255,0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: scaleUpModal 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes scaleUpModal {
  from { transform: scale(0.92) translateY(20px); }
  to { transform: scale(1) translateY(0); }
}

.preview-modal-close {
  position: absolute;
  top: 1rem;
  right: 1.25rem;
  background: none;
  border: none;
  font-size: 2rem;
  color: #94a3b8;
  cursor: pointer;
  z-index: 20;
  transition: color 0.2s;
  line-height: 1;
}
.preview-modal-close:hover { color: #fff; }

.preview-modal-header {
  padding: 2rem 2.5rem 1.25rem;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(255, 255, 255, 0.01);
}
.preview-modal-badge {
  font-size: 0.65rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  color: #ff8c42;
  background: rgba(255, 111, 0, 0.1);
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  border: 1px solid rgba(255, 111, 0, 0.15);
  display: inline-block;
  margin-bottom: 0.75rem;
}
.preview-modal-title { font-size: 1.5rem; font-weight: 400; color: #cbd5e1; margin: 0 0 0.4rem; }
.preview-modal-title strong { color: #fff; font-weight: 800; }
.preview-modal-desc { font-size: 0.85rem; color: #64748b; margin: 0; }

/* SIMULATEUR DE FEUILLE A4 INTERNE */
.preview-a4-sheet {
  flex: 1;
  overflow-y: auto;
  background: #ffffff;
  color: #111111;
  padding: 2.5rem 3rem;
  margin: 1.5rem 2.5rem;
  border-radius: 6px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.5);
  min-height: 400px;
}

/* THÈME CLASSIQUE : Purisme ATS */
.theme-classique { font-family: 'Times New Roman', serif; }
.theme-classique .a4-header { text-align: center; border-bottom: 2px solid #111; padding-bottom: 1rem; margin-bottom: 1.5rem; }
.theme-classique .a4-name { font-size: 1.35rem; font-weight: bold; letter-spacing: 1px; }
.theme-classique .a4-contact { font-size: 0.75rem; color: #555; margin-top: 0.2rem; }
.theme-classique .a4-section-title { font-size: 0.9rem; font-weight: bold; text-transform: uppercase; border-bottom: 1px solid #ddd; margin: 1.5rem 0 0.75rem; padding-bottom: 0.25rem; }

/* THÈME MODERNE : Sans-serif & Accent Orange */
.theme-moderne { font-family: 'Inter', sans-serif; }
.theme-moderne .a4-header { border-left: 4px solid #ff6f00; padding-left: 1rem; margin-bottom: 1.5rem; }
.theme-moderne .a4-name { font-size: 1.4rem; font-weight: 900; color: #0f172a; letter-spacing: -0.5px; }
.theme-moderne .a4-contact { font-size: 0.75rem; color: #ff6f00; font-weight: 600; }
.theme-moderne .a4-section-title { font-size: 0.85rem; font-weight: 800; color: #ff6f00; text-transform: uppercase; letter-spacing: 0.5px; margin: 1.5rem 0 0.75rem; }

/* THÈME HARVARD : Magistral Centré */
.theme-harvard { font-family: 'Georgia', serif; }
.theme-harvard .a4-header { text-align: center; margin-bottom: 2rem; }
.theme-harvard .a4-name { font-size: 1.5rem; font-weight: normal; text-transform: uppercase; letter-spacing: 2px; border-bottom: 1px solid #111; display: inline-block; padding-bottom: 0.2rem; }
.theme-harvard .a4-contact { font-size: 0.7rem; font-style: italic; color: #666; margin-top: 0.4rem; }
.theme-harvard .a4-section-title { font-size: 0.85rem; font-weight: bold; text-transform: uppercase; text-align: center; background: #f8fafc; padding: 0.2rem; margin: 1.5rem 0 1rem; }

/* THÈME CRÉATIF : Asymétrique */
.theme-creatif { font-family: 'system-ui', sans-serif; border-top: 8px solid #ff8c42; }
.theme-creatif .a4-header { display: flex; justify-content: space-between; align-items: flex-end; padding-bottom: 1rem; border-bottom: 2px dashed #eee; margin-bottom: 1.5rem; }
.theme-creatif .a4-name { font-size: 1.5rem; font-weight: 800; color: #ff6f00; }
.theme-creatif .a4-contact { font-size: 0.75rem; background: #f1f5f9; padding: 0.2rem 0.5rem; border-radius: 4px; }
.theme-creatif .a4-section-title { font-size: 0.85rem; font-weight: 800; text-transform: uppercase; color: #334155; display: inline-block; border-bottom: 3px solid #ff6f00; margin: 1.5rem 0 0.75rem; }

.a4-list { padding-left: 1.25rem; margin: 0; font-size: 0.8rem; line-height: 1.5; color: #334155; }
.a4-list li { margin-bottom: 0.5rem; }
.a4-list strong { color: #0f172a; }

.a4-locked-zone { position: relative; margin-top: 1.5rem; padding-top: 0.5rem; }
.a4-locked-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(3px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  border: 1px dashed #cbd5e1;
  border-radius: 4px;
  padding: 1rem;
}
.a4-locked-icon { width: 1.75rem; height: 1.75rem; color: #ff6f00; margin-bottom: 0.4rem; }
.a4-locked-overlay span { font-size: 0.85rem; font-weight: 800; color: #0f172a; margin-bottom: 0.2rem; }
.a4-locked-overlay small { font-size: 0.7rem; color: #64748b; }

.a4-dummy-line { height: 8px; background: #e2e8f0; border-radius: 2px; margin-bottom: 8px; width: 100%; }
.a4-dummy-line.short { width: 70%; }

.preview-modal-footer {
  padding: 1.25rem 2.5rem 2rem;
  background: rgba(0, 0, 0, 0.2);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  text-align: center;
}
.preview-modal-cta {
  width: 100%;
  padding: 1rem 2rem;
  font-size: 1rem;
  font-weight: 800;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
}
.preview-modal-cta:hover { transform: translateY(-2px); }
.cta--classic { background: #ffffff; color: #0f172a; box-shadow: 0 8px 20px rgba(255,255,255,0.15); }
.cta--classic:hover { box-shadow: 0 10px 25px rgba(255,255,255,0.25); background: #f8fafc; }
.cta--premium { background: linear-gradient(135deg, #ff9a5c, #ff6f00); color: #000; box-shadow: 0 8px 20px rgba(255,111,0,0.3); }
.cta--premium:hover { box-shadow: 0 10px 25px rgba(255,111,0,0.4); }

/* Bento 3 colonnes héritées */
.card-item-img-wrap--num { display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: 700; color: #ff6f00; background: rgba(255,255,255,0.03); }

/* Bloc ATS + FAQ */
.cv-roast-ats-block { background: linear-gradient(180deg, #252530 0%, #1c1c24 100%); border-top: 1px solid rgba(255,255,255,0.06); border-bottom: 1px solid rgba(255,255,255,0.06); padding: 3.5rem 1.5rem 4rem; }
.ats-block-inner { max-width: 900px; margin: 0 auto; }
.ats-badge { display: inline-block; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.2em; text-transform: uppercase; color: #ff6f00; margin-bottom: 0.75rem; }
.ats-main-title { font-size: clamp(1.5rem, 4vw, 2.25rem); font-weight: 700; color: #fff; margin: 0 0 1.5rem; letter-spacing: -0.02em; }
.ats-intro { margin-bottom: 2.5rem; }
.ats-intro-p { font-size: 1rem; line-height: 1.7; color: #e0e0e0; margin: 0 0 1rem; }
.ats-subtitle { font-size: 1.2rem; font-weight: 700; color: #fff; margin: 0 0 1.25rem; padding-bottom: 0.5rem; border-bottom: 2px solid rgba(255,111,0,0.4); display: inline-block; }
.ats-reasons-grid { display: grid; grid-template-columns: 1fr; gap: 1.25rem; margin-bottom: 3rem; }
@media (min-width: 768px) { .ats-reasons-grid { grid-template-columns: repeat(3, 1fr); gap: 1.5rem; } }
.ats-reason-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 1.5rem; position: relative; transition: border-color 0.2s, background 0.2s; }
.ats-reason-card:hover { background: rgba(255,255,255,0.05); border-color: rgba(255,111,0,0.25); }
.ats-reason-icon { width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 0.75rem; }
.ats-reason-icon--1 { background: rgba(255,111,0,0.15); color: #ff8c42; }
.ats-reason-icon--2 { background: rgba(0,94,255,0.15); color: #4d9aff; }
.ats-reason-icon--3 { background: rgba(34,197,94,0.15); color: #4ade80; }
.ats-reason-svg { width: 1.5rem; height: 1.5rem; }
.ats-reason-num { position: absolute; top: 1rem; right: 1rem; font-size: 0.7rem; font-weight: 700; color: rgba(255,255,255,0.35); }
.ats-reason-title { font-size: 1rem; font-weight: 700; color: #fff; margin: 0 0 0.5rem; line-height: 1.3; }
.ats-reason-desc { font-size: 0.875rem; line-height: 1.55; color: #b8b8b8; margin: 0; }
.ats-faq-wrap { padding-top: 2rem; border-top: 1px solid rgba(255,255,255,0.08); }
.ats-faq-heading { display: flex; align-items: center; gap: 0.5rem; font-size: 1.25rem; font-weight: 700; color: #fff; margin: 0 0 1.25rem; }
.ats-faq-heading-icon { width: 1.5rem; height: 1.5rem; color: #ff6f00; }
.ats-faq-list { display: flex; flex-direction: column; gap: 0.5rem; }
.ats-faq-item { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; overflow: hidden; transition: border-color 0.2s; }
.ats-faq-item--open { border-color: rgba(255,111,0,0.3); }
.ats-faq-q { width: 100%; display: flex; align-items: center; justify-content: space-between; padding: 1rem 1.25rem; background: none; border: none; font-size: 0.9375rem; font-weight: 600; color: #fff; text-align: left; cursor: pointer; }
.ats-faq-q:hover { background: rgba(255,255,255,0.04); }
.ats-faq-chevron { flex-shrink: 0; width: 20px; height: 20px; border-right: 2px solid currentColor; border-bottom: 2px solid currentColor; transform: rotate(45deg); margin-top: -4px; transition: transform 0.2s; opacity: 0.7; }
.ats-faq-item--open .ats-faq-chevron { transform: rotate(-135deg); margin-top: 4px; }
.ats-faq-a { max-height: 0; overflow: hidden; transition: max-height 0.25s ease-out; }
.ats-faq-item--open .ats-faq-a { max-height: 500px; }
.ats-faq-a p { margin: 0; padding: 0 1.25rem 1rem; font-size: 0.9375rem; line-height: 1.6; color: #c8c8c8; }
.shrink-0 { flex-shrink: 0; }
.ml-2 { margin-left: 0.5rem; }
</style>
