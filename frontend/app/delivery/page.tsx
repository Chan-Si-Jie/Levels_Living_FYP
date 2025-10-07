"use client"

import { useState, useEffect } from "react"
import { MobileHeader } from "@/components/mobile-header"
import { MobileNav } from "@/components/mobile-nav"
import { Button } from "@/components/ui/button"
import { DeliveryDateList } from "@/components/delivery-date-list"
import { Truck, Loader2, RefreshCw } from "lucide-react"
import { orderService } from "@/lib/api/order-service"
import { hasError } from "@/lib/api-client"
import { toast } from "sonner"
import type { DeliveryDate } from "@/lib/delivery-data"

export default function DeliveryPage() {
  const [deliveryDates, setDeliveryDates] = useState<DeliveryDate[]>([])
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    fetchAllSchedules()
  }, [])

  const handleRefresh = async () => {
    setRefreshing(true)
    await fetchAllSchedules()
    setRefreshing(false)
    toast.success("Delivery list refreshed")
  }

  const fetchAllSchedules = async () => {
    const loadingTimeout = setTimeout(() => setLoading(true), 200)

    // Fetch all schedules (without date filter)
    const response = await orderService.getSchedules()
    clearTimeout(loadingTimeout)

    if (hasError(response)) {
      toast.error(response.error.error || "Failed to load schedules")
      setLoading(false)
      return
    }

    if (response.data && response.data.schedules) {
      // Group schedules by date and format for DeliveryDateList
      const schedulesGrouped = response.data.schedules.reduce((acc: any, schedule: any) => {
        const date = schedule.schedule_date
        if (!acc[date]) {
          acc[date] = {
            id: date,
            date: formatDate(date),
            count: 0,
            isFavorite: false
          }
        }
        acc[date].count += schedule.total_locations || 0
        return acc
      }, {})

      // Filter out dates with 0 deliveries
      const dates = Object.values(schedulesGrouped).filter((d: any) => d.count > 0) as DeliveryDate[]
      setDeliveryDates(dates)
    }

    setLoading(false)
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    const options: Intl.DateTimeFormatOptions = { day: 'numeric', month: 'short', year: 'numeric' }
    return date.toLocaleDateString('en-US', options)
  }

  return (
    <div className="min-h-screen pb-20">
      <MobileHeader title="Delivery" icon={<Truck className="h-6 w-6 text-primary" />} />

      <main>
        {/* Refresh Button */}
        <div className="p-4">
          <Button
            onClick={handleRefresh}
            disabled={loading || refreshing}
            variant="outline"
            className="w-full flex items-center justify-center gap-2"
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            {refreshing ? "Refreshing..." : "Refresh Deliveries"}
          </Button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center p-8">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : deliveryDates.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            <p>No scheduled deliveries found</p>
            <p className="text-sm mt-2">Create schedules from the Schedule page</p>
          </div>
        ) : (
          <DeliveryDateList dates={deliveryDates} basePath="/delivery" />
        )}
      </main>
      <MobileNav />
    </div>
  )
}
