"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft, Rocket } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { NumberInput } from "@/components/number-input"
import { inventoryItems } from "@/lib/inventory-data"
import Link from "next/link"
import { MobileNav } from "@/components/mobile-nav"

export default function InventoryFormPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const item = inventoryItems.find((i) => i.id === params.id)

  const [formData, setFormData] = useState({
    type: item?.type || "",
    name: item?.name || "",
    quantity: item?.quantity || 0,
    required: item?.required || 0,
  })

  if (!item) {
    return <div>Item not found</div>
  }

  const handleSave = async () => {
    // Example: await fetch('/api/inventory', { method: 'PUT', body: JSON.stringify(formData) })
    console.log("Saving:", formData)
    router.push("/inventory")
  }

  const handleCancel = () => {
    router.push("/inventory")
  }

  return (
    <div className="min-h-screen bg-background flex flex-col pb-20">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-border bg-background">
        <div className="flex items-center gap-3 px-4 py-4">
          <Link href="/inventory">
            <Button variant="ghost" size="icon" className="h-10 w-10">
              <ArrowLeft className="h-6 w-6" />
            </Button>
          </Link>
          <Rocket className="h-6 w-6 text-primary" />
          <h1 className="text-xl font-semibold">Inventory Form</h1>
        </div>
      </header>

      {/* Form Content */}
      <main className="flex-1 px-4 py-6 space-y-6">
        <div className="space-y-2">
          <Label htmlFor="type" className="text-base">
            Type
          </Label>
          <Input
            id="type"
            value={formData.type}
            onChange={(e) => setFormData({ ...formData, type: e.target.value })}
            className="h-14 text-lg"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="name" className="text-base">
            Item<span className="text-amber-500">*</span>
          </Label>
          <Input
            id="name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="h-14 text-lg"
            required
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="quantity" className="text-base">
            Quantity<span className="text-amber-500">*</span>
          </Label>
          <NumberInput value={formData.quantity} onChange={(value) => setFormData({ ...formData, quantity: value })} />
        </div>

        <div className="space-y-2">
          <Label htmlFor="required" className="text-base">
            Required<span className="text-amber-500">*</span>
          </Label>
          <NumberInput value={formData.required} onChange={(value) => setFormData({ ...formData, required: value })} />
        </div>
      </main>

      {/* Bottom Actions */}
      <div className="sticky bottom-16 border-t border-border bg-background px-4 py-4 flex gap-4">
        <Button variant="ghost" onClick={handleCancel} className="flex-1 h-12 text-base">
          Cancel
        </Button>
        <Button onClick={handleSave} className="flex-1 h-12 text-base bg-amber-500 hover:bg-amber-600 text-white">
          Save
        </Button>
      </div>

      <MobileNav />
    </div>
  )
}
