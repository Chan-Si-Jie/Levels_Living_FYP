"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Locate } from "lucide-react"
import type { DeliveryLocation } from "@/lib/map-data"

interface DeliveryMapProps {
  locations: DeliveryLocation[]
}

export function DeliveryMap({ locations }: DeliveryMapProps) {
  const [mapType, setMapType] = useState<"map" | "satellite">("map")

  return (
    <div className="relative h-[calc(100vh-3.5rem-5rem)]">
      {/* Map Type Toggle */}
      <div className="absolute left-4 top-4 z-10 flex rounded-lg bg-background shadow-md overflow-hidden border border-border">
        <button
          onClick={() => setMapType("map")}
          className={`px-6 py-2 text-sm font-medium transition-colors ${
            mapType === "map" ? "bg-background text-foreground" : "bg-muted text-muted-foreground"
          }`}
        >
          Map
        </button>
        <button
          onClick={() => setMapType("satellite")}
          className={`px-6 py-2 text-sm font-medium transition-colors ${
            mapType === "satellite" ? "bg-background text-foreground" : "bg-muted text-muted-foreground"
          }`}
        >
          Satellite
        </button>
      </div>

      {/* Map Container */}
      <div className="h-full w-full bg-muted">
        <iframe
          src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d255281.19036!2d103.704!3d1.3521!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x31da11238a8b9375%3A0x887869cf52abf5c4!2sSingapore!5e0!3m2!1sen!2s!4v1234567890"
          width="100%"
          height="100%"
          style={{ border: 0 }}
          allowFullScreen
          loading="lazy"
          referrerPolicy="no-referrer-when-downgrade"
          title="Delivery locations map"
        />
      </div>

      {/* Recenter Button */}
      <Button size="icon" variant="secondary" className="absolute bottom-6 left-6 h-12 w-12 rounded-lg shadow-lg">
        <Locate className="h-5 w-5" />
      </Button>

      {/* User Location Button */}
      <Button size="icon" variant="secondary" className="absolute bottom-24 left-6 h-12 w-12 rounded-lg shadow-lg">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="h-6 w-6"
        >
          <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z" />
          <circle cx="12" cy="10" r="3" />
        </svg>
      </Button>
    </div>
  )
}
