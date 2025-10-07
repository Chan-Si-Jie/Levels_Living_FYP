import { MobileHeader } from "@/components/mobile-header"
import { MobileNav } from "@/components/mobile-nav"
import { DeliveryMap } from "@/components/delivery-map"
import { MapPin } from "lucide-react"
import { deliveryLocations } from "@/lib/map-data"

export default function OverviewPage() {
  return (
    <div className="min-h-screen pb-20">
      <MobileHeader
        title="Overview"
        icon={<MapPin className="h-6 w-6 text-primary" />}
        showSearch={false}
        showRefresh={false}
      />
      <main>
        <DeliveryMap locations={deliveryLocations} />
      </main>
      <MobileNav />
    </div>
  )
}
