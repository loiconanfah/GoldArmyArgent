<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { authFetch } from '@/utils/auth'
import { PlusIcon, TrashIcon, EnvelopeIcon, BuildingOfficeIcon } from '@heroicons/vue/24/outline'

const { t } = useI18n()
const loading = ref(true)
const contacts = ref([])
const showForm = ref(false)
const saving = ref(false)
const form = ref({ name: '', company: '', role: '', email: '', linkedin: '', notes: '' })

async function load() {
  loading.value = true
  try {
    const res = await authFetch('/api/org/network')
    const json = await res.safeJson()
    if (json?.status === 'success') contacts.value = json.data
  } catch (e) {} finally { loading.value = false }
}

async function add() {
  if (!form.value.name.trim()) return
  saving.value = true
  try {
    const res = await authFetch('/api/org/network', { method: 'POST', body: JSON.stringify(form.value) })
    const json = await res.safeJson()
    if (json?.status === 'success') {
      contacts.value.unshift(json.data)
      form.value = { name: '', company: '', role: '', email: '', linkedin: '', notes: '' }
      showForm.value = false
    }
  } catch (e) {} finally { saving.value = false }
}

async function remove(c) {
  if (!confirm(t('org.network.remove_confirm', { name: c.name }))) return
  try {
    const res = await authFetch(`/api/org/network/${c.id}`, { method: 'DELETE' })
    if (res.ok) contacts.value = contacts.value.filter(x => x.id !== c.id)
  } catch (e) {}
}

onMounted(load)
</script>

<template>
  <div class="on">
    <header class="on__head">
      <div>
        <h1 class="on__title">{{ t('org.nav.network') }}</h1>
        <p class="on__sub">{{ t('org.network.sub') }}</p>
      </div>
      <button class="on__add" @click="showForm = !showForm"><PlusIcon class="w-4 h-4" /> {{ t('org.network.add') }}</button>
    </header>

    <transition name="on-form">
      <div v-if="showForm" class="on__card on__form">
        <div class="on__form-grid">
          <input v-model="form.name" :placeholder="t('org.network.name')" class="on__input" />
          <input v-model="form.company" :placeholder="t('org.network.company')" class="on__input" />
          <input v-model="form.role" :placeholder="t('org.network.role')" class="on__input" />
          <input v-model="form.email" type="email" :placeholder="t('org.network.email')" class="on__input" />
          <input v-model="form.linkedin" :placeholder="t('org.network.linkedin')" class="on__input" />
          <input v-model="form.notes" :placeholder="t('org.network.notes')" class="on__input" />
        </div>
        <button class="on__save" @click="add" :disabled="saving">{{ saving ? t('common.saving') : t('org.network.save') }}</button>
      </div>
    </transition>

    <div v-if="loading" class="on__loading">{{ t('common.loading') }}…</div>
    <div v-else-if="!contacts.length" class="on__empty">{{ t('org.network.empty') }}</div>

    <div v-else class="on__grid">
      <div v-for="c in contacts" :key="c.id" class="on__card on__contact">
        <button class="on__del" @click="remove(c)"><TrashIcon class="w-4 h-4" /></button>
        <div class="on__contact-name">{{ c.name }}</div>
        <div v-if="c.role || c.company" class="on__contact-role">
          {{ c.role }}<span v-if="c.role && c.company"> · </span>{{ c.company }}
        </div>
        <div v-if="c.email" class="on__contact-line"><EnvelopeIcon class="w-3.5 h-3.5" /> {{ c.email }}</div>
        <div v-if="c.linkedin" class="on__contact-line"><BuildingOfficeIcon class="w-3.5 h-3.5" /> {{ c.linkedin }}</div>
        <p v-if="c.notes" class="on__contact-notes">{{ c.notes }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.on { max-width: 1100px; margin: 0 auto; color: #1E293B; }
.on__head { display: flex; align-items: flex-end; justify-content: space-between; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.on__title { font-size: 1.7rem; font-weight: 800; margin: 0; letter-spacing: -0.02em; }
.on__sub { color: #64748B; font-size: 0.9rem; margin: 0.3rem 0 0; }
.on__add { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.65rem 1.1rem; border-radius: 0.7rem; background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; border: none; font-weight: 700; font-size: 0.82rem; cursor: pointer; box-shadow: 0 6px 16px -6px rgba(245,158,11,0.6); transition: transform 0.15s; }
.on__add:hover { transform: translateY(-2px); }
.on__loading, .on__empty { padding: 3rem; text-align: center; color: #94A3B8; }
.on__card { background: #fff; border: 1px solid #E2E8F0; border-radius: 1rem; padding: 1.2rem; box-shadow: 0 1px 2px rgba(15,23,42,0.04); }
.on__form { margin-bottom: 1.25rem; }
.on__form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem; margin-bottom: 0.8rem; }
.on__input { padding: 0.65rem 0.85rem; border-radius: 0.6rem; background: #F8FAFC; border: 1px solid #E2E8F0; color: #1E293B; font-size: 0.85rem; outline: none; }
.on__input:focus { border-color: #F59E0B; box-shadow: 0 0 0 3px rgba(245,158,11,0.12); background: #fff; }
.on__save { padding: 0.65rem 1.3rem; border-radius: 0.6rem; background: #F59E0B; color: #fff; border: none; font-weight: 700; font-size: 0.82rem; cursor: pointer; }
.on__grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 0.9rem; }
.on__contact { position: relative; transition: transform 0.15s, box-shadow 0.15s; }
.on__contact:hover { transform: translateY(-3px); box-shadow: 0 14px 30px -18px rgba(15,23,42,0.25); }
.on__del { position: absolute; top: 0.8rem; right: 0.8rem; background: none; border: none; color: #FCA5A5; cursor: pointer; }
.on__del:hover { color: #EF4444; }
.on__contact-name { font-weight: 800; font-size: 0.98rem; color: #0F172A; }
.on__contact-role { font-size: 0.78rem; color: #64748B; margin-top: 0.15rem; }
.on__contact-line { display: flex; align-items: center; gap: 0.35rem; font-size: 0.76rem; color: #475569; margin-top: 0.5rem; }
.on__contact-line svg { color: #94A3B8; }
.on__contact-notes { font-size: 0.75rem; color: #64748B; margin: 0.7rem 0 0; border-top: 1px solid #F1F5F9; padding-top: 0.6rem; }
.on-form-enter-active, .on-form-leave-active { transition: opacity 0.2s; }
.on-form-enter-from, .on-form-leave-to { opacity: 0; }
@media (max-width: 600px) { .on__form-grid { grid-template-columns: 1fr; } }
</style>
