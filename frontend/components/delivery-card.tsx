"use client"

import { MessageCircle, Phone, MapPin } from "lucide-react"
import { cn } from "@/lib/utils"
import type { Delivery } from "@/lib/delivery-data"
import Link from "next/link"

interface DeliveryCardProps {
  delivery: Delivery
  basePath: string
}

export function DeliveryCard({ delivery, basePath }: DeliveryCardProps) {
  const handleGoogleMaps = () => {
    const encodedAddress = encodeURIComponent(delivery.address)
    window.open(`https://www.google.com/maps/search/?api=1&query=${encodedAddress}`, "_blank")
  }

  const handleWaze = () => {
    const encodedAddress = encodeURIComponent(delivery.address)
    window.open(`https://waze.com/ul?q=${encodedAddress}`, "_blank")
  }

  const handleWhatsApp = () => {
    const message = encodeURIComponent(`Hi ${delivery.customerName}, this is regarding your order ${delivery.orderId}`)
    window.open(`https://wa.me/${delivery.phone.replace(/\+/g, "")}?text=${message}`, "_blank")
  }

  const handleCall = () => {
    window.location.href = `tel:${delivery.phone}`
  }

  return (
    <Link href={`${basePath}/${delivery.id}`} className="block">
      <div className="rounded-lg border border-border bg-card p-4 shadow-sm hover:shadow-md transition-shadow">
        {/* Order details */}
        <h3 className="text-base font-semibold leading-tight mb-2">
          {delivery.orderId} : {delivery.orderDetails}
        </h3>

        {/* Time slot */}
        <p className="text-sm text-muted-foreground mb-4">{delivery.timeSlot}</p>

        {/* Customer name */}
        <p className="text-lg font-semibold mb-1">{delivery.customerName}</p>

        {/* Address with pin icon */}
        <div className="flex items-start gap-2 mb-4">
          <p className="text-sm text-muted-foreground flex-1">{delivery.address}</p>
          <MapPin className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
        </div>

        {/* Status */}
        <p
          className={cn(
            "text-sm font-semibold mb-4",
            delivery.status === "delivered" && "text-green-600",
            delivery.status === "pending" && "text-orange-500",
            delivery.status === "cancelled" && "text-red-600",
          )}
        >
          {delivery.status.toUpperCase()}
        </p>

        {/* Action buttons */}
        <div className="flex items-center gap-4" onClick={(e) => e.preventDefault()}>
          <button onClick={handleGoogleMaps} className="text-sm font-medium text-primary hover:underline">
            NAV (GMAPS)
          </button>
          <button onClick={handleWaze} className="text-sm font-medium text-primary hover:underline">
            NAV (WAZE)
          </button>
          <div className="flex-1" />
          <button
            onClick={handleWhatsApp}
            className="flex h-10 w-10 items-center justify-center rounded-full hover:bg-muted transition-colors"
            aria-label="Send WhatsApp message"
          >
            <MessageCircle className="h-5 w-5" />
          </button>
          <button
            onClick={handleCall}
            className="flex h-10 w-10 items-center justify-center rounded-full hover:bg-muted transition-colors"
            aria-label="Call customer"
          >
            <Phone className="h-5 w-5" />
          </button>
        </div>
      </div>
    </Link>
  )
}
