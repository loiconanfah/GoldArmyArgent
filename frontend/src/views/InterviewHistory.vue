<template>
  <div class="interview-history-page">
    <div class="page-header">
      <div class="header-left">
        <router-link to="/interview" class="back-btn">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
          Retour
        </router-link>
        <div>
          <h1 class="page-title">Historique des Entretiens</h1>
          <p class="page-sub">{{ total }} entretien{{ total !== 1 ? 's' : '' }} réalisé{{ total !== 1 ? 's' : '' }}</p>
        </div>
      </div>
      <router-link to="/interview" class="new-btn">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        Nouvel Entretien
      </router-link>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Chargement de l'historique…</p>
    </div>

    <!-- Empty state -->
    <div v-else-if="sessions.length === 0" class="empty-state">
      <div class="empty-icon">🎤</div>
      <h3>Aucun entretien pour l'instant</h3>
      <p>Complétez votre premier entretien simulé pour voir vos résultats ici.</p>
      <router-link to="/interview" class="new-btn">Démarrer un entretien</router-link>
    </div>

    <!-- Session cards -->
    <div v-else class="sessions-grid">
      <div
        v-for="session in sessions"
        :key="session.session_id"
        class="session-card"
        @click="openDetail(session)"
      >
        <div class="card-header">
          <div class="card-job">
            <span class="job-title">{{ session.job_title }}</span>
            <span class="company" v-if="session.company">@ {{ session.company }}</span>
          </div>
          <span class="decision-badge" :class="decisionClass(session.decision)">
            {{ session.decision }}
          </span>
        </div>

        <div class="card-meta">
          <span class="meta-item">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            {{ formatDate(session.created_at) }}
          </span>
          <span class="meta-item" v-if="session.duration_minutes">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            {{ session.duration_minutes }} min
          </span>
          <span class="meta-item type-badge">
            {{ session.interview_type === 'technical' ? 'Technique' : 'RH' }}
          </span>
        </div>

        <!-- Score bars -->
        <div class="score-row">
          <div v-for="(val, key) in scoreDisplay(session.scores)" :key="key" class="score-item">
            <div class="score-label">{{ val.label }}</div>
            <div class="score-bar-track">
              <div class="score-bar-fill" :style="{ width: (val.value * 10) + '%', background: scoreColor(val.value) }"></div>
            </div>
            <div class="score-num" :style="{ color: scoreColor(val.value) }">{{ val.value }}/10</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Detail Modal -->
    <div v-if="selected" class="modal-overlay" @click.self="selected = null">
      <div class="modal-box">
        <button class="modal-close" @click="selected = null">✕</button>

        <div class="modal-header">
          <div>
            <h2 class="modal-title">{{ selected.job_title }}</h2>
            <p class="modal-company" v-if="selected.company">{{ selected.company }}</p>
          </div>
          <span class="decision-badge lg" :class="decisionClass(selected.decision)">{{ selected.decision }}</span>
        </div>

        <div class="modal-meta">
          <span>{{ formatDate(selected.created_at) }}</span>
          <span v-if="selected.duration_minutes">{{ selected.duration_minutes }} min</span>
          <span>{{ selected.interview_type === 'technical' ? '💻 Technique' : '👥 RH' }}</span>
        </div>

        <!-- Scores -->
        <div class="modal-scores">
          <div v-for="(val, key) in scoreDisplay(selected.scores)" :key="key" class="modal-score-item">
            <div class="modal-score-header">
              <span>{{ val.label }}</span>
              <span :style="{ color: scoreColor(val.value) }">{{ val.value }}/10</span>
            </div>
            <div class="score-bar-track">
              <div class="score-bar-fill" :style="{ width: (val.value * 10) + '%', background: scoreColor(val.value) }"></div>
            </div>
          </div>
        </div>

        <!-- Feedback -->
        <div class="modal-section" v-if="selected.feedback">
          <div v-if="selected.feedback.points_forts?.length">
            <h4 class="section-label points-forts">✅ Points forts</h4>
            <ul class="feedback-list">
              <li v-for="p in selected.feedback.points_forts" :key="p">{{ p }}</li>
            </ul>
          </div>
          <div v-if="selected.feedback.points_amelioration?.length">
            <h4 class="section-label points-amelio">⚠️ Axes d'amélioration</h4>
            <ul class="feedback-list">
              <li v-for="p in selected.feedback.points_amelioration" :key="p">{{ p }}</li>
            </ul>
          </div>
          <div v-if="selected.feedback.conseils">
            <h4 class="section-label conseils">💡 Conseils</h4>
            <p class="conseils-text">{{ selected.feedback.conseils }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router  = useRouter()
const sessions = ref([])
const total    = ref(0)
const loading  = ref(true)
const selected = ref(null)

const API_BASE = import.meta.env.VITE_API_URL || ''

async function fetchHistory() {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`${API_BASE}/api/interview/history?limit=50`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Erreur réseau')
    const data = await res.json()
    sessions.value = data.sessions || []
    total.value    = data.total || 0
  } catch (e) {
    console.error('History fetch error:', e)
  } finally {
    loading.value = false
  }
}

