<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useHead } from '@unhead/vue'
import { ArrowLeftIcon, EnvelopeIcon, LockClosedIcon, UserIcon } from '@heroicons/vue/24/outline'
import { useGoogleAuth } from '@/composables/useGoogleAuth'
import { safeJson } from '@/utils/auth'
import { getApiUrl } from '@/config'

const { t } = useI18n()
const router = useRouter()
const email = ref('')
const password = ref('')
const firstName = ref('')
const lastName = ref('')
const errorMsg = ref('')
const isLoading = ref(false)
const showPassword = ref(false)

useHead({
  title: computed(() => t('register.title') + ' | GoldArmy'),
  meta: [
    { name: 'description', content: computed(() => t('register.subtitle') || t('register.title')) }
  ]
})

const { googleLoading, googleError, initGoogle } = useGoogleAuth()
onMounted(() => initGoogle('google-btn-register'))

const handleRegister = async () => {
  errorMsg.value = ''
  isLoading.value = true
  try {
    const res = await fetch(getApiUrl('/api/auth/register'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: email.value,
        password: password.value,
        first_name: firstName.value,
        last_name: lastName.value
      })
    })

    const data = await safeJson(res)
    if (!res.ok) {
      errorMsg.value = data?.detail || t('register.error_generic')
    } else if (!data) {
      errorMsg.value = t('register.error_invalid_response')
    } else {
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      router.push('/home')
    }
  } catch (err) {
    errorMsg.value = t('common.error') + ': ' + t('common.server_error')
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-page__bg">
      <div class="auth-page__gradient auth-page__gradient--1"></div>
      <div class="auth-page__gradient auth-page__gradient--2"></div>
      <div class="auth-page__grid"></div>
    </div>

    <div class="auth-card auth-card--register">
      <!-- Form panel (left on desktop) -->
      <div class="auth-card__form-wrap">
        <div class="auth-card__form">
          <header class="auth-form__header">
            <h1 class="auth-form__title">{{ t('register.title') }}</h1>
            <p class="auth-form__subtitle">
              {{ t('register.subtitle') }}
              <router-link to="/login" class="auth-form__link">{{ t('register.login_link') }}</router-link>
            </p>
          </header>

          <Transition name="auth-shake">
            <div v-if="errorMsg" class="auth-form__error" role="alert">
              {{ errorMsg }}
            </div>
          </Transition>

          <form @submit.prevent="handleRegister" class="auth-form">
            <div class="auth-form__row-2">
              <div class="auth-form__field">
                <label class="auth-form__label">{{ t('register.first_name') }}</label>
                <div class="auth-form__input-wrap">
                  <UserIcon class="auth-form__input-icon" />
                  <input
                    v-model="firstName"
                    type="text"
                    :placeholder="t('register.first_name')"
                    class="auth-form__input"
                    autocomplete="given-name"
                  />
                </div>
              </div>
              <div class="auth-form__field">
                <label class="auth-form__label">{{ t('register.last_name') }}</label>
                <div class="auth-form__input-wrap">
                  <UserIcon class="auth-form__input-icon" />
                  <input
                    v-model="lastName"
                    type="text"
                    :placeholder="t('register.last_name')"
                    class="auth-form__input"
                    autocomplete="family-name"
                  />
                </div>
              </div>
            </div>

            <div class="auth-form__field">
              <label class="auth-form__label">{{ t('register.email') }}</label>
              <div class="auth-form__input-wrap">
                <EnvelopeIcon class="auth-form__input-icon" />
                <input
                  v-model="email"
                  type="email"
                  required
                  :placeholder="t('register.email')"
                  class="auth-form__input"
                  autocomplete="email"
                />
              </div>
            </div>

            <div class="auth-form__field">
              <label class="auth-form__label">{{ t('register.password') }}</label>
              <div class="auth-form__input-wrap">
                <LockClosedIcon class="auth-form__input-icon" />
                <input
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  required
                  :placeholder="t('register.password')"
                  class="auth-form__input auth-form__input--with-toggle"
                  autocomplete="new-password"
                />
                <button
                  type="button"
                  class="auth-form__toggle-pwd"
                  :aria-label="showPassword ? 'Masquer' : 'Afficher'"
                  @click="showPassword = !showPassword"
                >
                  <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="auth-form__toggle-icon">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.644m17.928.644a1.012 1.012 0 010-.644M12 3c2.755 0 5.455.232 8.083.678a1.012 1.012 0 01.682.988 11 11 0 01-1.017 4.898 1.012 1.012 0 01-.658.658 11 11 0 01-4.898 1.017 1.012 1.012 0 01-.988-.682A48.936 48.936 0 0012 3z" />
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="auth-form__toggle-icon">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
                  </svg>
                </button>
              </div>
            </div>

            <label class="auth-form__terms">
              <input type="checkbox" required class="auth-form__checkbox" />
              <span class="auth-form__terms-text">
                {{ t('register.agree_terms') }}
                <a href="#" class="auth-form__link">{{ t('register.terms') }}</a>
                {{ t('register.and') }}
                <a href="#" class="auth-form__link">{{ t('register.privacy') }}</a>
              </span>
            </label>

            <button
              type="submit"
              :disabled="isLoading"
              class="auth-form__submit"
            >
              <span v-if="isLoading" class="auth-form__spinner"></span>
              <span class="auth-form__submit-text">
                {{ isLoading ? t('register.submitting') : t('register.submit') }}
              </span>
            </button>

            <div class="auth-form__divider">
              <span class="auth-form__divider-text">{{ t('register.or_register_with') }}</span>
            </div>

            <div class="auth-form__social">
              <div id="google-btn-register" class="auth-form__google"></div>
              <div class="auth-form__social-btns">
                <button type="button" class="auth-form__social-btn" disabled title="Bientôt">
                  <svg class="auth-form__social-icon" viewBox="0 0 814 1000" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="M788.1 340.9c-5.8 4.5-108.2 62.2-108.2 190.5 0 148.4 130.3 200.9 134.2 202.2-.6 3.2-20.7 71.9-68.7 141.9-42.8 61.6-87.5 123.1-155.5 123.1s-85.5-39.5-164-39.5c-76 0-103.7 40.8-165.9 40.8s-105-57.8-155.5-127.4C46 376.2 0 293.8 0 213.5c0-84.1 53.4-128.5 106.1-128.5 77.5 0 98.1 49.7 167.5 49.7 67.9 0 103.2-50 167.5-50 59.7 0 121.4 37.8 160.6 109.8zM642 94.1c0 44.7-16.2 89.5-47.7 123.5-32.2 35.3-76.5 58.2-119.7 58.2-1.4 0-2.8 0-4.1-.1 1.2-43.8 19.1-86.2 48.9-118.7 31-33.1 77.3-55.7 119.8-56.9 1.5-.1 2.8-.1 2.8-.1z"/></svg>
                  Apple
                </button>
                <button type="button" class="auth-form__social-btn" disabled title="Bientôt">
                  <svg class="auth-form__social-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" fill="currentColor"/></svg>
                  Meta
                </button>
              </div>
            </div>
            <p v-if="googleError" class="auth-form__google-error">{{ googleError }}</p>
          </form>
        </div>
      </div>

      <!-- Visual panel (right on desktop) -->
      <div class="auth-card__visual">
        <div class="auth-card__visual-img-wrap">
          <img src="/og-banner.png" alt="GoldArmy" class="auth-card__visual-img" />
          <div class="auth-card__visual-overlay"></div>
        </div>
        <div class="auth-card__visual-header">
          <div class="auth-card__brand">
            <div class="auth-card__logo">
              <img src="/logo.png" alt="Logo" />
            </div>
            <span class="auth-card__name">GoldArmy</span>
          </div>
          <router-link to="/" class="auth-card__back">
            {{ t('register.back_to_website') }}
            <ArrowLeftIcon class="auth-card__back-icon" />
          </router-link>
        </div>
        <div class="auth-card__visual-footer">
          <h2 class="auth-card__slogan" v-html="t('register.join_elite')"></h2>
          <div class="auth-card__bars">
            <span class="auth-card__bar"></span>
            <span class="auth-card__bar auth-card__bar--active"></span>
            <span class="auth-card__bar"></span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Shared auth styles - same as Login (duplicated so Register is self-contained) */
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  position: relative;
  overflow: hidden;
}

