<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useHead } from '@unhead/vue'
import { authFetch } from '@/utils/auth'
import { BoltIcon, CheckBadgeIcon, SparklesIcon, ArrowPathIcon } from '@heroicons/vue/24/outline'

const { t } = useI18n()
const route = useRoute()
const balance = ref(0)
const packs = ref([])
const txs = ref([])
const loading = ref(true)
const buying = ref('')

useHead({ title: computed(() => t('shop.title') + ' | GoldArmy') })

const costs = computed(() => [
  { key: 'cv_audit', gold: 10 }, { key: 'follow_up', gold: 5 }, { key: 'sniper_search', gold: 15 },
  { key: 'cv_adaptation', gold: 18 }, { key: 'hr_interview', gold: 10 }, { key: 'portfolio', gold: 15 },
])

async function load() {
  loading.value = true
  try {
    const [bRes, pRes, tRes] = await Promise.all([
      authFetch('/api/gold/balance'), authFetch('/api/shop/packs'), authFetch('/api/gold/transactions'),
    ])
    const bJson = await bRes.safeJson(); const pJson = await pRes.safeJson(); const tJson = await tRes.safeJson()
    if (bJson?.status === 'success') balance.value = bJson.data.balance
    if (pJson?.status === 'success') packs.value = pJson.data
    if (tJson?.status === 'success') txs.value = tJson.data
  } catch (e) {} finally { loading.value = false }
}

async function buy(pack) {
  buying.value = pack.key
  try {
    const res = await authFetch('/api/shop/checkout', { method: 'POST', body: JSON.stringify({ pack: pack.key }) })
    const json = await res.safeJson()
    if (json?.url) window.location.href = json.url
    else alert(json?.detail || t('common.error'))
  } catch (e) { alert(t('common.error')) } finally { buying.value = '' }
}

function fmtDate(d) { try { return new Date(d).toLocaleDateString() } catch { return '' } }
function txLabel(tx) {
  if (tx.reason === 'signup') return t('shop.tx_signup')
  if (tx.reason?.startsWith('pack:')) return t('shop.tx_pack')
  if (tx.reason?.startsWith('feature:')) return t('shop.tx_feature', { f: tx.reason.split(':')[1] })
  if (tx.reason === 'org_monthly') return t('shop.tx_org')
  return tx.reason
}

onMounted(load)
</script>

