<script setup>
import { useI18n } from 'vue-i18n'
import LandingNav from '../components/LandingNav.vue'
import Footer from '../components/Footer.vue'
import CookieBanner from '../components/popups/CookieBanner.vue'

const { t } = useI18n()
</script>

<template>
  <div class="page-wrapper">
    <LandingNav />
    <main class="main bg-dark">
      <section class="section pt-32 pb-20">
        <div class="container mx-auto px-6 max-w-4xl">
          <h1 class="text-5xl font-bold text-white mb-12">{{ t('privacy_page.title') }}</h1>
          
          <div class="prose prose-invert max-w-none text-gray-400 space-y-8">
            <section>
              <h2 class="text-2xl font-semibold text-white mb-4">{{ t('privacy_page.intro_title') }}</h2>
              <p>{{ t('privacy_page.intro_text') }}</p>
            </section>

            <section>
              <h2 class="text-2xl font-semibold text-white mb-4">{{ t('privacy_page.data_title') }}</h2>
              <p>{{ t('privacy_page.data_text') }}</p>
              <ul class="list-disc pl-6 space-y-2">
                <li>{{ t('privacy_page.data_item1') }}</li>
                <li>{{ t('privacy_page.data_item2') }}</li>
                <li>{{ t('privacy_page.data_item3') }}</li>
              </ul>
            </section>

            <section>
              <h2 class="text-2xl font-semibold text-white mb-4">{{ t('privacy_page.ai_title') }}</h2>
              <p>{{ t('privacy_page.ai_text') }}</p>
            </section>

            <section>
              <h2 class="text-2xl font-semibold text-white mb-4">{{ t('privacy_page.security_title') }}</h2>
              <p>{{ t('privacy_page.security_text') }}</p>
            </section>

            <section>
              <h2 class="text-2xl font-semibold text-white mb-4">{{ t('privacy_page.rights_title') }}</h2>
              <p>{{ t('privacy_page.rights_text') }}</p>
            </section>

            <section>
              <div class="p-6 bg-dark-lighter rounded-xl border border-gray-800">
                <p class="text-sm">{{ t('privacy_page.last_update') }}</p>
                <p class="text-sm">{{ t('privacy_page.contact_info') }}</p>
              </div>
            </section>
          </div>
        </div>
      </section>
    </main>
    <Footer />
    <CookieBanner />
  </div>
</template>

<style scoped>
.bg-dark { background-color: #0A0A0F; }
.bg-dark-lighter { background-color: #111119; }
</style>
