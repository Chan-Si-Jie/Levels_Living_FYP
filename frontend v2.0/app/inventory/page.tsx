import { MobileHeader } from "@/components/mobile-header"
import { MobileNav } from "@/components/mobile-nav"
import { InventoryTable } from "@/components/inventory-table"
import { Button } from "@/components/ui/button"
import { Warehouse, Plus } from "lucide-react"
import { inventoryItems } from "@/lib/inventory-data"

export default function InventoryPage() {
  return (
    <div className="min-h-screen pb-20">
      <MobileHeader title="Inventory" icon={<Warehouse className="h-6 w-6 text-primary" />} showCheck />
      <main>
        <InventoryTable items={inventoryItems} />
      </main>

      {/* Floating Action Button */}
      <Button size="icon" className="fixed bottom-24 right-6 h-14 w-14 rounded-full shadow-lg">
        <Plus className="h-6 w-6" />
      </Button>

      <MobileNav />
    </div>
  )
}
