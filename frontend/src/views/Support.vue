<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import LandingNav from '../components/LandingNav.vue'
import Footer from '../components/Footer.vue'

const { t } = useI18n()

const form = ref({
  name: '',
  email: '',
  subject: '',
  message: ''
})

const isSending = ref(false)
const showSuccess = ref(false)
const showError = ref(false)

const submitForm = async () => {
  isSending.value = true
  showSuccess.value = false
  showError.value = false

  try {
    const baseUrl = import.meta.env.VITE_API_URL || ''
    const response = await fetch(`${baseUrl}/api/support/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(form.value)
    })

    if (response.ok) {
      showSuccess.value = true
      form.value = { name: '', email: '', subject: '', message: '' }
    } else {
      showError.value = true
    }
  } catch (err) {
    console.error('Support form error:', err)
    showError.value = true
  } finally {
    isSending.value = false
  }
}
</script>

<template>
  <div class="page-wrapper">
    <LandingNav />
    <main class="main">
      <section class="section pt-32 pb-20 bg-dark">
        <div class="container mx-auto px-6 text-center">
          <h1 class="text-5xl font-bold text-white mb-6">{{ t('support_page.title') }}</h1>
          <p class="text-xl text-gray-400 mb-12 max-w-2xl mx-auto">
            {{ t('support_page.subtitle') }}
          </p>
        </div>
      </section>

      <section class="section py-20 bg-dark-lighter">
        <div class="container mx-auto px-6">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-16">
            <!-- Left Side: Boxes -->
            <div class="space-y-8">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <!-- Contact Unit -->
                <div class="p-8 rounded-2xl bg-dark border border-gray-800 hover:border-orange-500/50 transition-all">
                  <div class="w-12 h-12 bg-orange-500 rounded-lg flex items-center justify-center mb-6">
                    <svg class="w-6 h-6 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <h3 class="text-xl font-semibold text-white mb-4">{{ t('support_page.email_title') }}</h3>
                  <a href="mailto:support@goldarmyai.com" class="text-orange-500 font-bold hover:underline">support@goldarmyai.com</a>
                </div>

                <!-- FAQ Unit -->
                <div class="p-8 rounded-2xl bg-dark border border-gray-800 hover:border-orange-500/50 transition-all">
                  <div class="w-12 h-12 bg-orange-500 rounded-lg flex items-center justify-center mb-6">
                    <svg class="w-6 h-6 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <h3 class="text-xl font-semibold text-white mb-4">{{ t('support_page.faq_title') }}</h3>
                  <router-link to="/#faq" class="text-orange-500 font-bold hover:underline">{{ t('support_page.faq_cta') }}</router-link>
                </div>
              </div>

              <!-- Tech Status Box -->
              <div class="p-8 rounded-2xl bg-dark border border-gray-800 hover:border-orange-500/50 transition-all flex items-center justify-between">
                <div class="flex items-center gap-6">
                  <div class="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
                    <div class="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                  </div>
                  <div>
                    <h3 class="text-xl font-semibold text-white mb-1">{{ t('support_page.status_title') }}</h3>
                    <p class="text-gray-400 text-sm">{{ t('support_page.status_desc') }}</p>
                  </div>
                </div>
                <span class="text-green-500 font-black text-sm uppercase tracking-widest">{{ t('support_page.status_ok') }}</span>
              </div>
            </div>

            <!-- Right Side: Contact Form -->
            <div class="bg-dark p-10 rounded-3xl border border-gray-800 shadow-2xl relative overflow-hidden group">
              <div class="absolute top-0 right-0 w-32 h-32 bg-orange-500/5 rounded-bl-full blur-2xl"></div>
              
              <h2 class="text-3xl font-bold text-white mb-8">{{ t('support_form.title') }}</h2>

              <form @submit.prevent="submitForm" class="space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label class="block text-sm font-bold text-gray-400 mb-2">{{ t('support_form.name_label') }}</label>
                    <input 
                      v-model="form.name" 
                      type="text" 
                      required
                      class="w-full bg-dark-lighter border border-gray-800 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-orange-500 transition-all"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-bold text-gray-400 mb-2">{{ t('support_form.email_label') }}</label>
                    <input 
                      v-model="form.email" 
                      type="email" 
                      required
                      class="w-full bg-dark-lighter border border-gray-800 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-orange-500 transition-all"
                    />
                  </div>
                </div>

                <div>
                  <label class="block text-sm font-bold text-gray-400 mb-2">{{ t('support_form.subject_label') }}</label>
                  <input 
                    v-model="form.subject" 
                    type="text" 
                    required
                    class="w-full bg-dark-lighter border border-gray-800 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-orange-500 transition-all"
                  />
                </div>

                <div>
                  <label class="block text-sm font-bold text-gray-400 mb-2">{{ t('support_form.message_label') }}</label>
                  <textarea 
                    v-model="form.message" 
                    rows="5" 
                    required
                    class="w-full bg-dark-lighter border border-gray-800 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-orange-500 transition-all resize-none"
                  ></textarea>
                </div>

                <button 
                  type="submit" 
                  :disabled="isSending"
                  class="w-full bg-orange-500 hover:bg-orange-400 disabled:bg-gray-700 text-black font-black py-4 rounded-xl transition-all shadow-lg hover:shadow-orange-500/20 active:scale-95 flex items-center justify-center gap-3"
                >
                  <span v-if="isSending">{{ t('support_form.sending') }}</span>
                  <span v-else>{{ t('support_form.submit_btn') }}</span>
                </button>

                <!-- Success/Error Feedback -->
                <transition name="fade">
                  <div v-if="showSuccess" class="p-4 bg-green-500/10 border border-green-500/30 rounded-xl text-green-400 text-sm font-bold text-center">
                    {{ t('support_form.success_msg') }}
                  </div>
                  <div v-else-if="showError" class="p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm font-bold text-center">
                    {{ t('support_form.error_msg') }}
                  </div>
                </transition>
              </form>
            </div>
          </div>
        </div>
      </section>
    </main>
    <Footer />
  </div>
</template>

<style scoped>
.page-wrapper {
  background-color: #0A0A0F;
  min-height: 100vh;
}
.bg-dark { background-color: #0A0A0F; }
.bg-dark-lighter { background-color: #111119; }

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