<template>
  <div class="shop">
    <header class="shop__head">
      <div>
        <h1 class="shop__title">{{ t('shop.title') }}</h1>
        <p class="shop__sub">{{ t('shop.sub') }}</p>
      </div>
      <div class="shop__balance">
        <BoltIcon class="w-6 h-6" />
        <div>
          <div class="shop__balance-num">{{ balance }}</div>
          <div class="shop__balance-lbl">{{ t('shop.your_gold') }}</div>
        </div>
      </div>
    </header>

    <div v-if="route.query.status === 'success'" class="shop__banner">
      <CheckBadgeIcon class="w-5 h-5" /> {{ t('shop.success') }}
    </div>

    <div v-if="loading" class="shop__loading">{{ t('common.loading') }}…</div>

    <template v-else>
      <!-- Packs -->
      <div class="shop__packs">
        <div v-for="p in packs" :key="p.key" :class="['shop__pack', { 'shop__pack--best': p.badge === 'best' }]">
          <div v-if="p.badge === 'best'" class="shop__pack-badge"><SparklesIcon class="w-3.5 h-3.5" /> {{ t('shop.best') }}</div>
          <div class="shop__pack-gold"><BoltIcon class="w-5 h-5" /> {{ p.total_gold }}</div>
          <div class="shop__pack-name">{{ p.name }}</div>
          <div v-if="p.bonus" class="shop__pack-bonus">+{{ p.bonus }} {{ t('shop.bonus') }}</div>
          <div class="shop__pack-price">{{ p.price_eur.toFixed(2) }}€</div>
          <button class="shop__pack-btn" @click="buy(p)" :disabled="buying === p.key">
            {{ buying === p.key ? '…' : t('shop.buy') }}
          </button>
        </div>
      </div>

      <!-- Subscription callout (tokens récurrents) -->
      <router-link to="/tarifs" class="shop__sub-cta">
        <div class="shop__sub-cta-left">
          <SparklesIcon class="w-5 h-5" />
          <div>
            <div class="shop__sub-cta-title">{{ t('shop.sub_cta_title') }}</div>
            <div class="shop__sub-cta-desc">{{ t('shop.sub_cta_desc') }}</div>
          </div>
        </div>
        <span class="shop__sub-cta-btn">{{ t('shop.sub_cta_btn') }} →</span>
      </router-link>

      <div class="shop__cols">
        <!-- How it works / costs -->
        <section class="shop__card">
          <h2 class="shop__card-title">{{ t('shop.costs_title') }}</h2>
          <p class="shop__card-desc">{{ t('shop.costs_desc') }}</p>
          <ul class="shop__costs">
            <li v-for="c in costs" :key="c.key">
              <span>{{ t('shop.feat_' + c.key) }}</span>
              <span class="shop__cost-val"><BoltIcon class="w-3.5 h-3.5" /> {{ c.gold }}</span>
            </li>
          </ul>
        </section>

        <!-- Transactions -->
        <section class="shop__card">
          <div class="shop__card-head">
            <h2 class="shop__card-title">{{ t('shop.history') }}</h2>
            <button class="shop__refresh" @click="load"><ArrowPathIcon class="w-4 h-4" /></button>
          </div>
          <div v-if="!txs.length" class="shop__empty">{{ t('shop.no_tx') }}</div>
          <ul v-else class="shop__txs">
            <li v-for="(tx, i) in txs" :key="i" class="shop__tx">
              <div><div class="shop__tx-label">{{ txLabel(tx) }}</div><div class="shop__tx-date">{{ fmtDate(tx.created_at) }}</div></div>
              <span :class="['shop__tx-amt', tx.type === 'grant' ? 'shop__tx-amt--up' : 'shop__tx-amt--down']">
                {{ tx.type === 'grant' ? '+' : '−' }}{{ tx.amount }}
              </span>
            </li>
          </ul>
        </section>
      </div>
    </template>
  </div>
</template>

