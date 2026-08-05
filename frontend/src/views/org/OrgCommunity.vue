<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { authFetch } from '@/utils/auth'
import { HeartIcon, TrashIcon, LinkIcon, PaperAirplaneIcon, ChatBubbleOvalLeftIcon } from '@heroicons/vue/24/outline'

const { t } = useI18n()
const loading = ref(true)
const posts = ref([])
const posting = ref(false)
const draft = ref({ type: 'message', title: '', content: '', link: '' })
const myId = ref('')
const filter = ref('all')
const commentBox = ref({})   // postId -> draft text
const openComments = ref({})  // postId -> bool

const filtered = computed(() =>
  filter.value === 'all' ? posts.value : posts.value.filter(p => p.type === filter.value)
)
function toggleComments(p) { openComments.value[p.id] = !openComments.value[p.id] }
async function addComment(p) {
  const text = (commentBox.value[p.id] || '').trim()
  if (!text) return
  try {
    const res = await authFetch(`/api/org/community/posts/${p.id}/comment`, { method: 'POST', body: JSON.stringify({ content: text }) })
    const json = await res.safeJson()
    if (json?.status === 'success') {
      if (!p.comments) p.comments = []
      p.comments.push(json.data)
      commentBox.value[p.id] = ''
    }
  } catch (e) {}
}

const types = computed(() => [
  { key: 'message', label: t('org.community.type_message'), color: '#6366f1' },
  { key: 'cv', label: t('org.community.type_cv'), color: '#10b981' },
  { key: 'portfolio', label: t('org.community.type_portfolio'), color: '#f59e0b' },
  { key: 'offer', label: t('org.community.type_offer'), color: '#0ea5e9' },
  { key: 'interview_result', label: t('org.community.type_interview'), color: '#ec4899' },
])
function typeMeta(k) { return types.value.find(x => x.key === k) || types.value[0] }

async function load() {
  loading.value = true
  try {
    const u = JSON.parse(localStorage.getItem('user') || '{}')
    myId.value = u.id || ''
    const res = await authFetch('/api/org/community/posts')
    const json = await res.safeJson()
    if (json?.status === 'success') posts.value = json.data
  } catch (e) {} finally { loading.value = false }
}

async function publish() {
  if (!draft.value.content.trim()) return
  posting.value = true
  try {
    const res = await authFetch('/api/org/community/posts', { method: 'POST', body: JSON.stringify(draft.value) })
    const json = await res.safeJson()
    if (json?.status === 'success') {
      posts.value.unshift(json.data)
      draft.value = { type: 'message', title: '', content: '', link: '' }
    }
  } catch (e) {} finally { posting.value = false }
}

async function like(p) {
  try { await authFetch(`/api/org/community/posts/${p.id}/like`, { method: 'POST' }); p.likes = (p.likes || 0) + 1 } catch (e) {}
}
async function remove(p) {
  if (!confirm(t('org.community.remove_confirm'))) return
  try {
    const res = await authFetch(`/api/org/community/posts/${p.id}`, { method: 'DELETE' })
    if (res.ok) posts.value = posts.value.filter(x => x.id !== p.id)
  } catch (e) {}
}
function fmtDate(d) { if (!d) return ''; try { return new Date(d).toLocaleString() } catch { return '' } }
function initials(n) { return (n || '?')[0].toUpperCase() }

onMounted(load)
</script>

