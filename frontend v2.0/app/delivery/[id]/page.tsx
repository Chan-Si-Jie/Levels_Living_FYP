import { notFound } from "next/navigation"
import { MobileHeader } from "@/components/mobile-header"
import { DeliveryCard } from "@/components/delivery-card"
import { deliveryDates, getDeliveriesForDate } from "@/lib/delivery-data"
import { MobileNav } from "@/components/mobile-nav"

export default function DeliveryDetailPage({ params }: { params: { id: string } }) {
  // DATABASE INTEGRATION: Replace with API calls
  // Example: const dateInfo = await fetch(`/api/delivery-dates/${params.id}`).then(r => r.json())
  // Example: const deliveries = await fetch(`/api/deliveries?dateId=${params.id}`).then(r => r.json())
  const dateInfo = deliveryDates.find((d) => d.id === params.id)

  if (!dateInfo) {
    notFound()
  }

  const deliveries = getDeliveriesForDate(params.id)

  return (
    <div className="min-h-screen bg-background pb-20">
      <MobileHeader title="Delivery" showBack />

      <div className="p-4 space-y-4">
        {deliveries.length === 0 ? (
          <p className="text-center text-muted-foreground py-8">No deliveries for this date</p>
        ) : (
          deliveries.map((delivery) => (
            <DeliveryCard key={delivery.id} delivery={delivery} basePath={`/delivery/${params.id}`} />
          ))
        )}
      </div>

      <MobileNav />
    </div>
  )
}
