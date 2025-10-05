"use client"

import { useState, useMemo } from "react"
import { MobileHeader } from "@/components/mobile-header"
import { MobileNav } from "@/components/mobile-nav"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Calendar, MapPin, Phone, Package, ChevronUp, ChevronDown, GripVertical } from "lucide-react"
import { deliveries, type Delivery } from "@/lib/delivery-data"

export default function SchedulePage() {
  const [postalCode, setPostalCode] = useState("")
  const [address, setAddress] = useState("")

  const [orderedDeliveries, setOrderedDeliveries] = useState<Delivery[]>(deliveries)

  // Filter deliveries based on postal code and address
  const filteredDeliveries = useMemo(() => {
    return orderedDeliveries.filter((delivery) => {
      const matchesPostalCode = postalCode ? delivery.postalCode.toLowerCase().includes(postalCode.toLowerCase()) : true
      const matchesAddress = address
        ? delivery.address.toLowerCase().includes(address.toLowerCase()) ||
          delivery.street.toLowerCase().includes(address.toLowerCase())
        : true
      return matchesPostalCode && matchesAddress
    })
  }, [orderedDeliveries, postalCode, address])

  const moveDelivery = (index: number, direction: "up" | "down") => {
    const newOrder = [...orderedDeliveries]
    const targetIndex = direction === "up" ? index - 1 : index + 1

    if (targetIndex < 0 || targetIndex >= newOrder.length) return // Swap the deliveries
    ;[newOrder[index], newOrder[targetIndex]] = [newOrder[targetIndex], newOrder[index]]
    setOrderedDeliveries(newOrder)
  }

  return (
    <div className="min-h-screen pb-20 bg-muted/30">
      <MobileHeader title="Schedule" icon={<Calendar className="h-6 w-6 text-primary" />} />

      <main className="p-4 space-y-4">
        {/* Filter Section */}
        <Card className="p-4 space-y-4">
          <div className="space-y-2">
            <Label htmlFor="postal-code" className="text-sm font-medium">
              Postal Code
            </Label>
            <Input
              id="postal-code"
              placeholder="Enter postal code..."
              value={postalCode}
              onChange={(e) => setPostalCode(e.target.value)}
              className="h-10"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="address" className="text-sm font-medium">
              Address
            </Label>
            <Input
              id="address"
              placeholder="Enter street or address..."
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              className="h-10"
            />
          </div>

          <div className="flex items-center justify-between pt-2 border-t">
            <span className="text-sm text-muted-foreground">Total Deliveries</span>
            <span className="text-lg font-semibold text-primary">{filteredDeliveries.length}</span>
          </div>
        </Card>

        <div className="space-y-4">
          <h2 className="text-lg font-semibold px-1">Today's Deliveries</h2>

          {filteredDeliveries.length === 0 ? (
            <Card className="p-8 text-center">
              <p className="text-muted-foreground">No deliveries found</p>
            </Card>
          ) : (
            <div className="space-y-2">
              {filteredDeliveries.map((delivery, index) => {
                // Find the actual index in the ordered array for proper reordering
                const actualIndex = orderedDeliveries.findIndex((d) => d.id === delivery.id)

                return (
                  <Card key={delivery.id} className="p-4 space-y-3">
                    <div className="flex items-start gap-3">
                      <div className="flex flex-col items-center gap-1 pt-1">
                        <GripVertical className="h-5 w-5 text-muted-foreground" />
                        <div className="flex flex-col gap-0.5">
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6"
                            onClick={() => moveDelivery(actualIndex, "up")}
                            disabled={actualIndex === 0}
                          >
                            <ChevronUp className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6"
                            onClick={() => moveDelivery(actualIndex, "down")}
                            disabled={actualIndex === orderedDeliveries.length - 1}
                          >
                            <ChevronDown className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>

                      <div className="flex-1 space-y-3">
                        <div className="flex items-start justify-between">
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-semibold">Order #{delivery.orderId}</span>
                              <span
                                className={`text-xs px-2 py-0.5 rounded-full ${
                                  delivery.status === "delivered"
                                    ? "bg-green-100 text-green-700"
                                    : delivery.status === "cancelled"
                                      ? "bg-red-100 text-red-700"
                                      : "bg-yellow-100 text-yellow-700"
                                }`}
                              >
                                {delivery.status}
                              </span>
                            </div>
                            <p className="text-sm font-medium">{delivery.customerName}</p>
                          </div>
                        </div>

                        <div className="space-y-2 text-sm">
                          <div className="flex items-start gap-2">
                            <MapPin className="h-4 w-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                            <div>
                              <p className="text-foreground">{delivery.street}</p>
                              <p className="text-muted-foreground">
                                {delivery.unit}, Singapore {delivery.postalCode}
                              </p>
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            <Phone className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                            <p className="text-muted-foreground">{delivery.phone}</p>
                          </div>

                          <div className="flex items-start gap-2">
                            <Package className="h-4 w-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                            <p className="text-muted-foreground text-xs leading-relaxed">{delivery.orderDetails}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </Card>
                )
              })}
            </div>
          )}
        </div>
      </main>

      <MobileNav />
    </div>
  )
}
