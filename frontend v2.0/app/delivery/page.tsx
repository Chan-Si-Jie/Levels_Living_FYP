import { MobileHeader } from "@/components/mobile-header"
import { MobileNav } from "@/components/mobile-nav"
import { DeliveryDateList } from "@/components/delivery-date-list"
import { Truck } from "lucide-react"
import { deliveryDates } from "@/lib/delivery-data"

export default function DeliveryPage() {
  return (
    <div className="min-h-screen pb-20">
      <MobileHeader title="Delivery" icon={<Truck className="h-6 w-6 text-primary" />} />
      <main>
        <DeliveryDateList dates={deliveryDates} basePath="/delivery" />
      </main>
      <MobileNav />
    </div>
  )
}
