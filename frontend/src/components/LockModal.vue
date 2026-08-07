<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { lockState } from '@/store/lockState'
import { LockClosedIcon, BoltIcon, RocketLaunchIcon, XMarkIcon } from '@heroicons/vue/24/outline'

const { t } = useI18n()
const router = useRouter()

const isGold = computed(() => lockState.kind === 'gold')
const title = computed(() => isGold.value ? t('lock.gold_title') : t('lock.upgrade_title'))
const primaryLabel = computed(() => isGold.value ? t('lock.recharge') : t('lock.see_plans'))

function primaryAction() {
  const dest = isGold.value ? '/boutique' : '/tarifs'
  lockState.close()
  router.push(dest)
}
</script>

<template>
  <transition name="lock-fade">
    <div v-if="lockState.open" class="lock" @click.self="lockState.close()">
      <div class="lock__card">
        <button class="lock__close" @click="lockState.close()"><XMarkIcon class="w-5 h-5" /></button>

        <div :class="['lock__icon', isGold ? 'lock__icon--gold' : 'lock__icon--pro']">
          <BoltIcon v-if="isGold" class="w-8 h-8" />
          <RocketLaunchIcon v-else class="w-8 h-8" />
        </div>

        <h3 class="lock__title">{{ title }}</h3>
        <p class="lock__msg">{{ lockState.message || (isGold ? t('lock.gold_desc') : t('lock.upgrade_desc')) }}</p>

        <div class="lock__actions">
          <button class="lock__btn lock__btn--primary" @click="primaryAction">
            <BoltIcon v-if="isGold" class="w-4 h-4" />
            <RocketLaunchIcon v-else class="w-4 h-4" />
            {{ primaryLabel }}
          </button>
          <button class="lock__btn lock__btn--ghost" @click="lockState.close()">{{ t('lock.later') }}</button>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.lock { position: fixed; inset: 0; z-index: 200; display: flex; align-items: center; justify-content: center; padding: 1.5rem; background: rgba(15,23,42,0.55); backdrop-filter: blur(3px); }
.lock__card { position: relative; width: 100%; max-width: 400px; background: #fff; border-radius: 1.5rem; padding: 2rem 1.75rem 1.5rem; text-align: center; box-shadow: 0 30px 70px -20px rgba(15,23,42,0.5); }
.lock__close { position: absolute; top: 1rem; right: 1rem; background: #F1F5F9; border: none; border-radius: 0.6rem; padding: 0.35rem; color: #64748B; cursor: pointer; }
.lock__close:hover { background: #E2E8F0; }
.lock__icon { width: 4rem; height: 4rem; border-radius: 1.2rem; display: flex; align-items: center; justify-content: center; margin: 0 auto 1.1rem; color: #fff; }
.lock__icon--gold { background: linear-gradient(135deg, #FBBF24, #F59E0B); box-shadow: 0 14px 30px -12px rgba(245,158,11,0.7); }
.lock__icon--pro { background: linear-gradient(135deg, #6366F1, #4F46E5); box-shadow: 0 14px 30px -12px rgba(79,70,229,0.6); }
.lock__title { font-size: 1.25rem; font-weight: 800; color: #0F172A; margin: 0 0 0.5rem; }
.lock__msg { font-size: 0.9rem; color: #64748B; line-height: 1.5; margin: 0 0 1.5rem; }
.lock__actions { display: flex; flex-direction: column; gap: 0.6rem; }
.lock__btn { display: inline-flex; align-items: center; justify-content: center; gap: 0.45rem; padding: 0.85rem; border-radius: 0.9rem; font-weight: 700; font-size: 0.9rem; cursor: pointer; border: none; }
.lock__btn--primary { background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; box-shadow: 0 10px 22px -10px rgba(245,158,11,0.7); }
.lock__btn--ghost { background: #F1F5F9; color: #475569; }
.lock__btn--ghost:hover { background: #E2E8F0; }

.lock-fade-enter-active, .lock-fade-leave-active { transition: opacity 0.2s; }
.lock-fade-enter-active .lock__card, .lock-fade-leave-active .lock__card { transition: transform 0.2s; }
.lock-fade-enter-from, .lock-fade-leave-to { opacity: 0; }
.lock-fade-enter-from .lock__card, .lock-fade-leave-to .lock__card { transform: scale(0.94); }
</style>