function openDetail(session) {
  selected.value = session
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('fr-CA', {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

function decisionClass(d) {
  if (!d) return ''
  return d === 'Favorable' ? 'favorable' : d === 'Défavorable' ? 'defavorable' : 'reserve'
}

function scoreColor(v) {
  if (v >= 8) return '#10b981'
  if (v >= 6) return '#f59e0b'
  return '#ef4444'
}

function scoreDisplay(scores) {
  if (!scores) return []
  const labels = { technical: 'Technique', communication: 'Communication', soft_skills: 'Soft Skills', overall: 'Global' }
  return Object.entries(scores)
    .filter(([k]) => labels[k])
    .map(([k, v]) => ({ label: labels[k], value: v }))
}

onMounted(fetchHistory)
</script>

<style scoped>
.interview-history-page {
  min-height: 100vh;
  background: #0f172a;
  color: #e2e8f0;
  padding: 32px 24px;
  max-width: 900px;
  margin: 0 auto;
}

/* Header */
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 32px;
  gap: 16px;
}
.header-left { display: flex; align-items: center; gap: 20px; }
.back-btn {
  display: flex; align-items: center; gap: 6px;
  color: #94a3b8; text-decoration: none; font-size: 14px;
  padding: 8px 12px; border-radius: 8px; border: 1px solid #1e293b;
  transition: all .2s;
}
.back-btn:hover { color: #e2e8f0; background: #1e293b; }
.page-title { font-size: 24px; font-weight: 700; margin: 0 0 4px; }
.page-sub { font-size: 14px; color: #64748b; margin: 0; }

.new-btn {
  display: flex; align-items: center; gap: 8px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white; text-decoration: none; font-size: 14px; font-weight: 600;
  padding: 10px 18px; border-radius: 10px; border: none; cursor: pointer;
  transition: opacity .2s; white-space: nowrap;
}
.new-btn:hover { opacity: .85; }

/* Loading / Empty */
.loading-state, .empty-state {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; padding: 80px 20px; gap: 16px; text-align: center;
}
.spinner {
  width: 40px; height: 40px; border: 3px solid #1e293b;
  border-top-color: #6366f1; border-radius: 50%;
  animation: spin .8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.empty-icon { font-size: 48px; }
.empty-state h3 { font-size: 20px; font-weight: 700; margin: 0; }
.empty-state p { color: #64748b; margin: 0; }

/* Grid */
.sessions-grid { display: grid; gap: 16px; }

.session-card {
  background: #1e293b; border: 1px solid #334155;
  border-radius: 16px; padding: 20px 24px; cursor: pointer;
  transition: all .2s;
}
.session-card:hover { border-color: #6366f1; transform: translateY(-2px); }

.card-header {
  display: flex; justify-content: space-between;
  align-items: flex-start; margin-bottom: 10px; gap: 12px;
}
.card-job { display: flex; flex-direction: column; gap: 2px; }
.job-title { font-weight: 700; font-size: 16px; color: #f1f5f9; }
.company { font-size: 13px; color: #94a3b8; }

/* Decision badges */
.decision-badge {
  padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700;
  white-space: nowrap;
}
.decision-badge.lg { font-size: 14px; padding: 6px 16px; }
.favorable   { background: #064e3b; color: #34d399; }
.reserve     { background: #451a03; color: #fbbf24; }
.defavorable { background: #450a0a; color: #f87171; }

/* Meta */
.card-meta { display: flex; align-items: center; gap: 16px; margin-bottom: 14px; }
.meta-item {
  display: flex; align-items: center; gap: 5px;
  font-size: 12px; color: #64748b;
}
.type-badge {
  background: #1e3a5f; color: #60a5fa; padding: 2px 8px;
  border-radius: 6px; font-weight: 600;
}

/* Score bars */
.score-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.score-item { display: flex; flex-direction: column; gap: 4px; }
.score-label { font-size: 11px; color: #64748b; }
.score-bar-track {
  height: 5px; background: #0f172a; border-radius: 3px; overflow: hidden;
}
.score-bar-fill { height: 100%; border-radius: 3px; transition: width .4s; }
.score-num { font-size: 11px; font-weight: 700; }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,.7);
  display: flex; align-items: center; justify-content: center;
  z-index: 999; padding: 20px;
}
.modal-box {
  background: #1e293b; border: 1px solid #334155; border-radius: 20px;
  padding: 28px; max-width: 600px; width: 100%; max-height: 90vh;
  overflow-y: auto; position: relative;
}
.modal-close {
  position: absolute; top: 16px; right: 16px;
  background: none; border: none; color: #64748b; font-size: 18px;
  cursor: pointer; padding: 4px 8px; border-radius: 6px;
}
.modal-close:hover { color: #e2e8f0; background: #334155; }

.modal-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 12px; gap: 12px;
}
.modal-title { font-size: 20px; font-weight: 800; margin: 0 0 4px; }
.modal-company { color: #94a3b8; margin: 0; font-size: 14px; }
.modal-meta {
  display: flex; gap: 16px; font-size: 13px; color: #64748b;
  margin-bottom: 20px; flex-wrap: wrap;
}

/* Modal scores */
.modal-scores { display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px; }
.modal-score-item { display: flex; flex-direction: column; gap: 6px; }
.modal-score-header {
  display: flex; justify-content: space-between;
  font-size: 13px; font-weight: 600;
}

/* Feedback */
.modal-section { display: flex; flex-direction: column; gap: 16px; }
.section-label {
  font-size: 13px; font-weight: 700; margin: 0 0 8px;
}
.points-forts { color: #10b981; }
.points-amelio { color: #f59e0b; }
.conseils { color: #60a5fa; }

.feedback-list {
  margin: 0; padding-left: 18px;
  display: flex; flex-direction: column; gap: 6px;
}
.feedback-list li { font-size: 14px; color: #cbd5e1; line-height: 1.5; }
.conseils-text { font-size: 14px; color: #cbd5e1; line-height: 1.6; margin: 0; }

@media (max-width: 640px) {
  .score-row { grid-template-columns: repeat(2, 1fr); }
  .page-header { flex-direction: column; }
}
</style>