<template>
  <div class="oc">
    <header class="oc__head">
      <h1 class="oc__title">{{ t('org.nav.community') }}</h1>
      <p class="oc__sub">{{ t('org.community.sub') }}</p>
    </header>

    <!-- Composer -->
    <div class="oc__composer">
      <div class="oc__types">
        <button v-for="ty in types" :key="ty.key"
          :class="['oc__type', { 'oc__type--active': draft.type === ty.key }]"
          :style="draft.type === ty.key ? { background: ty.color, borderColor: ty.color, color: '#fff' } : {}"
          @click="draft.type = ty.key">{{ ty.label }}</button>
      </div>
      <input v-if="draft.type !== 'message'" v-model="draft.title" :placeholder="t('org.community.title_ph')" class="oc__input" />
      <textarea v-model="draft.content" :placeholder="t('org.community.content_ph')" class="oc__input oc__textarea"></textarea>
      <input v-if="draft.type !== 'message'" v-model="draft.link" :placeholder="t('org.community.link_ph')" class="oc__input" />
      <div class="oc__composer-foot">
        <button class="oc__publish" @click="publish" :disabled="posting">
          <PaperAirplaneIcon class="w-4 h-4" /> {{ posting ? t('org.community.publishing') : t('org.community.publish') }}
        </button>
      </div>
    </div>

    <!-- Filter bar -->
    <div class="oc__filters">
      <button :class="['oc__filter', { 'oc__filter--active': filter === 'all' }]" @click="filter = 'all'">{{ t('org.community.all') }}</button>
      <button v-for="ty in types" :key="ty.key" :class="['oc__filter', { 'oc__filter--active': filter === ty.key }]" @click="filter = ty.key">{{ ty.label }}</button>
    </div>

    <div v-if="loading" class="oc__loading">{{ t('common.loading') }}…</div>
    <div v-else-if="!filtered.length" class="oc__empty">{{ t('org.community.empty') }}</div>

    <div v-else class="oc__feed">
      <article v-for="p in filtered" :key="p.id" class="oc__post">
        <div class="oc__post-head">
          <div class="oc__avatar">{{ initials(p.author_name) }}</div>
          <div class="oc__post-meta">
            <span class="oc__post-author">{{ p.author_name }}</span>
            <span v-if="p.author_role !== 'member'" class="oc__author-badge">{{ p.author_role }}</span>
            <span class="oc__post-date">{{ fmtDate(p.created_at) }}</span>
          </div>
          <span class="oc__badge" :style="{ background: typeMeta(p.type).color + '22', color: typeMeta(p.type).color }">{{ typeMeta(p.type).label }}</span>
          <button v-if="p.author_id === myId" class="oc__del" @click="remove(p)"><TrashIcon class="w-4 h-4" /></button>
        </div>
        <h3 v-if="p.title" class="oc__post-title">{{ p.title }}</h3>
        <p class="oc__post-content">{{ p.content }}</p>
        <a v-if="p.link" :href="p.link" target="_blank" class="oc__post-link"><LinkIcon class="w-3.5 h-3.5" /> {{ p.link }}</a>
        <div class="oc__post-foot">
          <button class="oc__like" @click="like(p)"><HeartIcon class="w-4 h-4" /> {{ p.likes || 0 }}</button>
          <button class="oc__comment-btn" @click="toggleComments(p)">
            <ChatBubbleOvalLeftIcon class="w-4 h-4" /> {{ (p.comments && p.comments.length) || 0 }}
          </button>
        </div>

        <!-- Comments -->
        <div v-if="openComments[p.id]" class="oc__comments">
          <div v-for="c in (p.comments || [])" :key="c.id" class="oc__comment">
            <div class="oc__comment-avatar">{{ initials(c.author_name) }}</div>
            <div class="oc__comment-body">
              <span class="oc__comment-author">{{ c.author_name }}</span>
              <span class="oc__comment-text">{{ c.content }}</span>
            </div>
          </div>
          <div class="oc__comment-add">
            <input v-model="commentBox[p.id]" :placeholder="t('org.community.comment_ph')" class="oc__comment-input" @keyup.enter="addComment(p)" />
            <button class="oc__comment-send" @click="addComment(p)">{{ t('org.community.comment_send') }}</button>
          </div>
        </div>
      </article>
    </div>
  </div>
</template>

