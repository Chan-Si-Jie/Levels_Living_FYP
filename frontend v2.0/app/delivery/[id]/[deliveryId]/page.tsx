import { notFound } from "next/navigation"
import { MobileHeader } from "@/components/mobile-header"
import { SignaturePad } from "@/components/signature-pad"
import { getDeliveryById } from "@/lib/delivery-data"
import { cn } from "@/lib/utils"
import { MobileNav } from "@/components/mobile-nav"

export default function DeliveryDetailsPage({
  params,
}: {
  params: { id: string; deliveryId: string }
}) {
  // Example: const delivery = await fetch(`/api/deliveries/${params.deliveryId}`).then(r => r.json())
  const delivery = getDeliveryById(params.deliveryId)

  if (!delivery) {
    notFound()
  }

  return (
    <div className="min-h-screen bg-background pb-20">
      <MobileHeader title="Details" showBack />

      <div className="p-4 space-y-6">
        {/* All SKUs */}
        <div>
          <p className="text-sm text-muted-foreground mb-1">All SKUs</p>
          <p className="text-lg">{delivery.skus}</p>
        </div>

        {/* All Items */}
        <div>
          <p className="text-sm text-muted-foreground mb-1">All Items</p>
          <p className="text-lg leading-relaxed">{delivery.items}</p>
        </div>

        {/* All Variants */}
        <div>
          <p className="text-sm text-muted-foreground mb-1">All Variants</p>
          <p className="text-lg">{delivery.variants}</p>
        </div>

        {/* All Quantities */}
        <div>
          <p className="text-sm text-muted-foreground mb-1">All Quantities</p>
          <p className="text-lg">{delivery.quantities}</p>
        </div>

        {/* Customer Name */}
        <div>
          <p className="text-sm text-muted-foreground mb-1">Customer Name</p>
          <p className="text-lg font-semibold">{delivery.customerName}</p>
        </div>

        {/* Customer Contact */}
        <div>
          <p className="text-sm text-muted-foreground mb-1">Customer Contact</p>
          <p className="text-lg">{delivery.phone}</p>
        </div>

        {/* Customer Street */}
        <div>
          <p className="text-sm text-muted-foreground mb-1">Customer Street</p>
          <p className="text-lg">{delivery.street}</p>
        </div>

        {/* Customer Unit */}
        <div>
          <p className="text-sm text-muted-foreground mb-1">Customer Unit</p>
          <p className="text-lg">{delivery.unit}</p>
        </div>

        {/* Customer Postal Code */}
        <div>
          <p className="text-sm text-muted-foreground mb-1">Customer Postal Code</p>
          <p className="text-lg font-semibold">{delivery.postalCode}</p>
        </div>

        {/* Note */}
        <div>
          <p className="text-sm text-muted-foreground mb-1">Note</p>
          <p className="text-base leading-relaxed">{delivery.note}</p>
        </div>

        {/* Signature */}
        <div>
          <p className="text-sm text-muted-foreground mb-2">Signature</p>
          <SignaturePad />
        </div>

        {/* Delivery Status */}
        <div>
          <p className="text-sm text-muted-foreground mb-1">Delivered?</p>
          <p
            className={cn(
              "text-lg font-semibold",
              delivery.status === "delivered" && "text-green-600",
              delivery.status === "pending" && "text-orange-500",
              delivery.status === "cancelled" && "text-red-600",
            )}
          >
            {delivery.status.toUpperCase()}
          </p>
        </div>
      </div>

      <MobileNav />
    </div>
  )
}
