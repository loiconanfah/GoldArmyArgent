<script setup>
// Hub Mentors côté application (membres affiliés à une organisation).
// Réutilise le composant Mentors de l'espace organisation en mode "consultation"
// (memberMode) : liste des mentors/conseillers + événements avec RSVP,
// sans les contrôles d'administration (création/suppression/assignation).
import OrgMentors from './org/OrgMentors.vue'
</script>

<template>
  <div class="app-embed">
    <OrgMentors :member-mode="true" />
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
