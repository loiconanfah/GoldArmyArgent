<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const isVisible = ref(false)

onMounted(() => {
  // Show on every refresh as requested by user
  setTimeout(() => {
    isVisible.value = true
  }, 1500)
})

const accept = () => {
  localStorage.setItem('cookie-consent', 'accepted')
  isVisible.value = false
}

const decline = () => {
  localStorage.setItem('cookie-consent', 'declined')
  isVisible.value = false
}
</script>

<template>
  <transition name="slide-up">
    <div v-if="isVisible" class="cookie-banner">
      <div class="cookie-content">
        <div class="cookie-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2a10 10 0 1 0 10 10 4 4 0 0 1-5-5 4 4 0 0 1-5-5" />
            <circle cx="12" cy="12" r="1" fill="currentColor" />
            <circle cx="15" cy="15" r="1" fill="currentColor" />
            <circle cx="9" cy="16" r="1" fill="currentColor" />
            <circle cx="8" cy="11" r="1" fill="currentColor" />
          </svg>
        </div>
        <p class="cookie-text">{{ t('landing_popups.cookies.text') }}</p>
        <div class="cookie-actions">
          <button @click="decline" class="btn-decline">{{ t('landing_popups.cookies.decline') }}</button>
          <button @click="accept" class="btn-accept">{{ t('landing_popups.cookies.accept') }}</button>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.cookie-banner {
  position: fixed;
  bottom: 24px;
  left: 24px;
  right: 24px;
  z-index: 1000;
  display: flex;
  justify-content: center;
}

@media (min-width: 768px) {
  .cookie-banner {
    left: auto;
    width: 450px;
  }
}

.cookie-content {
  background: rgba(15, 15, 20, 0.9);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 16px 20px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.cookie-icon {
  width: 32px;
  height: 32px;
  color: #ff8c42;
  flex-shrink: 0;
}

.cookie-text {
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
  line-height: 1.4;
  margin: 0;
}

.cookie-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

button {
  padding: 8px 14px;
  font-size: 12px;
  font-weight: 700;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-accept {
  background: #ff8c42;
  color: #000;
  border: none;
}

.btn-accept:hover {
  background: #ffa870;
  transform: translateY(-1px);
}

.btn-decline {
  background: transparent;
  color: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-decline:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.05);
}

.slide-up-enter-active, .slide-up-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.slide-up-enter-from, .slide-up-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>
