<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const isVisible = ref(false)

onMounted(() => {
  // Show after scrolling 30% of the page
  const handleScroll = () => {
    const scrollPercent = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100
    const alreadyShown = localStorage.getItem('auth-cta-shown')
    
    if (scrollPercent > 30 && !alreadyShown && !isVisible.value) {
      isVisible.value = true
      localStorage.setItem('auth-cta-shown', 'true')
    }
  }
  
  window.addEventListener('scroll', handleScroll)
})

const close = () => {
  isVisible.value = false
}
</script>

<template>
  <transition name="fade-scale">
    <div v-if="isVisible" class="modal-overlay" @click.self="close">
      <div class="modal-card">
        <div class="modal-decoration"></div>
        <div class="modal-content">
          <div class="icon-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
            </svg>
          </div>
          <h2 class="modal-title">{{ t('landing_popups.auth_cta.title') }}</h2>
          <p class="modal-subtitle">{{ t('landing_popups.auth_cta.subtitle') }}</p>
          
          <div class="actions">
            <router-link to="/register" class="btn-primary" @click="close">
              {{ t('landing_popups.auth_cta.btn') }}
            </router-link>
            <button @click="close" class="btn-link">{{ t('landing_popups.auth_cta.close') }}</button>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
  padding: 20px;
}

.modal-card {
  background: #0a0a0f;
  width: 100%;
  max-width: 480px;
  border-radius: 30px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.8);
}

.modal-decoration {
  position: absolute;
  top: -50px;
  right: -50px;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(255, 140, 66, 0.15) 0%, transparent 70%);
  pointer-events: none;
}

.modal-content {
  padding: 40px;
  text-align: center;
}

.icon-box {
  width: 80px;
  height: 80px;
  background: rgba(255, 140, 66, 0.1);
  color: #ff8c42;
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
}

.icon-box svg {
  width: 40px;
  height: 40px;
}

.modal-title {
  color: #fff;
  font-size: 26px;
  font-weight: 800;
  line-height: 1.2;
  margin-bottom: 12px;
}

.modal-subtitle {
  color: rgba(255, 255, 255, 0.6);
  font-size: 16px;
  line-height: 1.6;
  margin-bottom: 32px;
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.btn-primary {
  background: #ff8c42;
  color: #000;
  text-decoration: none;
  padding: 18px;
  border-radius: 16px;
  font-weight: 800;
  font-size: 16px;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: #ffa870;
  transform: translateY(-2px);
}

.btn-link {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.btn-link:hover {
  color: #fff;
}

.fade-scale-enter-active, .fade-scale-leave-active {
  transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

.fade-scale-enter-from {
  opacity: 0;
  transform: scale(0.9) translateY(20px);
}

.fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.9) translateY(20px);
}
</style>
