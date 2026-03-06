import { ref, watch, onMounted } from 'vue'

const STORAGE_KEY = 'goldarmy-theme'

export function useTheme() {
  const theme = ref(
    typeof localStorage !== 'undefined' ? localStorage.getItem(STORAGE_KEY) || 'dark' : 'dark'
  )

  function toggleTheme() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
    localStorage.setItem(STORAGE_KEY, theme.value)
    applyThemeToDocument(theme.value)
  }

  function applyThemeToDocument(value) {
    if (typeof document === 'undefined') return
    const root = document.getElementById('app')
    if (!root) return
    root.classList.remove('theme-light', 'theme-dark')
    if (value === 'light') root.classList.add('theme-light')
    else root.classList.add('theme-dark')
  }

  onMounted(() => {
    applyThemeToDocument(theme.value)
  })

  watch(theme, (value) => {
    applyThemeToDocument(value)
  }, { immediate: true })

  return { theme, toggleTheme, isLight: () => theme.value === 'light' }
}
