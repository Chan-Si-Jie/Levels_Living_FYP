"use client"

import { useEffect, useState } from "react"
import { MobileHeader } from "@/components/mobile-header"
import { MobileNav } from "@/components/mobile-nav"
import { Loader2, MapPin, MessageCircle, Phone } from "lucide-react"
import { orderService } from "@/lib/api/order-service"
import { hasError } from "@/lib/api-client"
import { toast } from "sonner"
import Link from "next/link"
import { cn } from "@/lib/utils"

interface DeliveryDetailProps {
  params: { id: string }
}

export default function DeliveryDetailPage({ params }: DeliveryDetailProps) {
  const [deliveries, setDeliveries] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const dateStr = params.id // This is the date like "2025-10-03"

  useEffect(() => {
    fetchSchedulesByDate()
  }, [])

  const fetchSchedulesByDate = async () => {
    const loadingTimeout = setTimeout(() => setLoading(true), 200)
    const response = await orderService.getScheduleByDate(dateStr)
    clearTimeout(loadingTimeout)

    if (hasError(response)) {
      toast.error(response.error.error || "Failed to load schedules")
      setLoading(false)
      return
    }

    if (response.data && response.data.schedules) {
      // Flatten all deliveries from all schedules into a single list
      const allDeliveries = response.data.schedules.flatMap((schedule: any) =>
        (schedule.deliveries || []).map((delivery: any) => ({
          ...delivery,
          schedule_id: schedule.schedule_id,
          driver_name: schedule.driver_name,
          team: schedule.team
        }))
      )
      setDeliveries(allDeliveries)
    }
    setLoading(false)
  }

  const handleGoogleMaps = (address: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    const encodedAddress = encodeURIComponent(address)
    window.open(`https://www.google.com/maps/search/?api=1&query=${encodedAddress}`, "_blank")
  }

  const handleWaze = (address: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    const encodedAddress = encodeURIComponent(address)
    window.open(`https://waze.com/ul?q=${encodedAddress}`, "_blank")
  }

  const handleWhatsApp = (phone: string, customerName: string, orderNo: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    const message = encodeURIComponent(`Hi ${customerName}, this is regarding your order ${orderNo}`)
    window.open(`https://wa.me/${phone.replace(/[^0-9]/g, "")}?text=${message}`, "_blank")
  }

  const handleCall = (phone: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    window.location.href = `tel:${phone}`
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    const options: Intl.DateTimeFormatOptions = {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    }
    return date.toLocaleDateString('en-US', options)
  }

  return (
    <div className="min-h-screen bg-background pb-20">
      <MobileHeader title="Delivery" showBack />

      <div className="p-4 space-y-4">
        {/* Date Header */}
        {!loading && deliveries.length > 0 && (
          <div className="bg-primary/10 rounded-lg p-4 mb-2">
            <h2 className="text-lg font-semibold text-primary">{formatDate(dateStr)}</h2>
            <p className="text-sm text-muted-foreground mt-1">
              {deliveries.length} {deliveries.length === 1 ? 'delivery' : 'deliveries'}
            </p>
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center p-8">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : deliveries.length === 0 ? (
          <p className="text-center text-muted-foreground py-8">No deliveries for this date</p>
        ) : (
          deliveries.map((delivery, index) => (
            <Link
              key={index}
              href={`/delivery/${dateStr}/${delivery.order_id || index}`}
              className="block"
            >
              <div className="rounded-lg border border-border bg-card p-4 shadow-sm hover:shadow-md transition-shadow">
                {/* Order details with items */}
                <h3 className="text-base font-semibold leading-tight mb-2">
                  {delivery.platform_order_id || delivery.order_no}
                  {delivery.items && delivery.items.length > 0 && (
                    <span className="text-base font-semibold leading-tight mb-2">
                      {" : "}{delivery.items.join(", ")}
                    </span>
                  )}
                </h3>

                {/* Time slot */}
                {delivery.estimated_arrival && (
                  <p className="text-sm text-muted-foreground mb-4">
                    ETA: {delivery.estimated_arrival}
                  </p>
                )}

                {/* Customer name */}
                <p className="text-lg font-semibold mb-1">{delivery.customer_name}</p>

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
                    delivery.status === "scheduled" && "text-blue-600",
                    delivery.status === "in_transit" && "text-orange-500",
                    delivery.status === "failed" && "text-red-600"
                  )}
                >
                  {delivery.status.toUpperCase()}
                </p>

                {/* Action buttons */}
                <div className="flex items-center gap-4" onClick={(e) => e.preventDefault()}>
                  <button
                    onClick={(e) => handleGoogleMaps(delivery.address, e)}
                    className="text-sm font-medium text-primary hover:underline"
                  >
                    NAV (GMAPS)
                  </button>
                  <button
                    onClick={(e) => handleWaze(delivery.address, e)}
                    className="text-sm font-medium text-primary hover:underline"
                  >
                    NAV (WAZE)
                  </button>
                  <div className="flex-1" />
                  <button
                    onClick={(e) =>
                      handleWhatsApp(
                        delivery.customer_contact,
                        delivery.customer_name,
                        delivery.order_no,
                        e
                      )
                    }
                    className="flex h-10 w-10 items-center justify-center rounded-full hover:bg-muted transition-colors"
                    aria-label="Send WhatsApp message"
                  >
                    <MessageCircle className="h-5 w-5" />
                  </button>
                  <button
                    onClick={(e) => handleCall(delivery.customer_contact, e)}
                    className="flex h-10 w-10 items-center justify-center rounded-full hover:bg-muted transition-colors"
                    aria-label="Call customer"
                  >
                    <Phone className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </Link>
          ))
        )}
      </div>

      <MobileNav />
    </div>
  )
}
