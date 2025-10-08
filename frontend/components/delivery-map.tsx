"use client";

import { useEffect, useRef, useState } from "react";

interface DeliveryMapProps {
  locations?: { lat: number; lng: number; address: string; customer: string; sequence: number }[];
  routePolyline?: string | null;
}

export const DeliveryMap: React.FC<DeliveryMapProps> = ({ locations = [], routePolyline = null }) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const [map, setMap] = useState<google.maps.Map | null>(null);
  const [scriptLoaded, setScriptLoaded] = useState(false);

  const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;

  // Hardcoded start location (warehouse)
  const warehouseLocation = {
    lat: 1.375645, // Replace with the actual latitude of 18 Tampines Industrial Crescent
    lng: 103.929573, // Replace with the actual longitude of 18 Tampines Industrial Crescent
    address: "18 Tampines Industrial Crescent",
  };

  // Dynamically load the Google Maps script
  useEffect(() => {
    const loadGoogleMapsScript = () => {
      if (document.getElementById("google-maps-script")) {
        setScriptLoaded(true);
        return;
      }

      const script = document.createElement("script");
      script.id = "google-maps-script";
      script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=geometry`;
      script.async = true;
      script.defer = true;
      script.onload = () => setScriptLoaded(true);
      document.body.appendChild(script);
    };

    loadGoogleMapsScript();
  }, []);

  // Initialize the map
  useEffect(() => {
    if (!scriptLoaded || !mapRef.current) return;

    const initializeMap = () => {
      const mapInstance = new google.maps.Map(mapRef.current!, {
        center: { lat: 1.29, lng: 103.85 }, // Default center: Singapore
        zoom: 12,
        mapTypeControl: false,
        streetViewControl: false,
      });

      setMap(mapInstance);
    };

    if (typeof google !== "undefined") {
      initializeMap();
    }
  }, [scriptLoaded]);

  // Add markers and polyline
  useEffect(() => {
    if (!map) return;

    const bounds = new google.maps.LatLngBounds();

    // Add warehouse marker
    const warehouseMarker = new google.maps.Marker({
      position: { lat: warehouseLocation.lat, lng: warehouseLocation.lng },
      map,
      label: "Start", // Label the marker as "Start"
      title: warehouseLocation.address,
      icon: {
        url: "http://maps.google.com/mapfiles/ms/icons/green-dot.png", // Green marker for the warehouse
      },
    });

    const warehouseInfoWindow = new google.maps.InfoWindow({
      content: `<div><strong>Warehouse</strong><br>${warehouseLocation.address}</div>`,
    });

    warehouseMarker.addListener("click", () => {
      warehouseInfoWindow.open(map, warehouseMarker);
    });

    bounds.extend(warehouseMarker.getPosition()!);

    // Add markers for each location
    locations.forEach((location) => {
      const marker = new google.maps.Marker({
        position: { lat: location.lat, lng: location.lng },
        map,
        label: location.sequence.toString(), // Display sequence number as marker label
        title: `${location.customer} - ${location.address}`,
      });

      const infoWindow = new google.maps.InfoWindow({
        content: `<div><strong>${location.customer}</strong><br>${location.address}</div>`,
      });

      marker.addListener("click", () => {
        infoWindow.open(map, marker);
      });

      // Extend map bounds to include this location
      bounds.extend(marker.getPosition()!);
    });

    // Fit the map to the bounds of all markers
    map.fitBounds(bounds);

    // Draw the polyline if available
    if (routePolyline) {
      const decodedPath = google.maps.geometry.encoding.decodePath(routePolyline); // Decode the polyline
      const polyline = new google.maps.Polyline({
        path: decodedPath,
        geodesic: true,
        strokeColor: "#FF0000",
        strokeOpacity: 1.0,
        strokeWeight: 2,
      });

      polyline.setMap(map);
    }
  }, [map, locations, routePolyline]);

  return (
    <div style={{ width: "100%", height: "100vh" }}>
      {!scriptLoaded && <p>Loading Google Maps...</p>}
      <div ref={mapRef} style={{ width: "100%", height: "100%" }} />
    </div>
  );
};