<style scoped>
.oc { max-width: 780px; margin: 0 auto; color: #1E293B; }
.oc__head { margin-bottom: 1.25rem; }
.oc__title { font-size: 1.7rem; font-weight: 800; margin: 0; letter-spacing: -0.02em; }
.oc__sub { color: #64748B; font-size: 0.9rem; margin: 0.3rem 0 0; }
.oc__loading, .oc__empty { padding: 2.5rem; text-align: center; color: #94A3B8; }

.oc__composer { background: #fff; border: 1px solid #E2E8F0; border-radius: 1.1rem; padding: 1.1rem; margin-bottom: 1.5rem; box-shadow: 0 1px 2px rgba(15,23,42,0.04), 0 10px 30px -22px rgba(15,23,42,0.3); }
.oc__types { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 0.8rem; }
.oc__type { padding: 0.4rem 0.75rem; border-radius: 999px; border: 1px solid #E2E8F0; background: #F8FAFC; color: #64748B; font-size: 0.72rem; font-weight: 700; cursor: pointer; transition: all 0.15s; }
.oc__type:hover { border-color: #CBD5E1; }
.oc__input { width: 100%; padding: 0.65rem 0.85rem; border-radius: 0.6rem; background: #F8FAFC; border: 1px solid #E2E8F0; color: #1E293B; font-size: 0.85rem; outline: none; margin-bottom: 0.5rem; }
.oc__input:focus { border-color: #F59E0B; box-shadow: 0 0 0 3px rgba(245,158,11,0.12); background: #fff; }
.oc__textarea { resize: vertical; min-height: 68px; }
.oc__composer-foot { display: flex; justify-content: flex-end; }
.oc__publish { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.6rem 1.2rem; border-radius: 0.6rem; background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; border: none; font-weight: 700; font-size: 0.82rem; cursor: pointer; box-shadow: 0 6px 16px -6px rgba(245,158,11,0.6); }

.oc__feed { display: flex; flex-direction: column; gap: 1rem; }
.oc__post { background: #fff; border: 1px solid #E2E8F0; border-radius: 1.1rem; padding: 1.2rem; box-shadow: 0 1px 2px rgba(15,23,42,0.04); }
.oc__post-head { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.7rem; }
.oc__avatar { width: 2.4rem; height: 2.4rem; border-radius: 50%; background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 800; flex-shrink: 0; box-shadow: 0 4px 12px -3px rgba(245,158,11,0.5); }
.oc__post-meta { display: flex; flex-direction: column; flex: 1; min-width: 0; }
.oc__post-author { font-weight: 700; font-size: 0.85rem; color: #1E293B; }
.oc__author-badge { font-size: 0.58rem; text-transform: uppercase; color: #4F46E5; font-weight: 700; }
.oc__post-date { font-size: 0.68rem; color: #94A3B8; }
.oc__badge { font-size: 0.62rem; font-weight: 800; padding: 0.22rem 0.6rem; border-radius: 999px; text-transform: uppercase; }
.oc__del { background: none; border: none; color: #FCA5A5; cursor: pointer; }
.oc__del:hover { color: #EF4444; }
.oc__post-title { font-size: 1.02rem; font-weight: 700; color: #0F172A; margin: 0 0 0.35rem; }
.oc__post-content { font-size: 0.88rem; line-height: 1.55; color: #334155; margin: 0; white-space: pre-wrap; }
.oc__post-link { display: inline-flex; align-items: center; gap: 0.3rem; font-size: 0.76rem; color: #D97706; text-decoration: none; margin-top: 0.7rem; word-break: break-all; font-weight: 600; }
.oc__post-foot { margin-top: 0.9rem; display: flex; gap: 0.5rem; }
.oc__like, .oc__comment-btn { display: inline-flex; align-items: center; gap: 0.35rem; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 999px; padding: 0.35rem 0.85rem; color: #64748B; font-size: 0.78rem; font-weight: 600; cursor: pointer; transition: all 0.15s; }
.oc__like:hover { color: #EC4899; border-color: #F9A8D4; background: #FDF2F8; }
.oc__comment-btn:hover { color: #4F46E5; border-color: #C7D2FE; background: #EEF2FF; }

.oc__filters { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 1.25rem; }
.oc__filter { padding: 0.4rem 0.85rem; border-radius: 999px; border: 1px solid #E2E8F0; background: #fff; color: #64748B; font-size: 0.75rem; font-weight: 700; cursor: pointer; transition: all 0.15s; }
.oc__filter:hover { border-color: #CBD5E1; }
.oc__filter--active { background: #0F172A; color: #fff; border-color: #0F172A; }

.oc__comments { margin-top: 0.9rem; padding-top: 0.9rem; border-top: 1px solid #F1F5F9; display: flex; flex-direction: column; gap: 0.6rem; }
.oc__comment { display: flex; gap: 0.5rem; align-items: flex-start; }
.oc__comment-avatar { width: 1.7rem; height: 1.7rem; border-radius: 50%; background: #E2E8F0; color: #475569; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.7rem; flex-shrink: 0; }
.oc__comment-body { background: #F8FAFC; border: 1px solid #F1F5F9; border-radius: 0.7rem; padding: 0.5rem 0.7rem; }
.oc__comment-author { font-weight: 700; font-size: 0.76rem; color: #334155; margin-right: 0.4rem; }
.oc__comment-text { font-size: 0.8rem; color: #475569; }
.oc__comment-add { display: flex; gap: 0.5rem; margin-top: 0.2rem; }
.oc__comment-input { flex: 1; padding: 0.5rem 0.75rem; border-radius: 0.6rem; background: #F8FAFC; border: 1px solid #E2E8F0; color: #1E293B; font-size: 0.8rem; outline: none; }
.oc__comment-input:focus { border-color: #F59E0B; }
.oc__comment-send { padding: 0.5rem 0.9rem; border-radius: 0.6rem; background: #F59E0B; color: #fff; border: none; font-weight: 700; font-size: 0.76rem; cursor: pointer; }
</style>
