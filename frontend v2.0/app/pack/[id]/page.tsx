"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { MobileHeader } from "@/components/mobile-header"
import { packingDates, getPackingItemsForDate } from "@/lib/packing-data"
import { MobileNav } from "@/components/mobile-nav"
import { Search, Edit, Check, RefreshCw, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"

export default function PackDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const [isEditMode, setIsEditMode] = useState(false)
  const [isSelectionMode, setIsSelectionMode] = useState(false)
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set())
  const [showDeliveredDialog, setShowDeliveredDialog] = useState(false)

  // DATABASE INTEGRATION: Replace with API calls and state management
  // Example: const [items, setItems] = useState([])
  // Example: useEffect(() => { fetch(`/api/packing-items?dateId=${params.id}`).then(r => r.json()).then(setItems) }, [])
  const dateInfo = packingDates.find((d) => d.id === params.id)
  const [items, setItems] = useState(getPackingItemsForDate(params.id))

  if (!dateInfo) {
    return null
  }

  const handleEditClick = () => {
    setIsEditMode(!isEditMode)
    setIsSelectionMode(false)
    setSelectedItems(new Set())
  }

  const handleCheckClick = () => {
    setIsSelectionMode(!isSelectionMode)
    setIsEditMode(false)
    setSelectedItems(new Set())
  }

  const handleCancelSelection = () => {
    setIsSelectionMode(false)
    setSelectedItems(new Set())
  }

  const handleItemSelect = (itemId: string) => {
    const newSelected = new Set(selectedItems)
    if (newSelected.has(itemId)) {
      newSelected.delete(itemId)
    } else {
      newSelected.add(itemId)
    }
    setSelectedItems(newSelected)

    // Show dialog when items are selected
    if (newSelected.size > 0) {
      setShowDeliveredDialog(true)
    } else {
      setShowDeliveredDialog(false)
    }
  }

  const handleFieldChange = (itemId: string, field: string, value: string) => {
    // DATABASE INTEGRATION: Update via API
    // Example: await fetch(`/api/packing-items/${itemId}`, { method: 'PATCH', body: JSON.stringify({ [field]: value }) })
    setItems(items.map((item) => (item.id === itemId ? { ...item, [field]: value } : item)))
  }

  const handleMarkDelivered = () => {
    // DATABASE INTEGRATION: Mark items as delivered via API
    // Example: await fetch('/api/packing-items/mark-delivered', { method: 'POST', body: JSON.stringify({ ids: Array.from(selectedItems) }) })
    console.log("[v0] Marking items as delivered:", Array.from(selectedItems))
    setShowDeliveredDialog(false)
    setIsSelectionMode(false)
    setSelectedItems(new Set())
  }

  return (
    <div className="min-h-screen bg-background pb-20">
      <MobileHeader title="Pack" showBack={!isSelectionMode}>
        {isSelectionMode ? (
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={handleCancelSelection}>
              <X className="h-5 w-5" />
            </Button>
            <span className="text-sm font-medium">{selectedItems.size} Selected</span>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon">
              <Search className="h-5 w-5" />
            </Button>
            <Button variant="ghost" size="icon" onClick={handleEditClick}>
              <Edit className={`h-5 w-5 ${isEditMode ? "text-primary" : ""}`} />
            </Button>
            <Button variant="ghost" size="icon" onClick={handleCheckClick}>
              <Check className="h-5 w-5" />
            </Button>
            <Button variant="ghost" size="icon">
              <RefreshCw className="h-5 w-5" />
            </Button>
          </div>
        )}
      </MobileHeader>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead className="bg-muted/50 sticky top-0">
            <tr className="border-b">
              {isSelectionMode && <th className="w-12"></th>}
              <th className="text-left p-4 font-semibold text-sm min-w-[180px]">SKU</th>
              <th className="text-left p-4 font-semibold text-sm min-w-[100px]">Quantity</th>
              <th className="text-left p-4 font-semibold text-sm min-w-[120px]">Variant</th>
              <th className="text-left p-4 font-semibold text-sm min-w-[120px]">Order No</th>
              <th className="text-left p-4 font-semibold text-sm min-w-[80px]">Ass...</th>
              <th className="text-left p-4 font-semibold text-sm min-w-[200px]">Item</th>
            </tr>
          </thead>
          <tbody>
            {items.length === 0 ? (
              <tr>
                <td colSpan={isSelectionMode ? 7 : 6} className="text-center py-8 text-muted-foreground">
                  No items to pack for this date
                </td>
              </tr>
            ) : (
              items.map((item) => (
                <tr key={item.id} className={`border-b ${item.isHighlighted ? "bg-cyan-50" : ""}`}>
                  {isSelectionMode && (
                    <td className="p-4">
                      <Checkbox
                        checked={selectedItems.has(item.id)}
                        onCheckedChange={() => handleItemSelect(item.id)}
                        className="data-[state=checked]:bg-orange-500 data-[state=checked]:border-orange-500"
                      />
                    </td>
                  )}
                  <td className={`p-4 text-sm ${item.isHighlighted ? "text-cyan-500 font-medium" : ""}`}>
                    {isEditMode ? (
                      <Input
                        value={item.sku}
                        onChange={(e) => handleFieldChange(item.id, "sku", e.target.value)}
                        className="h-8 text-sm"
                      />
                    ) : (
                      item.sku
                    )}
                  </td>
                  <td className="p-4 text-sm">
                    {isEditMode ? (
                      <Input
                        type="number"
                        value={item.quantity}
                        onChange={(e) => handleFieldChange(item.id, "quantity", e.target.value)}
                        className="h-8 w-20 text-sm"
                      />
                    ) : (
                      item.quantity
                    )}
                  </td>
                  <td className="p-4 text-sm">
                    {isEditMode ? (
                      <Input
                        value={item.variant}
                        onChange={(e) => handleFieldChange(item.id, "variant", e.target.value)}
                        className="h-8 text-sm"
                      />
                    ) : (
                      item.variant
                    )}
                  </td>
                  <td className="p-4 text-sm">
                    {isEditMode ? (
                      <Input
                        value={item.orderNo}
                        onChange={(e) => handleFieldChange(item.id, "orderNo", e.target.value)}
                        className="h-8 text-sm"
                      />
                    ) : (
                      item.orderNo
                    )}
                  </td>
                  <td className="p-4 text-sm">
                    {isEditMode ? (
                      <Input
                        value={item.assembly}
                        onChange={(e) => handleFieldChange(item.id, "assembly", e.target.value)}
                        className="h-8 w-16 text-sm"
                      />
                    ) : (
                      item.assembly
                    )}
                  </td>
                  <td className="p-4 text-sm">
                    {isEditMode ? (
                      <Input
                        value={item.itemName}
                        onChange={(e) => handleFieldChange(item.id, "itemName", e.target.value)}
                        className="h-8 text-sm"
                      />
                    ) : (
                      <div className="flex items-center gap-2">
                        {item.itemColor && (
                          <div className={`w-2 h-2 rounded-full ${item.itemColor === "green" ? "bg-green-500" : ""}`} />
                        )}
                        <span className={item.isHighlighted ? "text-cyan-500 font-medium" : ""}>{item.itemName}</span>
                      </div>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <Dialog open={showDeliveredDialog} onOpenChange={setShowDeliveredDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Check className="h-5 w-5" />
              Order Delivered?
            </DialogTitle>
            <DialogDescription>
              Mark {selectedItems.size} selected {selectedItems.size === 1 ? "item" : "items"} as delivered?
            </DialogDescription>
          </DialogHeader>
          <div className="flex gap-2 justify-end">
            <Button variant="outline" onClick={() => setShowDeliveredDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleMarkDelivered}>Confirm</Button>
          </div>
        </DialogContent>
      </Dialog>

      <MobileNav />
    </div>
  )
}
