<script setup>
// Espace Communauté côté application (membres affiliés à une organisation).
// Réutilise le composant Discord-like de l'espace organisation : mêmes endpoints
// (/api/org/community/*, accessibles à tout membre via get_current_org_member).
import OrgCommunity from './org/OrgCommunity.vue'
</script>

<template>
  <div class="app-embed">
    <OrgCommunity />
  </div>
</template>

<style scoped>
.app-embed {
  min-height: 100%;
  background: #F9FAFB;
  padding: 1.5rem 1.5rem 2rem;
}
@media (max-width: 640px) {
  .app-embed { padding: 1rem; }
}
</style>
