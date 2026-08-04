<script setup>
import { ref, watch, onMounted } from 'vue'
import { authFetch } from '../utils/auth'
import { toastState } from '../store/toastState'
import {
  XMarkIcon, ClipboardDocumentIcon, CheckIcon, SparklesIcon,
  UserPlusIcon, GiftIcon, TrophyIcon, ArrowPathIcon, ShareIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  show: { type: Boolean, default: false }
})

const emit = defineEmits(['close'])

const isLoading = ref(true)
const stats = ref(null)
const copied = ref(false)

const fetchReferralStats = async () => {
  isLoading.value = true
  try {
    const res = await authFetch('/api/referral/stats')
    const json = await res.json()
    if (res.ok && json.status === 'success') {
      stats.value = json.data
    } else {
      toastState.addToast('Impossible de charger les statistiques de parrainage', 'error')
    }
  } catch (e) {
    console.error('Failed to load referral stats', e)
  } finally {
    isLoading.value = false
  }
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    fetchReferralStats()
  }
})

const copyShareUrl = async () => {
  if (!stats.value?.share_url) return
  try {
    await navigator.clipboard.writeText(stats.value.share_url)
    copied.value = true
    toastState.addToast('Lien de parrainage copié dans le presse-papier !', 'success')
    trackShare('copy_link')
    setTimeout(() => copied.value = false, 3000)
  } catch (e) {
    toastState.addToast('Erreur lors de la copie du lien', 'error')
  }
}

const trackShare = async (platform) => {
  try {
    await authFetch('/api/referral/share', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ platform })
    })
  } catch (e) {}
}

const shareLinkedIn = () => {
  if (!stats.value?.share_url) return
  const text = encodeURIComponent("J'utilise GoldArmy pour booster ma recherche d'emploi. Rejoins-moi avec mon lien pour recevoir 10 crédits offerts :")
  const url = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(stats.value.share_url)}`
  window.open(url, '_blank')
  trackShare('linkedin')
}

const shareWhatsApp = () => {
  if (!stats.value?.share_url) return
  const text = encodeURIComponent(`Salut ! Découvre GoldArmy pour ta recherche d'emploi. Inscris-toi via mon lien pour recevoir 10 crédits offerts : ${stats.value.share_url}`)
  window.open(`https://api.whatsapp.com/send?text=${text}`, '_blank')
  trackShare('whatsapp')
}

const shareEmail = () => {
  if (!stats.value?.share_url) return
  const subject = encodeURIComponent("Invitation GoldArmy - 10 crédits offerts")
  const body = encodeURIComponent(`Hello,\n\nJe voulais te recommander GoldArmy pour t'aider à postuler et contacter les décideurs sur LinkedIn.\n\nInscris-toi avec mon lien d'invitation pour recevoir 10 crédits offerts :\n${stats.value.share_url}\n\nÀ très vite !`)
  window.open(`mailto:?subject=${subject}&body=${body}`)
  trackShare('email')
}

const close = () => {
  emit('close')
}
</script>

