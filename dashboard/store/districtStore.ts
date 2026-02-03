/**
 * Zustand store for district state
 */
import { create } from 'zustand';
import { District, DISTRICTS, getDistrictLogin, setDistrictLogin, clearDistrictLogin } from '@/lib/auth';

interface DistrictState {
  district: District | null;
  setDistrict: (district: District) => void;
  clearDistrict: () => void;
  initialize: () => void;
  logout: () => void;
}

export const useDistrictStore = create<DistrictState>((set) => ({
  district: null,
  
  setDistrict: (district: District) => {
    setDistrictLogin(district);
    set({ district });
  },
  
  clearDistrict: () => {
    clearDistrictLogin();
    set({ district: null });
  },
  
  initialize: () => {
    const saved = getDistrictLogin();
    if (saved) {
      set({ district: saved });
    }
  },

  logout: () => {
    clearDistrictLogin();
    set({ district: null });
  },
}));

// Export DISTRICTS for use in components
export { DISTRICTS };
