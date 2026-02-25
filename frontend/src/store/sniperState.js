import { reactive } from 'vue'

// Global state for Sniper (Opportunities)
export const sniperState = reactive({
    filter: 'Toutes les pertinentes',
    searchQuery: '',
    inputLocation: '',
    cvText: '',
    selectedFileName: '',
    resultLimit: 20,
    jobs: [],

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