<template>
  <Transition name="modal-fade">
    <div v-if="show" class="fixed inset-0 z-[250] flex items-center justify-center p-4">
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-slate-900/30 backdrop-blur-sm" @click="close"></div>

      <!-- Modal Container (Clean Light Theme) -->
      <div class="relative z-10 bg-white border border-slate-200 rounded-3xl shadow-2xl w-full max-w-xl overflow-hidden animate-pop-in">
        
        <!-- Header Banner (Light Gold/Amber Theme) -->
        <div class="px-6 pt-6 pb-5 bg-amber-50/80 border-b border-amber-200/80">
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-3">
              <div class="w-11 h-11 rounded-2xl bg-amber-500 text-white flex items-center justify-center shadow-md shadow-amber-500/20 shrink-0">
                <GiftIcon class="w-6 h-6" />
              </div>
              <div>
                <span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-amber-100 border border-amber-300 text-amber-800 text-[10px] font-black uppercase tracking-wider">
                  <SparklesIcon class="w-3 h-3 text-amber-600" /> Programme Parrainage
                </span>
                <h3 class="text-xl font-display font-black tracking-tight text-slate-900 mt-0.5">Invitez des amis & Gagnez</h3>
              </div>
            </div>
            <button @click="close" class="p-1.5 text-slate-400 hover:text-slate-700 rounded-xl hover:bg-slate-100 transition-colors shrink-0">
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>

          <p class="text-xs text-slate-600 font-semibold mt-3 leading-relaxed">
            Offrez <span class="font-black text-slate-900">10 crédits bonus</span> à vos proches et recevez <span class="font-black text-amber-700">15 crédits</span> pour chaque inscription.
          </p>
        </div>

        <!-- Body Content -->
        <div class="p-6 space-y-5 max-h-[75vh] overflow-y-auto custom-scrollbar">
          
          <div v-if="isLoading" class="flex flex-col items-center justify-center py-10 gap-3">
            <ArrowPathIcon class="w-8 h-8 text-amber-500 animate-spin" />
            <p class="text-xs text-slate-500 font-semibold">Chargement de votre statut de parrainage…</p>
          </div>

          <template v-else-if="stats">
            
            <!-- 1. Stats Counter Cards -->
            <div class="grid grid-cols-3 gap-3">
              <div class="bg-slate-50 border border-slate-200 rounded-2xl p-3.5 text-center">
                <p class="text-2xl font-black text-slate-900 leading-none">{{ stats.total_referrals }}</p>
                <p class="text-[10px] font-bold text-slate-500 uppercase tracking-wider mt-1">Filleuls</p>
              </div>

              <div class="bg-amber-50/80 border border-amber-200/80 rounded-2xl p-3.5 text-center">
                <p class="text-2xl font-black text-amber-600 leading-none">+{{ stats.credits_earned }}</p>
                <p class="text-[10px] font-bold text-amber-800 uppercase tracking-wider mt-1">Crédits gagnés</p>
              </div>

              <div class="bg-slate-50 border border-slate-200 rounded-2xl p-3.5 text-center">
                <p class="text-2xl font-black text-slate-900 leading-none">{{ stats.bonus_credits_balance }}</p>
                <p class="text-[10px] font-bold text-slate-500 uppercase tracking-wider mt-1">Solde Actif</p>
              </div>
            </div>

            <!-- 2. Tier Progress & Level -->
            <div class="bg-slate-50 border border-slate-200 rounded-2xl p-4">
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2">
                  <TrophyIcon class="w-4 h-4 text-amber-600" />
                  <span class="text-xs font-bold text-slate-800">Statut : <span class="text-amber-700">{{ stats.tier_label }}</span></span>
                </div>
                <span class="text-[11px] font-bold text-slate-500">{{ stats.total_referrals }} / {{ stats.next_tier_target }} filleuls</span>
              </div>
              
              <!-- Progress Bar -->
              <div class="w-full h-2 rounded-full bg-slate-200 overflow-hidden">
                <div 
                  class="h-full bg-amber-500 rounded-full transition-all duration-700"
                  :style="`width: ${Math.min(100, Math.round((stats.total_referrals / stats.next_tier_target) * 100))}%`"
                ></div>
              </div>
            </div>

            <!-- 3. Unique Share Link -->
            <div>
              <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">Votre lien de parrainage unique</label>
              <div class="relative flex items-center">
                <input
                  type="text"
                  readonly
                  :value="stats.share_url"
                  class="w-full bg-slate-50 border border-slate-200 text-slate-900 font-mono text-xs rounded-xl pl-3.5 pr-28 py-3 focus:outline-none select-all font-semibold"
                />
                <button
                  @click="copyShareUrl"
                  class="absolute right-1.5 top-1.5 bottom-1.5 px-3.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5"
                  :class="copied ? 'bg-emerald-600 text-white' : 'bg-amber-500 hover:bg-amber-600 text-white shadow-sm'"
                >
                  <CheckIcon v-if="copied" class="w-3.5 h-3.5" />
                  <ClipboardDocumentIcon v-else class="w-3.5 h-3.5" />
                  {{ copied ? 'Copié !' : 'Copier' }}
                </button>
              </div>
            </div>

            <!-- 4. Quick Social Share Buttons -->
            <div>
              <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">Partager directement sur</label>
              <div class="grid grid-cols-3 gap-2.5">
                <button
                  @click="shareLinkedIn"
                  class="flex items-center justify-center gap-2 py-2.5 px-3 rounded-xl bg-slate-100 hover:bg-slate-200 border border-slate-200 text-slate-800 font-bold text-xs transition-all"
                >
                  <ShareIcon class="w-3.5 h-3.5 text-slate-700" /> LinkedIn
                </button>

                <button
                  @click="shareWhatsApp"
                  class="flex items-center justify-center gap-2 py-2.5 px-3 rounded-xl bg-slate-100 hover:bg-slate-200 border border-slate-200 text-slate-800 font-bold text-xs transition-all"
                >
                  <ShareIcon class="w-3.5 h-3.5 text-emerald-600" /> WhatsApp
                </button>

                <button
                  @click="shareEmail"
                  class="flex items-center justify-center gap-2 py-2.5 px-3 rounded-xl bg-slate-100 hover:bg-slate-200 border border-slate-200 text-slate-800 font-bold text-xs transition-all"
                >
                  <ShareIcon class="w-3.5 h-3.5 text-slate-700" /> Email
                </button>
              </div>
            </div>

            <!-- 5. Referred Friends History -->
            <div v-if="stats.referred_friends && stats.referred_friends.length > 0">
              <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">Vos filleuls inscrits</label>
              <div class="space-y-2 max-h-40 overflow-y-auto custom-scrollbar border border-slate-200 rounded-2xl p-2 bg-slate-50/50">
                <div 
                  v-for="friend in stats.referred_friends" 
                  :key="friend.id"
                  class="flex items-center justify-between p-2.5 bg-white rounded-xl border border-slate-200 shadow-sm"
                >
                  <div class="flex items-center gap-2.5">
                    <div class="w-7 h-7 rounded-lg bg-amber-50 text-amber-600 font-bold text-xs flex items-center justify-center border border-amber-200">
                      <UserPlusIcon class="w-4 h-4" />
                    </div>
                    <span class="text-xs font-bold text-slate-800">{{ friend.masked_email }}</span>
                  </div>
                  <span class="text-[11px] font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">
                    +{{ friend.credits_earned }} cr.
                  </span>
                </div>
              </div>
            </div>

          </template>
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 border-t border-slate-200 bg-slate-50 flex items-center justify-between">
          <span class="text-[11px] text-slate-500 font-medium">Les crédits sont attribués instantanément.</span>
          <button
            @click="close"
            class="px-4 py-2 rounded-xl text-xs font-bold bg-white hover:bg-slate-100 border border-slate-200 text-slate-700 transition-colors"
          >
            Fermer
          </button>
        </div>

      </div>
    </div>
  </Transition>
</template>

<style scoped>
@keyframes pop-in {
  from { transform: scale(0.95) translateY(8px); opacity: 0; }
  to   { transform: scale(1) translateY(0); opacity: 1; }
}
.animate-pop-in { animation: pop-in 0.2s ease-out forwards; }

.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.2s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }

.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
</style>
