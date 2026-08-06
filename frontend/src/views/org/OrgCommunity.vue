<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { authFetch } from '@/utils/auth'
import {
  HashtagIcon, PaperAirplaneIcon, HeartIcon, ChatBubbleOvalLeftIcon,
  TrashIcon, LinkIcon, DocumentTextIcon, BriefcaseIcon, SparklesIcon,
  MegaphoneIcon, UsersIcon, DocumentArrowUpIcon, ArrowDownTrayIcon
} from '@heroicons/vue/24/outline'

const { t } = useI18n()
const loading = ref(true)
const posts = ref([])
const roster = ref([])
const activeChannel = ref('message')
const draft = ref({ content: '', title: '', link: '' })
const posting = ref(false)
const myId = ref('')
const openComments = ref({})
const commentBox = ref({})
const streamRef = ref(null)
const cvInput = ref(null)
const uploading = ref(false)
let poll = null

function scoreClass(s) { return s >= 75 ? 'ok' : s >= 55 ? 'mid' : 'low' }

async function uploadCv(e) {
  const file = e.target.files?.[0]
  if (!file) return
  if (!file.name.toLowerCase().endsWith('.pdf')) { alert(t('org.community.cv_pdf_only')); return }
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    const res = await authFetch('/api/org/community/cv', { method: 'POST', body: fd })
    const json = await res.safeJson()
    if (res.ok && json?.status === 'success') { posts.value.push(json.data); scrollBottom() }
    else alert(json?.detail || t('common.error'))
  } catch (err) { alert(t('common.error')) }
  finally { uploading.value = false; if (cvInput.value) cvInput.value.value = '' }
}

const channels = computed(() => [
  { key: 'message', name: t('org.community.ch_general'), icon: HashtagIcon },
  { key: 'cv', name: t('org.community.ch_cv'), icon: DocumentTextIcon },
  { key: 'portfolio', name: t('org.community.ch_portfolio'), icon: SparklesIcon },
  { key: 'offer', name: t('org.community.ch_offer'), icon: BriefcaseIcon },
  { key: 'interview_result', name: t('org.community.ch_interview'), icon: MegaphoneIcon },
])
const activeChannelMeta = computed(() => channels.value.find(c => c.key === activeChannel.value) || channels.value[0])
const isResourceChannel = computed(() => activeChannel.value !== 'message')

const messages = computed(() =>
  posts.value
    .filter(p => p.type === activeChannel.value)
    .slice()
    .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
)
function channelCount(key) { return posts.value.filter(p => p.type === key).length }

const ROLE_GROUPS = computed(() => {
  const g = { org_admin: [], mentor: [], advisor: [], member: [] }
  roster.value.forEach(r => { (g[r.role] || g.member).push(r) })
  return [
    { key: 'org_admin', label: t('org.nav.admin_badge'), people: g.org_admin, color: '#F59E0B' },
    { key: 'mentor', label: t('org.roles.mentor'), people: g.mentor, color: '#6366F1' },
    { key: 'advisor', label: t('org.roles.advisor'), people: g.advisor, color: '#10B981' },
    { key: 'member', label: t('org.roles.member'), people: g.member, color: '#98A2B3' },
  ].filter(grp => grp.people.length)
})

