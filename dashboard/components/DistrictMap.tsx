'use client';

import React, { useEffect, useRef, useState } from 'react';

// Extend Window interface for Google Maps
declare global {
  interface Window {
    google: any;
  }
}

interface DistrictMapProps {
  districtName: string;
}

export function DistrictMap({ districtName }: DistrictMapProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const [apiKeyMissing, setApiKeyMissing] = useState(false);
  const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;

  useEffect(() => {
    if (!apiKey || apiKey.trim() === '') {
      setApiKeyMissing(true);
      return;
    }

    if (!mapRef.current) return;

    // Load Google Maps script
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places,geometry`;
    script.async = true;
    script.defer = true;
    
    script.onload = () => {
      initMap();
    };

    script.onerror = () => {
      setApiKeyMissing(true);
    };

    document.head.appendChild(script);

    return () => {
      if (script.parentNode) {
        script.parentNode.removeChild(script);
      }
    };
  }, [districtName, apiKey]);

  const initMap = () => {
    if (!mapRef.current || !window.google) return;

    // District coordinates (approximate centers)
    const districtCoordinates: { [key: string]: { lat: number; lng: number } } = {
      'ntr-district': { lat: 16.5062, lng: 80.6480 }, // Vijayawada
      'srikakulam': { lat: 18.2949, lng: 83.8938 },
      'visakhapatnam': { lat: 17.6868, lng: 83.2185 },
      'east-godavari': { lat: 17.0005, lng: 81.8040 },
      'west-godavari': { lat: 16.7107, lng: 81.1809 },
      'krishna': { lat: 16.1760, lng: 80.8574 },
      'guntur': { lat: 16.3067, lng: 80.4365 },
      'prakasam': { lat: 15.3647, lng: 79.5893 },
      'kurnool': { lat: 15.8281, lng: 78.0373 },
      'anantapuramu': { lat: 14.6819, lng: 77.6006 },
      'chittoor': { lat: 13.2172, lng: 79.1003 },
      'kadapa': { lat: 14.4674, lng: 78.8241 },
      'tirupati': { lat: 13.6288, lng: 79.4192 }
    };

    const coord = districtCoordinates[districtName.toLowerCase()] || districtCoordinates['ntr-district'];
    const center = Array.isArray(coord) ? { lat: coord[0], lng: coord[1] } : coord;

    const map = new window.google.maps.Map(mapRef.current, {
      center: center,
      zoom: 10,
      mapTypeId: 'roadmap',
      styles: [
        {
          featureType: 'administrative.locality',
          elementType: 'labels',
          stylers: [{ visibility: 'on' }]
        },
        {
          featureType: 'administrative.province',
          elementType: 'geometry.stroke',
          stylers: [
            { color: '#003366' },
            { weight: 2 },
            { visibility: 'on' }
          ]
        },
        {
          featureType: 'water',
          elementType: 'geometry',
          stylers: [{ color: '#e9e9e9' }, { lightness: 17 }]
        },
        {
          featureType: 'landscape',
          elementType: 'geometry',
          stylers: [{ color: '#f5f5f5' }, { lightness: 20 }]
        }
      ],
      mapTypeControl: true,
      mapTypeControlOptions: {
        position: window.google.maps.ControlPosition.TOP_RIGHT, // Move away from the title bar
      },
      streetViewControl: false,
      fullscreenControl: true,
      fullscreenControlOptions: {
        position: window.google.maps.ControlPosition.RIGHT_TOP,
      },
      zoomControl: true,
      zoomControlOptions: {
        position: window.google.maps.ControlPosition.RIGHT_CENTER,
      }
    });

    // Add a marker for the district center
    new (window.google.maps as any).Marker({
      position: center,
      map: map,
      title: districtName.toUpperCase(),
      icon: {
        path: (window.google.maps as any).SymbolPath.CIRCLE,
        scale: 10,
        fillColor: '#003366',
        fillOpacity: 1,
        strokeColor: '#ffffff',
        strokeWeight: 2
      }
    });

    // Load District Boundary via Data Layer (GeoJSON)
    // This is more reliable than KML for exact boundaries
    map.data.loadGeoJson(`/maps/${districtName.toLowerCase()}.json`, undefined, (features: any[]) => {
      if (features && features.length > 0) {
        console.log(`[DistrictMap] Loaded boundary for ${districtName}`);
        
        // Style the boundary
        map.data.setStyle({
          fillColor: '#3b82f6',
          fillOpacity: 0.1,
          strokeColor: '#ef4444', // Red boundary as seen in your reference
          strokeWeight: 2,
          strokeOpacity: 0.8,
          clickable: false
        });

        // Fit map to boundary if needed
        const bounds = new window.google.maps.LatLngBounds();
        map.data.forEach((feature: any) => {
          const geometry = feature.getGeometry();
          if (geometry) {
            geometry.forEachLatLng((latlng: any) => {
              bounds.extend(latlng);
            });
          }
        });
        map.fitBounds(bounds);
      }
    });
  };

  return (
    <div className="relative w-full h-full bg-slate-100 flex items-center justify-center overflow-hidden">
      {apiKeyMissing ? (
        <div className="text-center p-8 max-w-md space-y-4 animate-fade-in">
          <div className="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-6">
            <span className="text-4xl">🔑</span>
          </div>
          <h3 className="text-lg font-black text-slate-800 uppercase tracking-tight">API Configuration Required</h3>
          <p className="text-sm text-slate-500 font-medium leading-relaxed">
            Please add your Google Maps API Key to <code className="bg-slate-200 px-1.5 py-0.5 rounded text-blue-700">.env.local</code> to enable the official government geospatial layer.
          </p>
          <div className="pt-4">
             <div className="bg-white border border-slate-200 p-4 rounded-xl text-left text-[11px] font-mono text-slate-600">
               NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=AIza...
             </div>
          </div>
        </div>
      ) : (
        <div ref={mapRef} className="w-full h-full" />
      )}
    </div>
  );
}
