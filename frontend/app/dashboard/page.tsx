"use client"

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { MobileHeader } from "@/components/mobile-header"
import { MobileNav } from "@/components/mobile-nav"
import { orderService } from "@/lib/api/order-service"
import { hasError } from "@/lib/api-client"
import { toast } from "sonner"
import { Loader2, BarChart3, MapPin, Package, ArrowRight } from "lucide-react"
import { authStorage } from "@/lib/auth-storage"

interface Delivery {
  order_id: string
  order_no: string
  customer_name: string
  status: string
  address: string
  scheduled_time: string
  customer_contact: string
  sequence: number
  order_type: string
  total_items?: number
  items?: string[]
  housing_type?: string
  postal_code?: string
}

export default function DriverDashboard() {
  const router = useRouter()
  const [deliveries, setDeliveries] = useState<Delivery[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedDelivery, setSelectedDelivery] = useState<Delivery | null>(null)
  const [userName, setUserName] = useState("Driver")

  useEffect(() => {
    fetchTodaysDeliveries()
    loadUserInfo()
  }, [])

  const loadUserInfo = () => {
    const user = authStorage.getUserData()
    if (user?.email) {
      setUserName(user.email.split('@')[0])
    }
  }

  const fetchTodaysDeliveries = async () => {
    setLoading(true)

    // Get today's date in YYYY-MM-DD format
    const today = new Date().toISOString().split('T')[0]

    const response = await orderService.getScheduleByDate(today)

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

  const handleLogout = () => {
    authStorage.clearAll()
    window.location.href = '/login'
  }

  const handleStartDelivery = () => {
    window.location.href = '/delivery'
  }

  const handleMarkCompleted = async () => {
    if (!selectedDelivery) {
      toast.error("Please select a delivery first")
      return
    }

    if (!confirm(`Mark delivery for ${selectedDelivery.customer_name} as complete?`)) {
      return
    }

    const response = await orderService.completeDelivery(selectedDelivery.order_id)

    if (hasError(response)) {
      toast.error(response.error.error || "Failed to mark delivery as complete")
      return
    }

    toast.success("Delivery marked as complete!")
    setSelectedDelivery(null)
    await fetchTodaysDeliveries()
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

  if (loading) {
    return (
      <div className="min-h-screen bg-background pb-20">
        <MobileHeader title="Dashboard" icon={<BarChart3 className="h-6 w-6 text-primary" />} />
        <div className="flex items-center justify-center p-8">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
        <MobileNav />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background pb-20">
      <MobileHeader title="Dashboard" icon={<BarChart3 className="h-6 w-6 text-primary" />} />

      <div className="p-4 space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">{userName}</h1>
            <div className="text-sm text-muted-foreground">{currentDate}</div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-card border border-border rounded-lg p-4 text-center">
            <h2 className="text-3xl font-bold text-primary">{total}</h2>
            <p className="text-sm text-muted-foreground">Total Today</p>
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
          <h2 className="text-xl font-bold mb-4">Today's Deliveries</h2>

          {deliveries.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">No deliveries scheduled for today</p>
          ) : (
            <div className="space-y-2">
              {deliveries.map((delivery) => (
                <div
                  key={delivery.order_id}
                  className={`border border-border rounded-lg p-4 cursor-pointer hover:bg-accent transition-colors ${
                    selectedDelivery?.order_id === delivery.order_id ? 'bg-accent' : ''
                  }`}
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
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        delivery.status === 'delivered' ? 'bg-green-100 text-green-800' :
                        delivery.status === 'scheduled' ? 'bg-orange-100 text-orange-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {delivery.status.toUpperCase()}
                      </span>
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
              ))}
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="space-y-3">
          <button
            onClick={handleStartDelivery}
            className="w-full bg-primary text-primary-foreground hover:bg-primary/90 font-semibold py-3 px-4 rounded-lg"
          >
            View Delivery Routes
          </button>
          {/* <button
            onClick={handleMarkCompleted}
            disabled={!selectedDelivery}
            className="w-full bg-green-600 text-white hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold py-3 px-4 rounded-lg"
          >
            Mark Selected as Complete
          </button> */}
        </div>

        {/* Selected Delivery Details */}
        {selectedDelivery && (
          <div className="bg-card border-2 border-primary rounded-lg p-4">
            <h3 className="text-lg font-bold mb-3">Selected Delivery Details</h3>
            <div className="space-y-2 text-sm mb-4">
              <p><strong>Order ID:</strong> {selectedDelivery.order_no}</p>
              <p><strong>Customer:</strong> {selectedDelivery.customer_name}</p>
              <p><strong>Phone:</strong> {selectedDelivery.customer_contact}</p>
              <p><strong>Status:</strong> <span className="capitalize">{selectedDelivery.status}</span></p>
              <p><strong>Address:</strong> {selectedDelivery.address}</p>
              <p><strong>Scheduled Time:</strong> {selectedDelivery.scheduled_time}</p>
              <p><strong>Sequence:</strong> #{selectedDelivery.sequence}</p>
            </div>
            <button
              onClick={() => {
                const today = new Date().toISOString().split('T')[0]
                router.push(`/delivery/${today}/${selectedDelivery.order_id}`)
              }}
              className="w-full bg-blue-600 text-white hover:bg-blue-700 font-semibold py-3 px-4 rounded-lg flex items-center justify-center gap-2"
            >
              View Delivery Details
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        )}
      </div>

      <MobileNav />
    </div>
  )
}