<style scoped>
.shop { max-width: 1100px; margin: 0 auto; padding: 1.5rem; color: #0F172A; }
.shop__head { display: flex; align-items: flex-end; justify-content: space-between; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.shop__title { font-size: 1.8rem; font-weight: 800; margin: 0; letter-spacing: -0.02em; }
.shop__sub { color: #64748B; font-size: 0.92rem; margin: 0.3rem 0 0; }
.shop__balance { display: flex; align-items: center; gap: 0.7rem; padding: 0.8rem 1.3rem; border-radius: 1.2rem; background: linear-gradient(135deg, #1E293B, #0F172A); color: #FBBF24; box-shadow: 0 10px 26px -12px rgba(15,23,42,0.5); }
.shop__balance-num { font-size: 1.6rem; font-weight: 800; line-height: 1; color: #fff; }
.shop__balance-lbl { font-size: 0.66rem; text-transform: uppercase; letter-spacing: 0.05em; color: #FBBF24; margin-top: 0.15rem; }
.shop__banner { display: flex; align-items: center; gap: 0.5rem; padding: 0.85rem 1.1rem; border-radius: 1rem; background: #D1FAE5; color: #059669; border: 1px solid #A7F3D0; font-weight: 600; font-size: 0.85rem; margin-bottom: 1.2rem; }
.shop__loading { padding: 3rem; text-align: center; color: #94A3B8; }

.shop__packs { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 1rem; margin-bottom: 1.3rem; }
.shop__pack { position: relative; background: #fff; border: 1px solid #E2E8F0; border-radius: 1.4rem; padding: 1.5rem 1.3rem; text-align: center; box-shadow: 0 1px 2px rgba(15,23,42,0.04); transition: transform 0.15s, box-shadow 0.15s; }
.shop__pack:hover { transform: translateY(-4px); box-shadow: 0 18px 36px -20px rgba(245,158,11,0.5); }
.shop__pack--best { border-color: #F59E0B; box-shadow: 0 16px 34px -18px rgba(245,158,11,0.5); }
.shop__pack-badge { position: absolute; top: -0.7rem; left: 50%; transform: translateX(-50%); display: inline-flex; align-items: center; gap: 0.25rem; font-size: 0.62rem; font-weight: 800; text-transform: uppercase; padding: 0.25rem 0.7rem; border-radius: 999px; background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; white-space: nowrap; }
.shop__pack-gold { display: inline-flex; align-items: center; gap: 0.3rem; font-size: 2rem; font-weight: 800; color: #D97706; }
.shop__pack-name { font-size: 0.9rem; font-weight: 700; margin-top: 0.3rem; }
.shop__pack-bonus { font-size: 0.72rem; font-weight: 700; color: #059669; margin-top: 0.2rem; }
.shop__pack-price { font-size: 1.3rem; font-weight: 800; margin: 0.8rem 0; color: #0F172A; }
.shop__pack-btn { width: 100%; padding: 0.7rem; border-radius: 0.9rem; border: none; background: linear-gradient(135deg, #FBBF24, #F59E0B); color: #fff; font-weight: 800; font-size: 0.88rem; cursor: pointer; box-shadow: 0 8px 18px -8px rgba(245,158,11,0.6); }
.shop__pack-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.shop__sub-cta { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: 1.1rem 1.4rem; border-radius: 1.4rem; margin-bottom: 1.3rem; background: linear-gradient(135deg, #1E293B, #0F172A); color: #fff; text-decoration: none; box-shadow: 0 12px 28px -16px rgba(15,23,42,0.6); transition: transform 0.15s; }
.shop__sub-cta:hover { transform: translateY(-2px); }
.shop__sub-cta-left { display: flex; align-items: center; gap: 0.9rem; }
.shop__sub-cta-left svg { color: #FBBF24; flex-shrink: 0; }
.shop__sub-cta-title { font-weight: 800; font-size: 0.95rem; }
.shop__sub-cta-desc { font-size: 0.8rem; color: #94A3B8; margin-top: 0.15rem; }
.shop__sub-cta-btn { flex-shrink: 0; font-weight: 800; font-size: 0.85rem; color: #FBBF24; white-space: nowrap; }
.shop__cols { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.shop__card { background: #fff; border: 1px solid #E2E8F0; border-radius: 1.4rem; padding: 1.4rem; box-shadow: 0 1px 2px rgba(15,23,42,0.04); }
.shop__card-head { display: flex; align-items: center; justify-content: space-between; }
.shop__card-title { font-size: 1rem; font-weight: 800; margin: 0 0 0.3rem; }
.shop__card-desc { font-size: 0.82rem; color: #64748B; margin: 0 0 1rem; }
.shop__refresh { background: none; border: none; color: #94A3B8; cursor: pointer; }
.shop__costs { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.5rem; }
.shop__costs li { display: flex; align-items: center; justify-content: space-between; padding: 0.55rem 0.7rem; border-radius: 0.7rem; background: #F8FAFC; font-size: 0.85rem; }
.shop__cost-val { display: inline-flex; align-items: center; gap: 0.25rem; font-weight: 800; color: #D97706; }
.shop__txs { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.4rem; }
.shop__tx { display: flex; align-items: center; justify-content: space-between; padding: 0.55rem 0.7rem; border-radius: 0.7rem; background: #F8FAFC; }
.shop__tx-label { font-size: 0.82rem; font-weight: 600; }
.shop__tx-date { font-size: 0.68rem; color: #94A3B8; }
.shop__tx-amt { font-weight: 800; font-size: 0.9rem; }
.shop__tx-amt--up { color: #059669; }
.shop__tx-amt--down { color: #DC2626; }
.shop__empty { color: #94A3B8; font-size: 0.85rem; text-align: center; padding: 1.5rem; }
@media (max-width: 720px) { .shop__cols { grid-template-columns: 1fr; } }
</style>
