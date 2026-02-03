/**
 * Zustand store for voice assistant state
 */
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

interface VoiceState {
  enabled: boolean;
  listening: boolean;
  language: 'en' | 'te';
  toggle: () => void;
  setListening: (listening: boolean) => void;
  setLanguage: (lang: 'en' | 'te') => void;
}

const getStorage = () => {
  if (typeof window === 'undefined') {
    return {
      getItem: () => null,
      setItem: () => {},
      removeItem: () => {},
    };
  }
  return localStorage;
};

export const useVoiceStore = create<VoiceState>()(
  persist(
    (set) => ({
      enabled: false,
      listening: false,
      language: 'en',
      
      toggle: () => set((state) => ({ enabled: !state.enabled })),
      
      setListening: (listening: boolean) => set({ listening }),
      
      setLanguage: (lang: 'en' | 'te') => set({ language: lang }),
    }),
    {
      name: 'voice-assistant-storage',
      storage: createJSONStorage(() => getStorage()),
    }
  )
);