.auth-page__bg {
  position: fixed;
  inset: 0;
  background: #1a1a22;
  z-index: 0;
}
.auth-page__gradient {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.4;
  animation: auth-glow 12s ease-in-out infinite alternate;
}
.auth-page__gradient--1 {
  width: 60vw;
  height: 60vw;
  max-width: 800px;
  max-height: 800px;
  background: #ff6f00;
  top: -20%;
  right: -10%;
}
.auth-page__gradient--2 {
  width: 40vw;
  height: 40vw;
  max-width: 500px;
  max-height: 500px;
  background: #005eff;
  bottom: -10%;
  left: -5%;
  animation-delay: -4s;
}
@keyframes auth-glow {
  0% { transform: scale(1) translate(0, 0); opacity: 0.3; }
  100% { transform: scale(1.1) translate(2%, 2%); opacity: 0.5; }
}

.auth-page__grid {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
  background-size: 60px 60px;
  mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, black 20%, transparent 70%);
}

.auth-card {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 1000px;
  min-height: 620px;
  max-height: min(90vh, 700px);
  background: rgba(37, 37, 47, 0.85);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 1.75rem;
  box-shadow: 0 25px 80px -20px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.03);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: auth-card-in 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes auth-card-in {
  from {
    opacity: 0;
    transform: translateY(24px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@media (min-width: 900px) {
  .auth-card {
    flex-direction: row;
    min-height: 580px;
  }
}

.auth-card__visual {
  display: none;
  position: relative;
  width: 48%;
  min-height: 320px;
  overflow: hidden;
}
@media (min-width: 900px) {
  .auth-card__visual {
    display: block;
  }
}

.auth-card__visual-img-wrap {
  position: absolute;
  inset: 0;
}
.auth-card__visual-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  animation: auth-img-zoom 20s ease-out forwards;
}
@keyframes auth-img-zoom {
  from { transform: scale(1.08); }
  to { transform: scale(1.12); }
}
.auth-card__visual-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(26, 26, 34, 0.95) 0%, transparent 50%, rgba(0,0,0,0.2) 100%);
}

