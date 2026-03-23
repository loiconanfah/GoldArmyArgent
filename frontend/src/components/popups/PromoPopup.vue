<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const isVisible = ref(false)

onMounted(() => {
  // Show on every refresh as requested by user
  setTimeout(() => {
    isVisible.value = true
  }, 5000) // Show after 5 seconds
})

const close = () => {
  sessionStorage.setItem('promo-dismissed', 'true')
  isVisible.value = false
}
</script>

<template>
  <transition name="pop">
    <div v-if="isVisible" class="promo-popup">
      <div class="promo-card">
        <button @click="close" class="close-btn">&times;</button>
        <div class="promo-badge">HOT</div>
        <div class="promo-image">
          <div class="glow"></div>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607zM10.5 7.5v6m3-3h-6" />
          </svg>
        </div>
        <h3 class="promo-title">{{ t('landing_popups.promo.title') }}</h3>
        <p class="promo-text">{{ t('landing_popups.promo.text') }}</p>
        <router-link to="/register" class="promo-cta" @click="close">
          {{ t('landing_popups.promo.cta') }}
        </router-link>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.promo-popup {
  position: fixed;
  top: 100px;
  right: 24px;
  z-index: 1001;
  width: 300px;
}

.promo-card {
  background: #111119;
  border: 1px solid rgba(255, 140, 66, 0.3);
  border-radius: 20px;
  padding: 24px;
  position: relative;
  text-align: center;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6), 0 0 20px rgba(255, 140, 66, 0.1);
  overflow: hidden;
}

.close-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  font-size: 20px;
  cursor: pointer;
  z-index: 10;
}

.promo-badge {
  position: absolute;
  top: 15px;
  left: -25px;
  background: #ff4d4d;
  color: white;
  font-size: 10px;
  font-weight: 900;
  padding: 4px 30px;
  transform: rotate(-45deg);
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.promo-image {
  width: 60px;
  height: 60px;
  margin: 0 auto 16px;
  background: rgba(255, 140, 66, 0.1);
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ff8c42;
  position: relative;
}

.glow {
  position: absolute;
  width: 100%;
  height: 100%;
  background: #ff8c42;
  filter: blur(20px);
  opacity: 0.2;
}

.promo-image svg {
  width: 32px;
  height: 32px;
  position: relative;
  z-index: 1;
}

.promo-title {
  color: #fff;
  font-size: 18px;
  font-weight: 800;
  margin-bottom: 8px;
}

.promo-text {
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
  line-height: 1.5;
  margin-bottom: 20px;
}

.promo-cta {
  display: block;
  background: linear-gradient(135deg, #ff9a5c 0%, #ff6f00 100%);
  color: #000;
  text-decoration: none;
  padding: 12px;
  border-radius: 12px;
  font-weight: 800;
  font-size: 13px;
  transition: all 0.3s;
}

.promo-cta:hover {
  transform: scale(1.05);
  box-shadow: 0 5px 15px rgba(255, 111, 0, 0.3);
}

.pop-enter-active {
  animation: pop-in 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.pop-leave-active {
  transition: all 0.3s ease-in;
}
.pop-leave-to {
  opacity: 0;
  transform: translateX(50px) scale(0.9);
}

@keyframes pop-in {
  0% { opacity: 0; transform: scale(0.5) translateY(50px); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}
</style>
