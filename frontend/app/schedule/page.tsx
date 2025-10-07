"use client"

import { useState, useMemo, useEffect } from "react"
import { useRouter } from "next/navigation"
import { MobileHeader } from "@/components/mobile-header"
import { MobileNav } from "@/components/mobile-nav"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Calendar, MapPin, Phone, Package, ChevronUp, ChevronDown, GripVertical, Loader2, ShieldAlert } from "lucide-react"
import { orderService, type UnscheduledOrder } from "@/lib/api/order-service"
import { hasError } from "@/lib/api-client"
import { toast } from "sonner"
import { authStorage } from "@/lib/auth-storage"

export default function SchedulePage() {
  const router = useRouter()
  const [postalCode, setPostalCode] = useState("")
  const [address, setAddress] = useState("")
  const [orderedDeliveries, setOrderedDeliveries] = useState<UnscheduledOrder[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedOrders, setSelectedOrders] = useState<string[]>([])
  const [hasAccess, setHasAccess] = useState<boolean>(false)
  const [expandedOrders, setExpandedOrders] = useState<string[]>([])
  const [savingPreferences, setSavingPreferences] = useState<string[]>([])

  // Track temporary changes before saving
  const [tempPreferences, setTempPreferences] = useState<Record<string, {
    remarks?: string
    preferred_delivery_date?: string
    preferred_delivery_time?: string
  }>>({})

  // Schedule creation form
  const [scheduleDate, setScheduleDate] = useState("")
  const [driverId, setDriverId] = useState("")
  const [team, setTeam] = useState("")
  const [creating, setCreating] = useState(false)

  // Check if user has admin access
  useEffect(() => {
    const user = authStorage.getUserData()
    if (!user) {
      toast.error("Please login to access this page")
      router.push("/login")
      return
    }

    // Only allow admin or hq roles to access schedule page
    if (user.role !== "admin" && user.role !== "hq") {
      toast.error("Access denied. Only admin users can create schedules.")
      router.push("/dashboard")
      return
    }

    setHasAccess(true)
  }, [router])

  // Fetch unscheduled orders from backend
  useEffect(() => {
    if (hasAccess) {
      fetchUnscheduledOrders()
    }
  }, [hasAccess])

  const fetchUnscheduledOrders = async () => {
    const loadingTimeout = setTimeout(() => setLoading(true), 200)
    const response = await orderService.getUnscheduledOrders()
    clearTimeout(loadingTimeout)

    if (hasError(response)) {
      toast.error(response.error.error || "Failed to load unscheduled orders")
      setLoading(false)
      return
    }

    if (response.data) {
      setOrderedDeliveries(response.data.orders)
    }
    setLoading(false)
  }

  // Filter deliveries based on postal code and address
  const filteredDeliveries = useMemo(() => {
    return orderedDeliveries.filter((delivery) => {
      const matchesPostalCode = postalCode ? delivery.customer_postal_code.toLowerCase().includes(postalCode.toLowerCase()) : true
      const matchesAddress = address
        ? delivery.customer_street.toLowerCase().includes(address.toLowerCase())
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

  // Handle order selection
  const handleOrderSelect = (orderId: string) => {
    setSelectedOrders(prev => {
      if (prev.includes(orderId)) {
        return prev.filter(id => id !== orderId)
      } else {
        // Check 18 location limit
        if (prev.length >= 18) {
          toast.error("Maximum 18 locations per day (3rd party delivery agreement)")
          return prev
        }
        return [...prev, orderId]
      }
    })
  }

  // Handle select all
  const handleSelectAll = () => {
    if (selectedOrders.length === orderedDeliveries.length) {
      setSelectedOrders([])
    } else {
      const allOrderIds = orderedDeliveries.slice(0, 18).map(o => o.order_id)
      setSelectedOrders(allOrderIds)
      if (orderedDeliveries.length > 18) {
        toast.warning("Selected first 18 orders (maximum limit)")
      }
    }
  }

  // Handle order type change
  const handleOrderTypeChange = async (orderId: string, newOrderType: 'pre_order' | 'asap' | 'adhoc' | 'custom_date') => {
    const response = await orderService.updateOrderType(orderId, newOrderType)

    if (hasError(response)) {
      toast.error(response.error.error || "Failed to update order type")
      return
    }

    toast.success(`Order type updated to ${newOrderType.replace('_', ' ').toUpperCase()}`)

    // Update local state
    setOrderedDeliveries(prev =>
      prev.map(order =>
        order.order_id === orderId
          ? { ...order, order_type: newOrderType }
          : order
      )
    )
  }

  // Toggle expanded state for an order
  const toggleExpanded = (orderId: string) => {
    setExpandedOrders(prev =>
      prev.includes(orderId)
        ? prev.filter(id => id !== orderId)
        : [...prev, orderId]
    )
  }

  // Update temporary preferences (not saved yet)
  const handlePreferenceChange = (
    orderId: string,
    field: 'remarks' | 'preferred_delivery_date' | 'preferred_delivery_time',
    value: string
  ) => {
    setTempPreferences(prev => ({
      ...prev,
      [orderId]: {
        ...prev[orderId],
        [field]: value
      }
    }))
  }

  // Save delivery preferences
  const handleSavePreferences = async (orderId: string) => {
    const data = tempPreferences[orderId]

    if (!data || Object.keys(data).length === 0) {
      toast.info("No changes to save")
      return
    }

    setSavingPreferences(prev => [...prev, orderId])

    console.log('Saving preferences:', orderId, data)

    const response = await orderService.updateDeliveryPreferences(orderId, data)

    setSavingPreferences(prev => prev.filter(id => id !== orderId))

    if (hasError(response)) {
      console.error('Failed to save:', response.error)
      toast.error(response.error.error || "Failed to update preferences")
      return
    }

    console.log('Saved successfully:', response)
    toast.success("Delivery preferences saved")

    // Update local state
    setOrderedDeliveries(prev =>
      prev.map(order =>
        order.order_id === orderId
          ? { ...order, ...data }
          : order
      )
    )

    // Clear temp preferences for this order
    setTempPreferences(prev => {
      const { [orderId]: _, ...rest } = prev
      return rest
    })
  }

  // Handle schedule creation
  const handleCreateSchedule = async () => {
    if (selectedOrders.length === 0) {
      toast.error("Please select at least one order")
      return
    }

    if (!scheduleDate) {
      toast.error("Please select a schedule date")
      return
    }

    setCreating(true)

    const response = await orderService.createSchedule({
      order_ids: selectedOrders,
      schedule_date: scheduleDate,
      driver_id: driverId || undefined,
      team: team || undefined
    })

    if (hasError(response)) {
      toast.error(response.error.error || "Failed to create schedule")
      setCreating(false)
      return
    }

    if (response.data) {
      toast.success(`Schedule created! ${response.data.total_locations} locations scheduled.`)

      // Reset form
      setSelectedOrders([])
      setScheduleDate("")
      setDriverId("")
      setTeam("")

      // Refresh orders list
      setTimeout(() => {
        fetchUnscheduledOrders()
      }, 1000)
    }

    setCreating(false)
  }

  // Get today's date for min date
  const today = new Date().toISOString().split('T')[0]

  // Show loading while checking access
  if (!hasAccess) {
    return (
      <div className="min-h-screen pb-20 bg-muted/30">
        <MobileHeader title="Schedule" icon={<Calendar className="h-6 w-6 text-primary" />} />
        <div className="flex items-center justify-center p-8">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
        <MobileNav />
      </div>
    )
  }

  return (
    <div className="min-h-screen pb-20 bg-muted/30">
      <MobileHeader title="Schedule" icon={<Calendar className="h-6 w-6 text-primary" />} />

      <main className="p-4 space-y-4">
        {/* Schedule Creation Form */}
        <Card className="p-4 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold">Create Schedule</h3>
            <span className="text-sm text-muted-foreground">
              {selectedOrders.length} / 18 selected
            </span>
          </div>

          <div className="grid grid-cols-1 gap-3">
            <div className="space-y-2">
              <Label htmlFor="schedule-date">Schedule Date *</Label>
              <Input
                id="schedule-date"
                type="date"
                value={scheduleDate}
                onChange={(e) => setScheduleDate(e.target.value)}
                min={today}
                className="h-10"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label htmlFor="driver-id">Driver ID (Optional)</Label>
                <Input
                  id="driver-id"
                  placeholder="e.g., DRV001"
                  value={driverId}
                  onChange={(e) => setDriverId(e.target.value)}
                  className="h-10"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="team">Team (Optional)</Label>
                <Input
                  id="team"
                  placeholder="e.g., Team A"
                  value={team}
                  onChange={(e) => setTeam(e.target.value)}
                  className="h-10"
                />
              </div>
            </div>
          </div>

          <div className="flex gap-2">
            <Button
              onClick={handleCreateSchedule}
              disabled={selectedOrders.length === 0 || !scheduleDate || creating}
              className="flex-1"
            >
              {creating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Create Schedule ({selectedOrders.length})
            </Button>
            <Button
              variant="outline"
              onClick={handleSelectAll}
              disabled={orderedDeliveries.length === 0}
            >
              {selectedOrders.length === orderedDeliveries.length ? "Deselect All" : "Select All"}
            </Button>
          </div>

          <div className="text-xs text-muted-foreground bg-yellow-50 p-2 rounded">
            ℹ Orders sorted by priority (ASAP → Adhoc → Pre-order) then by postal code
          </div>
        </Card>

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
          <h2 className="text-lg font-semibold px-1">Unscheduled Orders</h2>

          {loading ? (
            <Card className="p-8 text-center">
              <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
              <p className="text-muted-foreground mt-2">Loading orders...</p>
            </Card>
          ) : filteredDeliveries.length === 0 ? (
            <Card className="p-8 text-center">
              <p className="text-muted-foreground">No unscheduled orders found</p>
            </Card>
          ) : (
            <div className="space-y-2">
              {filteredDeliveries.map((delivery, index) => {
                // Find the actual index in the ordered array for proper reordering
                const actualIndex = orderedDeliveries.findIndex((d) => d.order_id === delivery.order_id)
                const isSelected = selectedOrders.includes(delivery.order_id)

                return (
                  <Card
                    key={delivery.order_id}
                    className={`p-4 space-y-3 ${isSelected ? 'border-primary' : ''}`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="flex items-center pt-1">
                        <Checkbox
                          checked={isSelected}
                          onCheckedChange={() => handleOrderSelect(delivery.order_id)}
                          className={`transition-colors ${isSelected ? "border-blue-500" : "border-blue-500"} border-2 rounded`}
                        />
                      </div>

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
                        <div className="flex items-start justify-between gap-2">
                          <div className="space-y-1 flex-1">
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className="text-sm font-semibold">{delivery.order_no}</span>

                              {/* Order Type Selector */}
                              <Select
                                value={delivery.order_type}
                                onValueChange={(value: 'pre_order' | 'asap' | 'adhoc' | 'custom_date') =>
                                  handleOrderTypeChange(delivery.order_id, value)
                                }
                              >
                                <SelectTrigger
                                  className={`w-[110px] h-6 text-xs px-2 py-0 border-0 ${
                                    delivery.order_type === "asap"
                                      ? "bg-red-100 text-red-700"
                                      : delivery.order_type === "adhoc"
                                        ? "bg-orange-100 text-orange-700"
                                        : delivery.order_type === "custom_date"
                                          ? "bg-purple-100 text-purple-700"
                                          : "bg-blue-100 text-blue-700"
                                  }`}
                                >
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="asap" className="text-xs">
                                    <span className="font-semibold text-red-700">ASAP</span>
                                  </SelectItem>
                                  <SelectItem value="adhoc" className="text-xs">
                                    <span className="font-semibold text-orange-700">ADHOC</span>
                                  </SelectItem>
                                  <SelectItem value="pre_order" className="text-xs">
                                    <span className="font-semibold text-blue-700">PRE ORDER</span>
                                  </SelectItem>
                                  <SelectItem value="custom_date" className="text-xs">
                                    <span className="font-semibold text-purple-700">CUSTOM DATE</span>
                                  </SelectItem>
                                </SelectContent>
                              </Select>

                              <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-700">
                                {delivery.housing_type}
                              </span>
                            </div>
                            <p className="text-sm font-medium">{delivery.customer_name}</p>
                          </div>
                        </div>

                        <div className="space-y-2 text-sm">
                          <div className="flex items-start gap-2">
                            <MapPin className="h-4 w-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                            <div>
                              <p className="text-foreground">{delivery.customer_street}</p>
                              <p className="text-muted-foreground">
                                {delivery.customer_unit}, Singapore {delivery.customer_postal_code}
                              </p>
                            </div>
                          </div>

                          <div className="flex items-start gap-2">
                            <Package className="h-4 w-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                            <div className="text-xs">
                              <p className="font-medium">{delivery.total_items} items</p>
                              {Number(delivery.total_value || delivery.order_value || 0) > 0 && (
                                <p className="text-muted-foreground">
                                  Value: ${Number(delivery.total_value || delivery.order_value).toFixed(2)}
                                </p>
                              )}
                            </div>
                          </div>

                          {(delivery.preferred_delivery_date || delivery.preferred_delivery_time) && (
                            <div className="flex items-center gap-2">
                              <Calendar className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                              <p className="text-muted-foreground text-xs">
                                Preferred: {delivery.preferred_delivery_date && new Date(delivery.preferred_delivery_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}{delivery.preferred_delivery_date && delivery.preferred_delivery_time && ', '}{delivery.preferred_delivery_time}
                              </p>
                            </div>
                          )}

                          {delivery.remarks && (
                            <div className="flex items-start gap-2">
                              <Package className="h-4 w-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                              <p className="text-muted-foreground text-xs">
                                <span className="font-medium">Remarks:</span> {delivery.remarks}
                              </p>
                            </div>
                          )}
                        </div>

                        {/* Expandable Preferences Section */}
                        <div className="pt-3 border-t">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="w-full text-xs"
                            onClick={() => toggleExpanded(delivery.order_id)}
                          >
                            {expandedOrders.includes(delivery.order_id) ? "Hide" : "Add"} Delivery Preferences
                            <ChevronDown className={`ml-2 h-3 w-3 transition-transform ${expandedOrders.includes(delivery.order_id) ? 'rotate-180' : ''}`} />
                          </Button>

                          {expandedOrders.includes(delivery.order_id) && (
                            <div className="mt-3 space-y-3 bg-muted/30 p-3 rounded-lg">
                              <div className="space-y-1">
                                <Label htmlFor={`remarks-${delivery.order_id}`} className="text-xs">
                                  Remarks
                                </Label>
                                <Input
                                  id={`remarks-${delivery.order_id}`}
                                  placeholder="Add remarks for this order..."
                                  defaultValue={tempPreferences[delivery.order_id]?.remarks ?? delivery.remarks ?? ""}
                                  onChange={(e) => handlePreferenceChange(delivery.order_id, 'remarks', e.target.value)}
                                  className="h-8 text-xs"
                                />
                              </div>

                              <div className="grid grid-cols-2 gap-2">
                                <div className="space-y-1">
                                  <Label htmlFor={`pref-date-${delivery.order_id}`} className="text-xs">
                                    Preferred Date
                                  </Label>
                                  <Input
                                    id={`pref-date-${delivery.order_id}`}
                                    type="date"
                                    defaultValue={tempPreferences[delivery.order_id]?.preferred_delivery_date ?? delivery.preferred_delivery_date ?? ""}
                                    onChange={(e) => handlePreferenceChange(delivery.order_id, 'preferred_delivery_date', e.target.value)}
                                    className="h-8 text-xs"
                                  />
                                </div>

                                <div className="space-y-1">
                                  <Label htmlFor={`pref-time-${delivery.order_id}`} className="text-xs">
                                    Preferred Time
                                  </Label>
                                  <Input
                                    id={`pref-time-${delivery.order_id}`}
                                    type="time"
                                    defaultValue={tempPreferences[delivery.order_id]?.preferred_delivery_time ?? delivery.preferred_delivery_time ?? ""}
                                    onChange={(e) => handlePreferenceChange(delivery.order_id, 'preferred_delivery_time', e.target.value)}
                                    className="h-8 text-xs"
                                  />
                                </div>
                              </div>

                              <Button
                                size="sm"
                                onClick={() => handleSavePreferences(delivery.order_id)}
                                disabled={savingPreferences.includes(delivery.order_id)}
                                className="w-full h-8 text-xs"
                              >
                                {savingPreferences.includes(delivery.order_id) ? (
                                  <>
                                    <Loader2 className="mr-2 h-3 w-3 animate-spin" />
                                    Saving...
                                  </>
                                ) : (
                                  "Save Preferences"
                                )}
                              </Button>
                            </div>
                          )}
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
