declare namespace google {
  namespace maps {
    class Map {
      constructor(element: HTMLElement, options?: any);
      data: {
        addGeoJson(geoJson: any): void;
        setStyle(style: any): void;
        forEach(callback: (feature: any) => void): void;
      };
      fitBounds(bounds: LatLngBounds): void;
    }

    class LatLngBounds {
      extend(latLng: LatLng): void;
    }

    class LatLng {
      constructor(lat: number, lng: number);
    }
  }
}
