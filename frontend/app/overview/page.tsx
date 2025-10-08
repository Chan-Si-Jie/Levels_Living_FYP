"use client";

import { useEffect, useState } from "react";
import { MobileHeader } from "@/components/mobile-header";
import { MobileNav } from "@/components/mobile-nav";
import { DeliveryMap } from "@/components/delivery-map";
import { MapPin } from "lucide-react";
import { orderService, hasError } from "@/lib/api/order-service";
import { toast } from "sonner";

export default function OverviewPage() {
  const [locations, setLocations] = useState<any[]>([]); // Stores delivery locations
  const [routePolyline, setRoutePolyline] = useState<string | null>(null); // Stores the route polyline
  const [loading, setLoading] = useState(false);

  // Fetch today's schedules
  const fetchSchedules = async () => {
    setLoading(true);

    // Get today's date in YYYY-MM-DD format
    const today = new Date().toISOString().split("T")[0];

    const response = await orderService.getScheduleByDate(today);

    if (hasError(response)) {
      toast.error(response.error.error || "Failed to fetch schedules");
      setLoading(false);
      return;
    }

    if (response.data?.schedules && response.data.schedules.length > 0) {
      // Sort schedules by the most recent (assuming `updated_at` or `created_at` exists)
      const sortedSchedules = response.data.schedules.sort(
        (a: any, b: any) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
      );

      // Get the latest schedule
      const latestSchedule = sortedSchedules[0];
      console.log("Latest Schedule:", latestSchedule);

      // Extract delivery locations and route polyline from the latest schedule
      const extractedLocations = latestSchedule.deliveries.map((delivery: any) => ({
        lat: delivery.latitude,
        lng: delivery.longitude,
        address: delivery.address,
        customer: delivery.customer_name,
        sequence: delivery.sequence, // Include sequence number
      }));

      setLocations(extractedLocations);
      setRoutePolyline(latestSchedule.route_polyline || null); // Set the route polyline
    } else {
      toast.error("No schedules found for today");
    }

    setLoading(false);
  };

  // Fetch schedules on component mount
  useEffect(() => {
    fetchSchedules();
  }, []);

  return (
    <div className="min-h-screen pb-20">
      <MobileHeader
        title="Overview"
        icon={<MapPin className="h-6 w-6 text-primary" />}
      />
      <main>
        {loading ? (
          <p className="text-center mt-4">Loading schedules...</p>
        ) : (
          <DeliveryMap locations={locations} routePolyline={routePolyline} />
        )}
      </main>
      <MobileNav /> 
    </div>
  );
}