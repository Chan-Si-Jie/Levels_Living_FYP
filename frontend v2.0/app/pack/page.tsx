import { MobileHeader } from "@/components/mobile-header"
import { MobileNav } from "@/components/mobile-nav"
import { DeliveryDateList } from "@/components/delivery-date-list"
import { Package } from "lucide-react"
import { packingDates } from "@/lib/packing-data"

export default function PackPage() {
  return (
    <div className="min-h-screen pb-20">
      <MobileHeader title="Pack" icon={<Package className="h-6 w-6 text-primary" />} />
      <main>
        <div className="border-b border-border bg-muted/30 px-4 py-3">
          <h2 className="text-sm font-semibold text-muted-foreground">Delivery Date</h2>
        </div>
        <DeliveryDateList dates={packingDates} basePath="/pack" />
      </main>
      <MobileNav />
    </div>
  )
}