function initials(n) { return (n || '?')[0].toUpperCase() }
function roleColor(r) { return r === 'org_admin' ? '#F59E0B' : r === 'mentor' ? '#6366F1' : r === 'advisor' ? '#10B981' : '#98A2B3' }
function fmtTime(d) { try { return new Date(d).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' }) } catch { return '' } }

async function scrollBottom() { await nextTick(); if (streamRef.value) streamRef.value.scrollTop = streamRef.value.scrollHeight }

async function loadPosts(scroll = false) {
  try {
    const res = await authFetch('/api/org/community/posts')
    const json = await res.safeJson()
    if (json?.status === 'success') { posts.value = json.data; if (scroll) scrollBottom() }
  } catch (e) {}
}
async function loadRoster() {
  try {
    const res = await authFetch('/api/org/community/members')
    const json = await res.safeJson()
    if (json?.status === 'success') roster.value = json.data
  } catch (e) {}
}

async function publish() {
  if (!draft.value.content.trim()) return
  posting.value = true
  try {
    const body = { type: activeChannel.value, content: draft.value.content, title: draft.value.title, link: draft.value.link }
    const res = await authFetch('/api/org/community/posts', { method: 'POST', body: JSON.stringify(body) })
    const json = await res.safeJson()
    if (json?.status === 'success') {
      posts.value.push(json.data)
      draft.value = { content: '', title: '', link: '' }
      scrollBottom()
    }
  } catch (e) {} finally { posting.value = false }
}
async function like(p) { try { await authFetch(`/api/org/community/posts/${p.id}/like`, { method: 'POST' }); p.likes = (p.likes || 0) + 1 } catch (e) {} }
async function remove(p) {
  if (!confirm(t('org.community.remove_confirm'))) return
  try { const res = await authFetch(`/api/org/community/posts/${p.id}`, { method: 'DELETE' }); if (res.ok) posts.value = posts.value.filter(x => x.id !== p.id) } catch (e) {}
}
function toggleComments(p) { openComments.value[p.id] = !openComments.value[p.id] }
async function addComment(p) {
  const text = (commentBox.value[p.id] || '').trim()
  if (!text) return
  try {
    const res = await authFetch(`/api/org/community/posts/${p.id}/comment`, { method: 'POST', body: JSON.stringify({ content: text }) })
    const json = await res.safeJson()
    if (json?.status === 'success') { if (!p.comments) p.comments = []; p.comments.push(json.data); commentBox.value[p.id] = '' }
  } catch (e) {}
}
function selectChannel(k) { activeChannel.value = k; scrollBottom() }

onMounted(async () => {
  try {
    const u = JSON.parse(localStorage.getItem('user') || '{}'); myId.value = u.id || ''
  } catch (e) {}
  await Promise.all([loadPosts(), loadRoster()])
  loading.value = false
  scrollBottom()
  poll = setInterval(() => loadPosts(false), 12000)
})
onUnmounted(() => { if (poll) clearInterval(poll) })
</script>

<template>
  <div class="oc">
    <header class="oc__head">
      <h1 class="oc__title">{{ t('org.nav.community') }}</h1>
      <p class="oc__sub">{{ t('org.community.sub') }}</p>
    </header>

    <div class="oc__server">
      <!-- Channels -->
      <aside class="oc__channels">
        <div class="oc__channels-label">{{ t('org.community.channels') }}</div>
        <button v-for="c in channels" :key="c.key"
          :class="['oc__channel', { 'oc__channel--active': activeChannel === c.key }]"
          @click="selectChannel(c.key)">
          <component :is="c.icon" class="w-4 h-4 shrink-0" />
          <span class="oc__channel-name">{{ c.name }}</span>
          <span v-if="channelCount(c.key)" class="oc__channel-count">{{ channelCount(c.key) }}</span>
        </button>
      </aside>

      <!-- Messages -->
      <section class="oc__chat">
        <div class="oc__chat-head">
          <component :is="activeChannelMeta.icon" class="w-5 h-5" />
          <span class="oc__chat-title">{{ activeChannelMeta.name }}</span>
          <span class="oc__chat-topic">{{ t('org.community.ch_topic_' + activeChannel) }}</span>
        </div>

        <div ref="streamRef" class="oc__stream">
          <div v-if="loading" class="oc__loading">{{ t('common.loading') }}…</div>
          <div v-else-if="!messages.length" class="oc__empty">
            <component :is="activeChannelMeta.icon" class="oc__empty-ic" />
            <p>{{ t('org.community.channel_empty') }}</p>
          </div>

          <div v-for="p in messages" :key="p.id" class="oc__msg">
            <div class="oc__msg-avatar" :style="{ background: roleColor(p.author_role) }">{{ initials(p.author_name) }}</div>
            <div class="oc__msg-body">
              <div class="oc__msg-head">
                <span class="oc__msg-author">{{ p.author_name }}</span>
                <span v-if="p.author_role && p.author_role !== 'member'" class="oc__msg-role" :style="{ color: roleColor(p.author_role) }">{{ p.author_role === 'org_admin' ? t('org.nav.admin_badge') : (p.author_role === 'mentor' ? t('org.roles.mentor') : t('org.roles.advisor')) }}</span>
                <span class="oc__msg-time">{{ fmtTime(p.created_at) }}</span>
                <button v-if="p.author_id === myId" class="oc__msg-del" @click="remove(p)"><TrashIcon class="w-3.5 h-3.5" /></button>
              </div>

              <!-- CV file card: preview + ATS score + download -->
              <div v-if="p.file_url" class="oc__cv">
                <div class="oc__cv-head">
                  <div class="oc__cv-name">📄 {{ p.file_name || p.title }}</div>
                  <div :class="['oc__cv-score', 'oc__cv-score--' + scoreClass(p.ats_score || 0)]">
                    <span class="oc__cv-score-num">{{ p.ats_score || 0 }}</span><span class="oc__cv-score-lbl">ATS</span>
                  </div>
                </div>
                <iframe :src="p.file_url + '#toolbar=0&view=FitH'" class="oc__cv-preview" loading="lazy" :title="p.file_name"></iframe>
                <a :href="p.file_url" :download="p.file_name" target="_blank" class="oc__cv-dl">
                  <ArrowDownTrayIcon class="w-4 h-4" /> {{ t('org.community.cv_download') }}
                </a>
              </div>

              <!-- Resource card for non-general channels -->
              <div v-else-if="p.title || p.link" class="oc__resource">
                <div v-if="p.title" class="oc__resource-title">{{ p.title }}</div>
                <p v-if="p.content" class="oc__resource-desc">{{ p.content }}</p>
                <a v-if="p.link" :href="p.link" target="_blank" class="oc__resource-link"><LinkIcon class="w-3.5 h-3.5" /> {{ p.link }}</a>
              </div>
              <p v-else class="oc__msg-text">{{ p.content }}</p>

              <div class="oc__msg-foot">
                <button class="oc__react" @click="like(p)"><HeartIcon class="w-3.5 h-3.5" /> {{ p.likes || 0 }}</button>
                <button class="oc__react" @click="toggleComments(p)"><ChatBubbleOvalLeftIcon class="w-3.5 h-3.5" /> {{ (p.comments && p.comments.length) || 0 }}</button>
              </div>

              <!-- Thread -->
              <div v-if="openComments[p.id]" class="oc__thread">
                <div v-for="c in (p.comments || [])" :key="c.id" class="oc__reply">
                  <div class="oc__reply-avatar">{{ initials(c.author_name) }}</div>
                  <div><span class="oc__reply-author">{{ c.author_name }}</span><span class="oc__reply-text">{{ c.content }}</span></div>
                </div>
                <div class="oc__reply-add">
                  <input v-model="commentBox[p.id]" :placeholder="t('org.community.comment_ph')" @keyup.enter="addComment(p)" />
                  <button @click="addComment(p)"><PaperAirplaneIcon class="w-4 h-4" /></button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Composer -->
        <div class="oc__composer">
          <div v-if="activeChannel === 'cv'" class="oc__cv-upload">
            <input ref="cvInput" type="file" accept=".pdf,application/pdf" class="oc__file-hidden" @change="uploadCv" />
            <button class="oc__cv-upbtn" :disabled="uploading" @click="cvInput?.click()">
              <DocumentArrowUpIcon class="w-4 h-4" /> {{ uploading ? t('org.community.cv_uploading') : t('org.community.cv_upload') }}
            </button>
            <span class="oc__cv-hint">{{ t('org.community.cv_hint') }}</span>
          </div>
          <div v-else-if="isResourceChannel" class="oc__composer-extra">
            <input v-model="draft.title" :placeholder="t('org.community.title_ph')" class="oc__cinput" />
            <input v-model="draft.link" :placeholder="t('org.community.link_ph')" class="oc__cinput" />
          </div>
          <div class="oc__composer-main">
            <textarea v-model="draft.content" rows="1" :placeholder="t('org.community.msg_ph', { ch: activeChannelMeta.name })" class="oc__textarea" @keydown.enter.exact.prevent="publish"></textarea>
            <button class="oc__send" @click="publish" :disabled="posting"><PaperAirplaneIcon class="w-5 h-5" /></button>
          </div>
        </div>
      </section>

      <!-- Members -->
      <aside class="oc__members">
        <div class="oc__members-label"><UsersIcon class="w-3.5 h-3.5" /> {{ t('org.community.members') }} — {{ roster.length }}</div>
        <div v-for="g in ROLE_GROUPS" :key="g.key" class="oc__mgroup">
          <div class="oc__mgroup-label">{{ g.label }} — {{ g.people.length }}</div>
          <div v-for="p in g.people" :key="p.id" class="oc__member">
            <div class="oc__member-avatar" :style="{ background: g.color }">{{ initials(p.name) }}<span class="oc__online"></span></div>
            <span class="oc__member-name">{{ p.name }}</span>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.oc { max-width: 1240px; margin: 0 auto; color: #101828; }
.oc__head { margin-bottom: 1.2rem; }
.oc__title { font-size: 1.9rem; font-weight: 800; margin: 0; letter-spacing: -0.03em; }
.oc__sub { color: #667085; font-size: 0.92rem; margin: 0.3rem 0 0; }

.oc__server { display: grid; grid-template-columns: 210px 1fr 220px; height: calc(100vh - 12rem); min-height: 520px; background: #fff; border: 1px solid #EEF0F3; border-radius: 1.5rem; overflow: hidden; box-shadow: 0 1px 2px rgba(16,24,40,0.03); }

/* Channels */
.oc__channels { background: #F9FAFB; border-right: 1px solid #EEF0F3; padding: 1rem 0.7rem; overflow-y: auto; }
.oc__channels-label { font-size: 0.62rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.09em; color: #98A2B3; margin: 0 0 0.6rem 0.6rem; }
.oc__channel { display: flex; align-items: center; gap: 0.5rem; width: 100%; padding: 0.55rem 0.7rem; border-radius: 0.7rem; border: none; background: none; color: #667085; font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: all 0.15s; }
.oc__channel:hover { background: #F1F3F6; color: #101828; }
.oc__channel--active { background: #FEF6E7; color: #B45309; font-weight: 700; }
.oc__channel-name { flex: 1; text-align: left; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.oc__channel-count { font-size: 0.65rem; font-weight: 700; background: #EAECF0; color: #475467; border-radius: 999px; padding: 0.05rem 0.4rem; }
.oc__channel--active .oc__channel-count { background: #FDE68A; color: #B45309; }

/* Chat */
.oc__chat { display: flex; flex-direction: column; min-width: 0; }
.oc__chat-head { display: flex; align-items: center; gap: 0.5rem; padding: 1rem 1.3rem; border-bottom: 1px solid #EEF0F3; color: #101828; }
.oc__chat-title { font-weight: 800; font-size: 0.95rem; }
.oc__chat-topic { font-size: 0.75rem; color: #98A2B3; border-left: 1px solid #EEF0F3; padding-left: 0.6rem; margin-left: 0.2rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.oc__stream { flex: 1; overflow-y: auto; padding: 1.2rem 1.3rem; display: flex; flex-direction: column; gap: 1.1rem; }
.oc__loading { text-align: center; color: #98A2B3; padding: 2rem; }
.oc__empty { text-align: center; color: #98A2B3; margin: auto; }
.oc__empty-ic { width: 2.6rem; height: 2.6rem; color: #D0D5DD; margin: 0 auto 0.6rem; }

.oc__msg { display: flex; gap: 0.75rem; }
.oc__msg-avatar { width: 2.5rem; height: 2.5rem; border-radius: 50%; color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 800; flex-shrink: 0; }
.oc__msg-body { flex: 1; min-width: 0; }
.oc__msg-head { display: flex; align-items: center; gap: 0.5rem; }
.oc__msg-author { font-weight: 700; font-size: 0.88rem; color: #101828; }
.oc__msg-role { font-size: 0.6rem; font-weight: 800; text-transform: uppercase; }
.oc__msg-time { font-size: 0.68rem; color: #98A2B3; }
.oc__msg-del { margin-left: auto; background: none; border: none; color: #FCA5A5; cursor: pointer; }
.oc__msg-del:hover { color: #EF4444; }
.oc__msg-text { font-size: 0.9rem; line-height: 1.5; color: #344054; margin: 0.2rem 0 0; white-space: pre-wrap; }
.oc__resource { margin-top: 0.4rem; border: 1px solid #EEF0F3; border-left: 3px solid #F59E0B; border-radius: 0.8rem; padding: 0.7rem 0.9rem; background: #FFFBEB; }
.oc__resource-title { font-weight: 700; font-size: 0.88rem; color: #101828; }
.oc__resource-desc { font-size: 0.82rem; color: #475467; margin: 0.3rem 0 0; white-space: pre-wrap; }
.oc__resource-link { display: inline-flex; align-items: center; gap: 0.3rem; font-size: 0.75rem; color: #D97706; font-weight: 600; text-decoration: none; margin-top: 0.5rem; word-break: break-all; }
/* CV file card */
.oc__cv { margin-top: 0.4rem; border: 1px solid #EEF0F3; border-radius: 1rem; overflow: hidden; background: #fff; max-width: 420px; }
.oc__cv-head { display: flex; align-items: center; justify-content: space-between; gap: 0.6rem; padding: 0.7rem 0.9rem; background: #F9FAFB; border-bottom: 1px solid #EEF0F3; }
.oc__cv-name { font-weight: 700; font-size: 0.82rem; color: #101828; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.oc__cv-score { display: flex; align-items: baseline; gap: 0.2rem; padding: 0.2rem 0.55rem; border-radius: 999px; flex-shrink: 0; }
.oc__cv-score-num { font-weight: 800; font-size: 0.95rem; }
.oc__cv-score-lbl { font-size: 0.55rem; font-weight: 800; text-transform: uppercase; opacity: 0.7; }
.oc__cv-score--ok { background: #D1FAE5; color: #059669; }
.oc__cv-score--mid { background: #FEF3C7; color: #B45309; }
.oc__cv-score--low { background: #FEE2E2; color: #DC2626; }
.oc__cv-preview { width: 100%; height: 300px; border: none; display: block; background: #F1F3F6; }
.oc__cv-dl { display: flex; align-items: center; justify-content: center; gap: 0.4rem; padding: 0.6rem; background: #fff; border-top: 1px solid #EEF0F3; color: #D97706; font-weight: 700; font-size: 0.8rem; text-decoration: none; }
.oc__cv-dl:hover { background: #FFFBEB; }

.oc__cv-upload { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.6rem; flex-wrap: wrap; }
.oc__file-hidden { display: none; }
.oc__cv-upbtn { display: inline-flex; align-items: center; gap: 0.45rem; padding: 0.65rem 1.1rem; border-radius: 999px; background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; border: none; font-weight: 700; font-size: 0.82rem; cursor: pointer; box-shadow: 0 8px 18px -8px rgba(245,158,11,0.6); }
.oc__cv-upbtn:disabled { opacity: 0.6; cursor: not-allowed; }
.oc__cv-hint { font-size: 0.72rem; color: #98A2B3; }

.oc__msg-foot { display: flex; gap: 0.5rem; margin-top: 0.5rem; }
.oc__react { display: inline-flex; align-items: center; gap: 0.3rem; padding: 0.25rem 0.6rem; border-radius: 999px; background: #F9FAFB; border: 1px solid #EEF0F3; color: #667085; font-size: 0.72rem; font-weight: 600; cursor: pointer; }
.oc__react:hover { border-color: #D0D5DD; color: #101828; }

.oc__thread { margin-top: 0.7rem; padding-left: 0.7rem; border-left: 2px solid #EEF0F3; display: flex; flex-direction: column; gap: 0.5rem; }
.oc__reply { display: flex; gap: 0.5rem; align-items: flex-start; }
.oc__reply-avatar { width: 1.5rem; height: 1.5rem; border-radius: 50%; background: #EAECF0; color: #475467; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.65rem; flex-shrink: 0; }
.oc__reply-author { font-weight: 700; font-size: 0.74rem; color: #344054; margin-right: 0.4rem; }
.oc__reply-text { font-size: 0.8rem; color: #475467; }
.oc__reply-add { display: flex; gap: 0.4rem; margin-top: 0.2rem; }
.oc__reply-add input { flex: 1; padding: 0.45rem 0.7rem; border-radius: 999px; background: #F9FAFB; border: 1px solid #EEF0F3; font-size: 0.78rem; outline: none; }
.oc__reply-add input:focus { border-color: #F59E0B; }
.oc__reply-add button { background: #F59E0B; color: #fff; border: none; border-radius: 50%; width: 2rem; height: 2rem; display: flex; align-items: center; justify-content: center; cursor: pointer; }

/* Composer */
.oc__composer { padding: 0.9rem 1.3rem 1.1rem; border-top: 1px solid #EEF0F3; }
.oc__composer-extra { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-bottom: 0.5rem; }
.oc__cinput { padding: 0.6rem 0.8rem; border-radius: 0.7rem; background: #F9FAFB; border: 1px solid #EEF0F3; font-size: 0.82rem; outline: none; }
.oc__cinput:focus { border-color: #F59E0B; }
.oc__composer-main { display: flex; align-items: flex-end; gap: 0.6rem; background: #F9FAFB; border: 1px solid #EEF0F3; border-radius: 1rem; padding: 0.5rem 0.5rem 0.5rem 1rem; }
.oc__textarea { flex: 1; border: none; background: none; resize: none; outline: none; font-size: 0.88rem; color: #101828; max-height: 120px; font-family: inherit; padding: 0.35rem 0; }
.oc__send { width: 2.5rem; height: 2.5rem; border-radius: 0.8rem; background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; border: none; display: flex; align-items: center; justify-content: center; cursor: pointer; flex-shrink: 0; box-shadow: 0 6px 14px -6px rgba(245,158,11,0.6); }
.oc__send:disabled { opacity: 0.6; cursor: not-allowed; }

/* Members */
.oc__members { background: #F9FAFB; border-left: 1px solid #EEF0F3; padding: 1rem 0.8rem; overflow-y: auto; }
.oc__members-label { display: flex; align-items: center; gap: 0.35rem; font-size: 0.62rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; color: #98A2B3; margin: 0 0 0.8rem 0.4rem; }
.oc__mgroup { margin-bottom: 1rem; }
.oc__mgroup-label { font-size: 0.6rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; color: #98A2B3; margin: 0 0 0.4rem 0.4rem; }
.oc__member { display: flex; align-items: center; gap: 0.55rem; padding: 0.35rem 0.4rem; border-radius: 0.6rem; }
.oc__member:hover { background: #F1F3F6; }
.oc__member-avatar { position: relative; width: 1.9rem; height: 1.9rem; border-radius: 50%; color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.72rem; flex-shrink: 0; }
.oc__online { position: absolute; right: -1px; bottom: -1px; width: 0.6rem; height: 0.6rem; border-radius: 50%; background: #12B76A; border: 2px solid #F9FAFB; }
.oc__member-name { font-size: 0.82rem; font-weight: 600; color: #344054; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

@media (max-width: 980px) {
  .oc__server { grid-template-columns: 64px 1fr; height: calc(100vh - 10rem); }
  .oc__channel-name, .oc__channels-label { display: none; }
  .oc__channel { justify-content: center; }
  .oc__members { display: none; }
}
</style>
