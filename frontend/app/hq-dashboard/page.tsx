"use client"

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { MobileHeader } from "@/components/mobile-header"
import { MobileNav } from "@/components/mobile-nav"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { orderService } from "@/lib/api/order-service"
import { hasError } from "@/lib/api-client"
import { toast } from "sonner"
import { Loader2, BarChart3, RotateCcw, Trash2, Package, MapPin, ArrowRight } from "lucide-react"

interface Delivery {
  order_id: string
  order_no: string
  customer_name: string
  status: string
  address: string
  scheduled_time: string
  customer_contact: string
  sequence: number
  schedule_date: string
  order_type: string
  total_items?: number
  items?: string[]
  housing_type?: string
  postal_code?: string
}

export default function HQDashboard() {
  const router = useRouter()
  const [deliveries, setDeliveries] = useState<Delivery[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedDelivery, setSelectedDelivery] = useState<Delivery | null>(null)
  const [selectedDate, setSelectedDate] = useState<string>("")
  const [availableDates, setAvailableDates] = useState<string[]>([])
  const [resetting, setResetting] = useState(false)
  const [selectedOrders, setSelectedOrders] = useState<string[]>([])
  const [unscheduling, setUnscheduling] = useState(false)

  useEffect(() => {
    fetchAllSchedules()
  }, [])

  // Handle order selection
  const handleOrderSelect = (orderId: string) => {
    setSelectedOrders(prev => {
      if (prev.includes(orderId)) {
        return prev.filter(id => id !== orderId)
      } else {
        return [...prev, orderId]
      }
    })
  }

  // Handle select all
  const handleSelectAll = () => {
    if (selectedOrders.length === deliveries.length) {
      setSelectedOrders([])
    } else {
      setSelectedOrders(deliveries.map(d => d.order_id))
    }
  }

  // Handle unschedule selected orders
  const handleUnscheduleSelected = async () => {
    if (selectedOrders.length === 0) {
      toast.error("Please select at least one order to unschedule")
      return
    }

    if (!confirm(`Are you sure you want to unschedule ${selectedOrders.length} order(s)? They will be removed from the schedule.`)) {
      return
    }

    setUnscheduling(true)

    let successCount = 0
    let errorCount = 0

    // Unschedule each selected order
    for (const orderId of selectedOrders) {
      const response = await orderService.unscheduleOrder(orderId)

      if (hasError(response)) {
        errorCount++
      } else {
        successCount++
      }
    }

    setUnscheduling(false)

    if (successCount > 0) {
      toast.success(`Successfully unscheduled ${successCount} order(s)`)
    }

    if (errorCount > 0) {
      toast.error(`Failed to unschedule ${errorCount} order(s)`)
    }

    // Clear selection and refresh
    setSelectedOrders([])

    if (selectedDate) {
      await fetchDeliveriesForDate(selectedDate)
    } else {
      await fetchAllSchedules()
    }
  }

  const handleResetDelivered = async () => {
    if (!confirm("Are you sure you want to reset all delivered orders? This will set them back to 'ready_for_delivery' status.")) {
      return
    }

    setResetting(true)

    const response = await orderService.resetDeliveredOrders()

    if (hasError(response)) {
      toast.error(response.error.error || "Failed to reset delivered orders")
      setResetting(false)
      return
    }

    if (response.data) {
      toast.success(`Successfully reset ${response.data.orders_reset} delivered orders`)
      // Refresh the current view
      if (selectedDate) {
        await fetchDeliveriesForDate(selectedDate)
      } else {
        await fetchAllSchedules()
      }
    }

    setResetting(false)
  }

  const fetchAllSchedules = async () => {
    const loadingTimeout = setTimeout(() => setLoading(true), 200)

    // Fetch all schedules
    const response = await orderService.getSchedules()
    clearTimeout(loadingTimeout)

    if (hasError(response)) {
      toast.error(response.error.error || "Failed to load schedules")
      setLoading(false)
      return
    }

    if (response.data && response.data.schedules) {
      // Extract unique dates
      const dates = [...new Set(response.data.schedules.map((s: any) => s.schedule_date))].sort()
      setAvailableDates(dates)

      // Set today's date as default if available
      const today = new Date().toISOString().split('T')[0]
      const defaultDate = dates.includes(today) ? today : dates[0]

      if (defaultDate) {
        setSelectedDate(defaultDate)
        await fetchDeliveriesForDate(defaultDate)
      }
    }

    setLoading(false)
  }

  const fetchDeliveriesForDate = async (date: string) => {
    const loadingTimeout = setTimeout(() => setLoading(true), 200)

    const response = await orderService.getScheduleByDate(date)
    clearTimeout(loadingTimeout)

    if (hasError(response)) {
      toast.error(response.error.error || "Failed to load deliveries")
      setLoading(false)
      return
    }

    if (response.data && response.data.schedules) {
      // Flatten all deliveries from all schedules
      const allDeliveries = response.data.schedules.flatMap((schedule: any) =>
        (schedule.deliveries || []).map((delivery: any) => ({
          order_id: delivery.order_id,
          order_no: delivery.order_no || delivery.platform_order_id,
          customer_name: delivery.customer_name,
          status: delivery.status,
          address: delivery.address,
          scheduled_time: delivery.estimated_arrival || "TBD",
          customer_contact: delivery.customer_contact,
          sequence: delivery.sequence,
          schedule_date: date,
          order_type: delivery.order_type || 'pre_order',
          total_items: delivery.total_items,
          items: delivery.items || [],
          housing_type: delivery.housing_type,
          postal_code: delivery.postal_code
        }))
      )
      setDeliveries(allDeliveries)
    }

    setLoading(false)
  }

  const handleDateChange = async (date: string) => {
    setSelectedDate(date)
    setSelectedDelivery(null)
    setSelectedOrders([]) // Clear selected orders when changing date
    await fetchDeliveriesForDate(date)
  }

  // Stats
  const total = deliveries.length
  const completed = deliveries.filter(d => d.status === 'delivered').length
  const pending = deliveries.filter(d => d.status === 'scheduled').length
  const onRoute = deliveries.filter(d => d.status === 'in_transit').length

  const currentDate = new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })

  if (loading && availableDates.length === 0) {
    return (
      <div className="min-h-screen bg-background pb-20">
        <MobileHeader title="HQ Dashboard" icon={<BarChart3 className="h-6 w-6 text-primary" />} />
        <div className="flex items-center justify-center p-8">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
        <MobileNav />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background pb-20">
      <MobileHeader title="HQ Dashboard" icon={<BarChart3 className="h-6 w-6 text-primary" />} />

      <div className="p-4 space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold">HQ Manager</h1>
            <div className="text-sm text-muted-foreground">{currentDate}</div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleResetDelivered}
            disabled={resetting || completed === 0}
            className="flex items-center gap-2"
          >
            {resetting ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <RotateCcw className="h-4 w-4" />
            )}
            Reset Delivered
          </Button>
        </div>

        {/* Date Selector */}
        {availableDates.length > 0 && (
          <div className="bg-card border border-border rounded-lg p-4">
            <label className="text-sm font-medium mb-2 block">Select Date</label>
            <select
              value={selectedDate}
              onChange={(e) => handleDateChange(e.target.value)}
              className="w-full px-3 py-2 border border-border rounded-lg bg-background"
            >
              {availableDates.map((date) => (
                <option key={date} value={date}>
                  {new Date(date).toLocaleDateString('en-US', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-card border border-border rounded-lg p-4 text-center">
            <h2 className="text-3xl font-bold text-primary">{total}</h2>
            <p className="text-sm text-muted-foreground">Total Deliveries</p>
          </div>
          <div className="bg-card border border-border rounded-lg p-4 text-center">
            <h2 className="text-3xl font-bold text-green-600">{completed}</h2>
            <p className="text-sm text-muted-foreground">Completed</p>
          </div>
          <div className="bg-card border border-border rounded-lg p-4 text-center">
            <h2 className="text-3xl font-bold text-orange-500">{pending}</h2>
            <p className="text-sm text-muted-foreground">Pending</p>
          </div>
          <div className="bg-card border border-border rounded-lg p-4 text-center">
            <h2 className="text-3xl font-bold text-blue-600">{onRoute}</h2>
            <p className="text-sm text-muted-foreground">On Route</p>
          </div>
        </div>

        {/* Delivery List */}
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">Delivery List</h2>
            {deliveries.length > 0 && (
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleSelectAll}
                >
                  {selectedOrders.length === deliveries.length ? "Deselect All" : "Select All"}
                </Button>
                {selectedOrders.length > 0 && (
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={handleUnscheduleSelected}
                    disabled={unscheduling}
                    className="flex items-center gap-2"
                  >
                    {unscheduling ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Trash2 className="h-4 w-4" />
                    )}
                    Unschedule ({selectedOrders.length})
                  </Button>
                )}
              </div>
            )}
          </div>

          {loading ? (
            <div className="flex items-center justify-center p-8">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : deliveries.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">No deliveries scheduled for this date</p>
          ) : (
            <div className="space-y-2">
              {deliveries.map((delivery) => {
                const isSelected = selectedOrders.includes(delivery.order_id)
                return (
                <div
                  key={delivery.order_id}
                  className={`border border-border rounded-lg p-4 transition-colors ${
                    isSelected ? 'border-primary border-2 bg-primary/5' : ''
                  } ${selectedDelivery?.order_id === delivery.order_id ? 'bg-accent' : ''}`}
                >
                  <div className="flex items-start gap-3">
                    {/* Checkbox */}
                    <div className="pt-1" onClick={(e) => e.stopPropagation()}>
                      <Checkbox
                        checked={isSelected}
                        onCheckedChange={() => handleOrderSelect(delivery.order_id)}
                        className="border-2"
                      />
                    </div>

                    {/* Delivery Info */}
                    <div
                      className="flex-1 cursor-pointer"
                      onClick={() => setSelectedDelivery(delivery)}
                    >
                      <div className="space-y-2 mb-2">
                        <div className="flex justify-between items-center">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-semibold text-black">{delivery.order_no}</span>
                            {delivery.housing_type && (
                              <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-700">
                                {delivery.housing_type}
                              </span>
                            )}
                          </div>
                          <div className="flex gap-2">
                            <span className={`text-xs px-2 py-1 rounded-full ${
                              delivery.order_type === 'asap' ? 'bg-red-100 text-red-800' :
                              delivery.order_type === 'adhoc' ? 'bg-orange-100 text-orange-800' :
                              delivery.order_type === 'pre_order' ? 'bg-blue-100 text-blue-800' :
                              'bg-purple-100 text-purple-800'
                            }`}>
                              {delivery.order_type.toUpperCase().replace('_', ' ')}
                            </span>
                            <span className={`text-xs px-2 py-1 rounded-full ${
                              delivery.status === 'delivered' ? 'bg-green-100 text-green-800' :
                              delivery.status === 'scheduled' ? 'bg-orange-100 text-orange-800' :
                              'bg-blue-100 text-blue-800'
                            }`}>
                              {delivery.status.toUpperCase()}
                            </span>
                          </div>
                        </div>
                        <p className="text-sm font-medium text-black whitespace-nowrap">{delivery.customer_name}</p>
                      </div>

                      <div className="space-y-2 text-sm mt-2">
                        <div className="flex items-start gap-2">
                          <MapPin className="h-4 w-4 text-black mt-0.5 flex-shrink-0" />
                          <div>
                            <p className="text-black">{delivery.address}</p>
                            {delivery.postal_code && (
                              <p className="text-black text-xs">Singapore {delivery.postal_code}</p>
                            )}
                          </div>
                        </div>

                        {delivery.total_items && (
                          <div className="flex items-start gap-2">
                            <Package className="h-4 w-4 text-black mt-0.5 flex-shrink-0" />
                            <div className="text-xs w-full">
                              <p className="font-medium text-black">{delivery.total_items} items</p>
                              {delivery.items && delivery.items.length > 0 && (
                                <div className="mt-1 space-y-0.5 pl-2 border-l-2 border-gray-300">
                                  {delivery.items.map((item: string, idx: number) => (
                                    <div key={idx} className="text-xs text-black">
                                      {item}
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>
                          </div>
                        )}

                        <p className="text-xs text-black">Seq: {delivery.sequence} • {delivery.scheduled_time}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )})}
            </div>
          )}
        </div>

        {/* Selected Delivery Details */}
        {selectedDelivery && (
          <div className="bg-card border-2 border-primary rounded-lg p-4">
            <h3 className="text-lg font-bold mb-3">Delivery Details</h3>
            <div className="space-y-2 text-sm mb-4">
              <p><strong>Order ID:</strong> {selectedDelivery.order_no}</p>
              <p><strong>Customer:</strong> {selectedDelivery.customer_name}</p>
              <p><strong>Phone:</strong> {selectedDelivery.customer_contact}</p>
              <p><strong>Status:</strong> <span className="capitalize">{selectedDelivery.status}</span></p>
              <p><strong>Address:</strong> {selectedDelivery.address}</p>
              <p><strong>Scheduled Time:</strong> {selectedDelivery.scheduled_time}</p>
              <p><strong>Sequence:</strong> #{selectedDelivery.sequence}</p>
            </div>
            <div className="space-y-2">
              <button
                onClick={() => router.push(`/delivery/${selectedDate}/${selectedDelivery.order_id}`)}
                className="w-full bg-blue-600 text-white hover:bg-blue-700 font-semibold py-3 px-4 rounded-lg flex items-center justify-center gap-2"
              >
                View Delivery Details
                <ArrowRight className="h-4 w-4" />
              </button>
              <button
                onClick={() => setSelectedDelivery(null)}
                className="w-full px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90"
              >
                Close
              </button>
            </div>
          </div>
        )}
      </div>

      <MobileNav />
    </div>
  )
}
