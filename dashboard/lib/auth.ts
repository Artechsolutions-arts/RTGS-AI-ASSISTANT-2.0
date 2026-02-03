/**
 * District-based Authentication
 * 26 districts supported
 */

export interface District {
  id: string;
  name: string;
  slug: string;
}

export const DISTRICTS: District[] = [
  { id: 'srikakulam', name: 'Srikakulam', slug: 'srikakulam' },
  { id: 'parvathipuram-manyam', name: 'Parvathipuram Manyam', slug: 'parvathipuram-manyam' },
  { id: 'vizianagaram', name: 'Vizianagaram', slug: 'vizianagaram' },
  { id: 'alluri-sitharama-raju', name: 'Alluri Sitharama Raju', slug: 'alluri-sitharama-raju' },
  { id: 'visakhapatnam', name: 'Visakhapatnam', slug: 'visakhapatnam' },
  { id: 'kakinada', name: 'Kakinada', slug: 'kakinada' },
  { id: 'east-godavari', name: 'East Godavari', slug: 'east-godavari' },
  { id: 'dr-br-ambedkar-konaseema', name: 'Dr. B.R. Ambedkar Konaseema', slug: 'dr-br-ambedkar-konaseema' },
  { id: 'eluru', name: 'Eluru', slug: 'eluru' },
  { id: 'west-godavari', name: 'West Godavari', slug: 'west-godavari' },
  { id: 'krishna', name: 'Krishna', slug: 'krishna' },
  { id: 'ntr-district', name: 'NTR District (Vijayawada)', slug: 'ntr-district' },
  { id: 'guntur', name: 'Guntur', slug: 'guntur' },
  { id: 'palnadu', name: 'Palnadu', slug: 'palnadu' },
  { id: 'bapatla', name: 'Bapatla', slug: 'bapatla' },
  { id: 'prakasam', name: 'Prakasam', slug: 'prakasam' },
  { id: 'sri-potti-sriramulu-nellore', name: 'Sri Potti Sriramulu Nellore', slug: 'sri-potti-sriramulu-nellore' },
  { id: 'kurnool', name: 'Kurnool', slug: 'kurnool' },
  { id: 'nandyal', name: 'Nandyal', slug: 'nandyal' },
  { id: 'anantapuramu', name: 'Anantapuramu', slug: 'anantapuramu' },
  { id: 'sri-sathya-sai', name: 'Sri Sathya Sai (Puttaparthi)', slug: 'sri-sathya-sai' },
  { id: 'kadapa', name: 'Kadapa (YSR Kadapa)', slug: 'kadapa' },
  { id: 'annamayya', name: 'Annamayya (Rayachoti)', slug: 'annamayya' },
  { id: 'chittoor', name: 'Chittoor', slug: 'chittoor' },
  { id: 'tirupati', name: 'Tirupati', slug: 'tirupati' },
  { id: 'sri-balaji-district', name: 'Sri Balaji District (Alipiri/Tirumala)', slug: 'sri-balaji-district' },
];

export function getDistrictBySlug(slug: string): District | undefined {
  return DISTRICTS.find(d => d.slug === slug);
}

export function getDistrictById(id: string): District | undefined {
  return DISTRICTS.find(d => d.id === id);
}

/**
 * Store district login in sessionStorage
 */
export function setDistrictLogin(district: District): void {
  if (typeof window !== 'undefined') {
    sessionStorage.setItem('districtId', district.id);
    sessionStorage.setItem('districtName', district.name);
    sessionStorage.setItem('districtSlug', district.slug);
  }
}

/**
 * Get current logged-in district
 */
export function getDistrictLogin(): District | null {
  if (typeof window === 'undefined') return null;
  
  const id = sessionStorage.getItem('districtId');
  const name = sessionStorage.getItem('districtName');
  const slug = sessionStorage.getItem('districtSlug');

  if (!id || !name || !slug) return null;

  return { id, name, slug };
}

/**
 * Clear district login
 */
export function clearDistrictLogin(): void {
  if (typeof window !== 'undefined') {
    sessionStorage.removeItem('districtId');
    sessionStorage.removeItem('districtName');
    sessionStorage.removeItem('districtSlug');
  }
}

/**
 * Check if user is logged in
 */
export function isLoggedIn(): boolean {
  return getDistrictLogin() !== null;
}
