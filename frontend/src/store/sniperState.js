import { reactive, watch } from 'vue'

const SNIPER_STORAGE_KEY = 'goldarmy_sniper_state'

const loadState = () => {
    try {
        const stored = localStorage.getItem(SNIPER_STORAGE_KEY)
        if (stored) return JSON.parse(stored)
    } catch (e) {
        console.error('Error parsing sniper state', e)
    }
    return null
}

const saved = loadState()

// Global state for Sniper (Opportunities)
export const sniperState = reactive({
    filter: saved?.filter || 'Toutes les pertinentes',
    searchQuery: saved?.searchQuery || '',
    inputLocation: saved?.inputLocation || '',
    cvText: saved?.cvText || '',
    selectedFileName: saved?.selectedFileName || '',
    resultLimit: saved?.resultLimit || 50,
    jobs: saved?.jobs || [],

    // UI state
    isUploading: false,
    isLoading: false,
    isParsingPdf: false,

    // Adapted CV Modal state
    showAdaptModal: false,
    isAdaptingCV: false,
    adaptingJobId: null,
    adaptedData: null,

    // Radar state
    loadingRadarFor: null
})

// Persist relevant data
watch(() => ({
    filter: sniperState.filter,
    searchQuery: sniperState.searchQuery,
    inputLocation: sniperState.inputLocation,
    cvText: sniperState.cvText,
    selectedFileName: sniperState.selectedFileName,
    resultLimit: sniperState.resultLimit,
    jobs: sniperState.jobs
}), (newVal) => {
    localStorage.setItem(SNIPER_STORAGE_KEY, JSON.stringify(newVal))
}, { deep: true })
