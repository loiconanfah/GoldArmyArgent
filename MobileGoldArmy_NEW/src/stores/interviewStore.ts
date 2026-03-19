import { create } from 'zustand';

interface InterviewConfig {
  company: string;
  jobTitle: string;
  jobDetails: string;
  cvText: string;
  recruiterId: 'tech' | 'hr' | 'ceo';
  interviewType: 'general' | 'tech';
}

interface InterviewStore {
  config: InterviewConfig | null;
  setConfig: (config: InterviewConfig) => void;
  clearConfig: () => void;
}

export const useInterviewStore = create<InterviewStore>((set) => ({
  config: null,
  setConfig: (config) => set({ config }),
  clearConfig: () => set({ config: null }),
}));
