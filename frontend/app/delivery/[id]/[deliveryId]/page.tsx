"use client"

import { useEffect, useState } from "react"
import { notFound } from "next/navigation"
import { MobileHeader } from "@/components/mobile-header"
import { SignaturePad } from "@/components/signature-pad"
import { cn } from "@/lib/utils"
import { MobileNav } from "@/components/mobile-nav"
import { orderService } from "@/lib/api/order-service"
import { hasError } from "@/lib/api-client"
import { toast } from "sonner"
import { Loader2 } from "lucide-react"
import { authStorage } from "@/lib/auth-storage"

export default function DeliveryDetailsPage({
  params,
}: {
  params: { id: string; deliveryId: string }
}) {
  const [delivery, setDelivery] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [notFoundState, setNotFoundState] = useState(false)
  const [userRole, setUserRole] = useState<string>("")

  useEffect(() => {
    // Get user role
    const user = authStorage.getUserData()
    if (user?.role) {
      setUserRole(user.role)
    }

    fetchDeliveryDetails()
  }, [])

  const fetchDeliveryDetails = async () => {
    const loadingTimeout = setTimeout(() => setLoading(true), 200)

    // Fetch order details by order_id
    const response = await orderService.getOrderById(params.deliveryId)
    clearTimeout(loadingTimeout)

    if (hasError(response)) {
      toast.error(response.error.error || "Failed to load delivery details")
      setNotFoundState(true)
      setLoading(false)
      return
    }

    if (response.data && response.data.order) {
      setDelivery(response.data)
    } else {
      setNotFoundState(true)
    }
    setLoading(false)
  }

  const handleMarkAsComplete = async () => {
    if (!confirm("Mark this delivery as complete?")) {
      return
    }

    setLoading(true)

    const response = await orderService.completeDelivery(params.deliveryId)

    if (hasError(response)) {
      toast.error(response.error.error || "Failed to mark delivery as complete")
      setLoading(false)
      return
    }

    toast.success("Delivery marked as complete!")

    // Refresh the delivery details to show updated status
    await fetchDeliveryDetails()
  }

  const handleUnschedule = async () => {
    if (!confirm("Are you sure you want to unschedule this order? It will be removed from the schedule.")) {
      return
    }

    setLoading(true)

    const response = await orderService.unscheduleOrder(params.deliveryId)

    if (hasError(response)) {
      toast.error(response.error.error || "Failed to unschedule order")
      setLoading(false)
      return
    }

    toast.success("Order unscheduled successfully!")

    // Navigate back to the delivery list
    window.history.back()
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background pb-20">
        <MobileHeader title="Details" showBack />
        <div className="flex items-center justify-center p-8">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
        <MobileNav />
      </div>
    )
  }

  if (notFoundState || !delivery) {
    notFound()
  }

  return (
    <div className="min-h-screen bg-background pb-20">
      <MobileHeader title="Details" showBack />

      <div className="p-4 space-y-6">
        {/* All SKUs */}
        <div>
          <p className="text-sm text-muted-foreground mb-1">All SKUs</p>
          <p className="text-lg">
            {delivery.items?.map((item: any) => item.sku).join(", ") || "N/A"}
          </p>
        </div>

        {/* All Items */}
        <div>
          <p className="text-sm text-muted-foreground mb-1">All Items</p>
          <p className="text-lg leading-relaxed">
            {delivery.items?.map((item: any) => item.item_name).join(", ") || "N/A"}
          </p>
        </div>

        {/* All Variants */}
        <div>
          <p className="text-sm text-muted-foreground mb-1">All Variants</p>
          <p className="text-lg">
            {delivery.items?.map((item: any) => item.variant || "Standard").join(", ") || "N/A"}
          </p>
        </div>

        {/* All Quantities */}
        <div>
          <p className="text-sm text-muted-foreground mb-1">All Quantities</p>
          <p className="text-lg">
            {delivery.items?.map((item: any) => item.quantity).join(", ") || "N/A"}
          </p>
        </div>

        {/* Customer Name */}
        <div>
          <p className="text-sm text-muted-foreground mb-1">Customer Name</p>
          <p className="text-lg font-semibold">{delivery.order.customer_name || "N/A"}</p>
        </div>

        {/* Customer Contact */}
        <div>
          <p className="text-sm text-muted-foreground mb-1">Customer Contact</p>
          <p className="text-lg">{delivery.order.customer_contact || "N/A"}</p>
        </div>

        {/* Customer Street */}
        <div>
          <p className="text-sm text-muted-foreground mb-1">Customer Street</p>
          <p className="text-lg">{delivery.order.customer_street || "N/A"}</p>
        </div>

        {/* Customer Unit */}
        <div>
          <p className="text-sm text-muted-foreground mb-1">Customer Unit</p>
          <p className="text-lg">{delivery.order.customer_unit || "N/A"}</p>
        </div>

        {/* Customer Postal Code */}
        <div>
          <p className="text-sm text-muted-foreground mb-1">Customer Postal Code</p>
          <p className="text-lg font-semibold">{delivery.order.customer_postal_code || "N/A"}</p>
        </div>

        {/* Note */}
        <div>
          <p className="text-sm text-muted-foreground mb-1">Note</p>
          <p className="text-base leading-relaxed">
            Please sign below to confirm inspection and receipt of the items in the above packing list, and that they are in good condition. Hereafter, the recipient is responsible for the item and the condition it is in. Any new issue highlighted will be reviewed on a case-to-case basis and any decision made will be at the discretion of the company.
          </p>
        </div>

        {/* Signature */}
        <div>
          <p className="text-sm text-muted-foreground mb-2">Signature</p>
          <SignaturePad />
        </div>

        {/* Action Buttons */}
        <div className="pt-4 space-y-3">
          <button
            onClick={handleMarkAsComplete}
            disabled={loading}
            className="w-full bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed font-semibold py-3 px-4 rounded-lg transition-colors"
          >
            {loading ? "Updating..." : "Mark Delivery as Complete"}
          </button>

          {/* Only show Unschedule button for admin and hq roles */}
          {(userRole === "admin" || userRole === "hq") && (
            <button
              onClick={handleUnschedule}
              disabled={loading}
              className="w-full bg-yellow-500 text-white hover:bg-yellow-600 disabled:opacity-50 disabled:cursor-not-allowed font-semibold py-3 px-4 rounded-lg transition-colors"
            >
              {loading ? "Updating..." : "Unschedule Order"}
            </button>
          )}
        </div>

        {/* Delivery Status */}
        <div>
          <p className="text-sm text-muted-foreground mb-1">Delivered?</p>
          <p
            className={cn(
              "text-lg font-semibold",
              delivery.order?.status === "delivered" && "text-green-600",
              (delivery.order?.status === "pending" || delivery.order?.status === "scheduled") && "text-orange-500",
              delivery.order?.status === "cancelled" && "text-red-600",
            )}
          >
            {delivery.order?.status?.toUpperCase() || "N/A"}
          </p>
        </div>
      </div>

      <MobileNav />
    </div>
  )
}