.auth-card__visual-header {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  padding: 1.5rem 1.5rem 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  animation: auth-fade-in 0.8s 0.2s ease-out both;
}
@keyframes auth-fade-in {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}

.auth-card__brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.auth-card__logo {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.75rem;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: #25252f;
}
.auth-card__logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.auth-card__name {
  font-size: 1.25rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.02em;
}

.auth-card__back {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 999px;
  text-decoration: none;
  transition: background 0.2s, color 0.2s, transform 0.2s;
}
.auth-card__back:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
  transform: translateX(-2px);
}
.auth-card__back-icon {
  width: 0.875rem;
  height: 0.875rem;
}

.auth-card__visual-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 0 1.5rem 2rem;
  animation: auth-fade-in 0.8s 0.4s ease-out both;
}
.auth-card__slogan {
  font-size: clamp(1.25rem, 2.5vw, 1.75rem);
  font-weight: 700;
  color: #fff;
  line-height: 1.2;
  margin: 0 0 1rem;
}
.auth-card__bars {
  display: flex;
  gap: 0.5rem;
}
.auth-card__bar {
  width: 2.5rem;
  height: 0.25rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.2);
  transition: background 0.3s;
}
.auth-card__bar--active {
  background: #ff6f00;
}

.auth-card__form-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 2rem 1.5rem;
}
@media (min-width: 900px) {
  .auth-card__form-wrap {
    padding: 2.5rem 2.5rem 2.5rem 2rem;
  }
}

.auth-card__form {
  max-width: 400px;
  margin: 0 auto;
  width: 100%;
}

.auth-form__header {
  margin-bottom: 1.75rem;
  animation: auth-fade-in 0.6s 0.15s ease-out both;
}
.auth-form__title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #fff;
  letter-spacing: -0.03em;
  margin: 0 0 0.5rem;
}
.auth-form__subtitle {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.55);
  margin: 0;
}
.auth-form__link {
  color: #ff6f00;
  font-weight: 600;
  text-decoration: none;
  transition: color 0.2s, text-decoration 0.2s;
}
.auth-form__link:hover {
  color: #ff8c42;
  text-decoration: underline;
}

.auth-form__error {
  padding: 0.875rem 1rem;
  margin-bottom: 1.25rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.25);
  border-radius: 0.75rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #fca5a5;
  animation: auth-fade-in 0.3s ease-out;
}
.auth-shake-enter-active {
  animation: auth-shake 0.5s ease-out;
}
@keyframes auth-shake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-6px); }
  40% { transform: translateX(6px); }
  60% { transform: translateX(-4px); }
  80% { transform: translateX(4px); }
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.auth-form__field {
  animation: auth-fade-in 0.5s 0.25s ease-out both;
}
.auth-form__label {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 0.35rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.auth-form__input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}
.auth-form__input-icon {
  position: absolute;
  left: 1rem;
  width: 1.125rem;
  height: 1.125rem;
  color: rgba(255, 255, 255, 0.35);
  pointer-events: none;
  transition: color 0.2s;
}
.auth-form__input {
  width: 100%;
  padding: 0.875rem 1rem 0.875rem 2.75rem;
  font-size: 0.9375rem;
  color: #fff;
  background: rgba(28, 28, 36, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.75rem;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
}
.auth-form__input::placeholder {
  color: rgba(255, 255, 255, 0.35);
}
.auth-form__input:focus {
  border-color: rgba(255, 111, 0, 0.5);
  box-shadow: 0 0 0 3px rgba(255, 111, 0, 0.15);
}
.auth-form__input--with-toggle {
  padding-right: 3rem;
}
.auth-form__toggle-pwd {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  padding: 0.5rem;
  color: rgba(255, 255, 255, 0.4);
  background: none;
  border: none;
  cursor: pointer;
  border-radius: 0.5rem;
  transition: color 0.2s, background 0.2s;
}
.auth-form__toggle-pwd:hover {
  color: rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.05);
}
.auth-form__toggle-icon {
  width: 1.125rem;
  height: 1.125rem;
}

.auth-form__submit {
  position: relative;
  width: 100%;
  padding: 1rem 1.5rem;
  font-size: 0.9375rem;
  font-weight: 700;
  color: #1a1a22;
  background: linear-gradient(135deg, #ff9a5c 0%, #ff6f00 100%);
  border: none;
  border-radius: 0.75rem;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(255, 111, 0, 0.35);
  transition: transform 0.2s, box-shadow 0.2s, opacity 0.2s;
  animation: auth-fade-in 0.5s 0.45s ease-out both;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-height: 52px;
}
.auth-form__submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 28px rgba(255, 111, 0, 0.45);
}
.auth-form__submit:active:not(:disabled) {
  transform: translateY(0);
}
.auth-form__submit:disabled {
  opacity: 0.8;
  cursor: not-allowed;
}
.auth-form__spinner {
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid rgba(26, 26, 34, 0.3);
  border-top-color: #1a1a22;
  border-radius: 50%;
  animation: auth-spin 0.7s linear infinite;
}
@keyframes auth-spin {
  to { transform: rotate(360deg); }
}
.auth-form__submit-text {
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.auth-form__divider {
  position: relative;
  padding: 1.25rem 0;
  animation: auth-fade-in 0.5s 0.5s ease-out both;
}
.auth-form__divider::before {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  top: 50%;
  height: 1px;
  background: rgba(255, 255, 255, 0.06);
}
.auth-form__divider-text {
  position: relative;
  display: block;
  text-align: center;
  font-size: 0.6875rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.35);
  text-transform: uppercase;
  letter-spacing: 0.15em;
  background: rgba(37, 37, 47, 0.9);
  width: fit-content;
  margin: 0 auto;
  padding: 0 0.75rem;
}

.auth-form__social {
  animation: auth-fade-in 0.5s 0.55s ease-out both;
}
.auth-form__google {
  display: flex;
  justify-content: center;
  margin-bottom: 0.75rem;
}
.auth-form__social-btns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
.auth-form__social-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  font-size: 0.6875rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.6);
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.75rem;
  cursor: not-allowed;
  opacity: 0.7;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.auth-form__social-icon {
  width: 1rem;
  height: 1rem;
}
.auth-form__google-error {
  margin-top: 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #fca5a5;
  text-align: center;
}

/* Register-specific */
.auth-card--register {
  flex-direction: column;
}
@media (min-width: 900px) {
  .auth-card--register {
    flex-direction: row-reverse;
  }
}

.auth-card--register .auth-card__form-wrap {
  padding: 2rem 1.5rem;
}
@media (min-width: 900px) {
  .auth-card--register .auth-card__form-wrap {
    padding: 2.5rem 2rem 2.5rem 2.5rem;
  }
}

.auth-form__row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  animation: auth-fade-in 0.5s 0.2s ease-out both;
}

.auth-form__terms {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  cursor: pointer;
  animation: auth-fade-in 0.5s 0.38s ease-out both;
}
.auth-form__terms .auth-form__checkbox {
  margin-top: 0.25rem;
  width: 1rem;
  height: 1rem;
  accent-color: #ff6f00;
  cursor: pointer;
  flex-shrink: 0;
}
.auth-form__terms-text {
  font-size: 0.75rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.55);
  line-height: 1.5;
}
.auth-form__terms-text .auth-form__link {
  font-weight: 600;
}
</style>
