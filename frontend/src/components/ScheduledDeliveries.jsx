import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../styles.css";

const ScheduledDeliveries = () => {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  // Fetch scheduled deliveries when date changes
  useEffect(() => {
    if (selectedDate) {
      fetchScheduledDeliveries(selectedDate);
    }
  }, [selectedDate]);

  const fetchScheduledDeliveries = async (date) => {
    try {
      setLoading(true);
      setError("");

      const token = localStorage.getItem("jwt_token") || "mock-token";

      const response = await fetch(`http://localhost:5005/schedules/${date}`, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch schedules: ${response.statusText}`);
      }

      const data = await response.json();
      setSchedules(data.schedules || []);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching scheduled deliveries:", err);
      setError(err.message);
      setLoading(false);
    }
  };

  // Mark delivery as complete
  const handleMarkComplete = async (orderId, orderNo) => {
    if (!window.confirm(`Mark order ${orderNo} as delivered?`)) {
      return;
    }

    try {
      const token = localStorage.getItem("jwt_token") || "mock-token";

      const response = await fetch(`http://localhost:5005/orders/${orderId}/complete`, {
        method: "PATCH",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to mark as complete");
      }

      alert(`Order ${orderNo} marked as delivered!`);

      // Refresh the schedule
      fetchScheduledDeliveries(selectedDate);
    } catch (err) {
      console.error("Error marking delivery complete:", err);
      alert(`Error: ${err.message}`);
    }
  };

  // Get status badge
  const getStatusBadge = (status) => {
    const badges = {
      scheduled: { text: "Scheduled", color: "#0088FF", bg: "#E5F3FF" },
      in_transit: { text: "In Transit", color: "#FF8800", bg: "#FFF3E5" },
      arrived: { text: "Arrived", color: "#8800FF", bg: "#F3E5FF" },
      delivered: { text: "Delivered", color: "#00AA00", bg: "#E5FFE5" },
      failed: { text: "Failed", color: "#FF0000", bg: "#FFE5E5" },
      skipped: { text: "Skipped", color: "#666", bg: "#F0F0F0" }
    };

    const badge = badges[status] || badges.scheduled;

    return (
      <span style={{
        padding: "4px 12px",
        borderRadius: "12px",
        fontSize: "12px",
        fontWeight: "600",
        color: badge.color,
        backgroundColor: badge.bg
      }}>
        {badge.text}
      </span>
    );
  };

  // Get schedule status color
  const getScheduleStatusColor = (status) => {
    const colors = {
      draft: "#999",
      confirmed: "#0088FF",
      in_progress: "#FF8800",
      completed: "#00AA00",
      cancelled: "#FF0000"
    };
    return colors[status] || "#999";
  };

  return (
    <div className="scheduled-deliveries-container" style={{ padding: "20px", maxWidth: "1400px", margin: "0 auto" }}>
      {/* Header */}
      <div style={{ marginBottom: "30px" }}>
        <button onClick={() => navigate("/deliveries")} style={{ marginBottom: "10px" }}>
          ← Back
        </button>
        <h1 style={{ fontSize: "28px", fontWeight: "bold", marginBottom: "10px" }}>
          Scheduled Deliveries
        </h1>
        <p style={{ color: "#666" }}>
          View all scheduled deliveries by date
        </p>
      </div>

      {/* Date Selector */}
      <div style={{ marginBottom: "30px", display: "flex", gap: "15px", alignItems: "center" }}>
        <label style={{ fontWeight: "600", fontSize: "16px" }}>Select Date:</label>
        <input
          type="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          style={{
            padding: "10px 15px",
            borderRadius: "6px",
            border: "1px solid #DDD",
            fontSize: "16px"
          }}
        />
        <button
          onClick={() => setSelectedDate(new Date().toISOString().split('T')[0])}
          style={{
            padding: "10px 20px",
            backgroundColor: "#F0F0F0",
            border: "1px solid #DDD",
            borderRadius: "6px",
            cursor: "pointer"
          }}
        >
          Today
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div style={{ padding: "15px", backgroundColor: "#FFE5E5", color: "#FF0000", borderRadius: "8px", marginBottom: "20px" }}>
          ⚠ {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div style={{ textAlign: "center", padding: "40px", color: "#999" }}>
          Loading schedules...
        </div>
      )}

      {/* No Schedules */}
      {!loading && schedules.length === 0 && (
        <div style={{
          textAlign: "center",
          padding: "60px",
          backgroundColor: "#F8F9FA",
          borderRadius: "8px",
          color: "#999"
        }}>
          <h3 style={{ marginBottom: "10px" }}>No schedules found for {selectedDate}</h3>
          <p>Create a new schedule from the Order Scheduling page</p>
          <button
            onClick={() => navigate("/schedule-orders")}
            style={{
              marginTop: "20px",
              padding: "12px 24px",
              backgroundColor: "#4CAF50",
              color: "white",
              border: "none",
              borderRadius: "6px",
              cursor: "pointer",
              fontWeight: "600"
            }}
          >
            Go to Order Scheduling
          </button>
        </div>
      )}

      {/* Schedules List */}
      {!loading && schedules.map((schedule) => (
        <div
          key={schedule.schedule_id}
          style={{
            backgroundColor: "white",
            borderRadius: "8px",
            boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
            marginBottom: "30px",
            overflow: "hidden"
          }}
        >
          {/* Schedule Header */}
          <div
            style={{
              padding: "20px",
              backgroundColor: "#F8F9FA",
              borderBottom: "1px solid #EEE",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center"
            }}
          >
            <div>
              <h3 style={{ marginBottom: "8px", fontSize: "20px" }}>
                Schedule #{schedule.schedule_id.substring(0, 8)}
              </h3>
              <div style={{ display: "flex", gap: "20px", fontSize: "14px", color: "#666" }}>
                <span>📅 {schedule.schedule_date}</span>
                <span>👤 {schedule.driver_name || "Unassigned"}</span>
                {schedule.driver_contact && <span>📞 {schedule.driver_contact}</span>}
                {schedule.team && <span>👥 {schedule.team}</span>}
              </div>
            </div>

            <div style={{ textAlign: "right" }}>
              <div style={{
                fontSize: "24px",
                fontWeight: "bold",
                color: getScheduleStatusColor(schedule.status),
                textTransform: "uppercase"
              }}>
                {schedule.status}
              </div>
              <div style={{ fontSize: "14px", color: "#666", marginTop: "5px" }}>
                {schedule.total_locations} / {schedule.max_locations} locations
              </div>
            </div>
          </div>

          {/* Deliveries Table */}
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead style={{ backgroundColor: "#F0F0F0" }}>
                <tr>
                  <th style={{ padding: "12px", textAlign: "left", fontWeight: "600" }}>#</th>
                  <th style={{ padding: "12px", textAlign: "left", fontWeight: "600" }}>Order No</th>
                  <th style={{ padding: "12px", textAlign: "left", fontWeight: "600" }}>Type</th>
                  <th style={{ padding: "12px", textAlign: "left", fontWeight: "600" }}>Customer</th>
                  <th style={{ padding: "12px", textAlign: "left", fontWeight: "600" }}>Address</th>
                  <th style={{ padding: "12px", textAlign: "left", fontWeight: "600" }}>Postal Code</th>
                  <th style={{ padding: "12px", textAlign: "left", fontWeight: "600" }}>Items</th>
                  <th style={{ padding: "12px", textAlign: "left", fontWeight: "600" }}>ETA</th>
                  <th style={{ padding: "12px", textAlign: "left", fontWeight: "600" }}>Status</th>
                  <th style={{ padding: "12px", textAlign: "left", fontWeight: "600" }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {schedule.deliveries && schedule.deliveries.map((delivery) => (
                  <tr
                    key={delivery.sequence}
                    style={{
                      borderBottom: "1px solid #EEE",
                      backgroundColor: delivery.status === "delivered" ? "#F0FFF0" : "white"
                    }}
                  >
                    <td style={{ padding: "12px", fontWeight: "bold", fontSize: "16px" }}>
                      {delivery.sequence}
                    </td>
                    <td style={{ padding: "12px", fontWeight: "600" }}>
                      {delivery.order_no}
                    </td>
                    <td style={{ padding: "12px", fontSize: "12px", textTransform: "uppercase", color: "#666" }}>
                      {delivery.order_type.replace('_', ' ')}
                    </td>
                    <td style={{ padding: "12px" }}>
                      <div style={{ fontWeight: "600" }}>{delivery.customer_name}</div>
                      <div style={{ fontSize: "12px", color: "#666" }}>{delivery.customer_contact}</div>
                    </td>
                    <td style={{ padding: "12px", fontSize: "13px", maxWidth: "250px" }}>
                      {delivery.address}
                      <br />
                      <span style={{ color: "#666" }}>{delivery.housing_type}</span>
                    </td>
                    <td style={{ padding: "12px", fontWeight: "600" }}>
                      {delivery.postal_code}
                    </td>
                    <td style={{ padding: "12px", textAlign: "center" }}>
                      {delivery.total_items}
                      {delivery.requires_warehouse_return && (
                        <div style={{ fontSize: "11px", color: "#FF8800" }}>⚠ Return trip</div>
                      )}
                    </td>
                    <td style={{ padding: "12px", fontSize: "13px" }}>
                      {delivery.estimated_arrival || "-"}
                      {delivery.actual_arrival && (
                        <div style={{ fontSize: "11px", color: "#00AA00" }}>
                          ✓ {delivery.actual_arrival}
                        </div>
                      )}
                    </td>
                    <td style={{ padding: "12px" }}>
                      {getStatusBadge(delivery.status)}
                    </td>
                    <td style={{ padding: "12px" }}>
                      {delivery.status !== "delivered" && (
                        <button
                          onClick={() => handleMarkComplete(delivery.order_id, delivery.order_no)}
                          style={{
                            padding: "6px 12px",
                            backgroundColor: "#4CAF50",
                            color: "white",
                            border: "none",
                            borderRadius: "4px",
                            cursor: "pointer",
                            fontSize: "12px"
                          }}
                        >
                          Mark Done
                        </button>
                      )}
                      {delivery.status === "delivered" && (
                        <span style={{ color: "#00AA00", fontSize: "12px" }}>✓ Completed</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Schedule Footer */}
          <div style={{
            padding: "15px 20px",
            backgroundColor: "#F8F9FA",
            borderTop: "1px solid #EEE",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center"
          }}>
            <div style={{ fontSize: "14px", color: "#666" }}>
              Start: {schedule.start_time} | Estimated End: {schedule.estimated_end_time || "Calculating..."}
            </div>
            {schedule.route_polyline && (
              <button
                onClick={() => alert("Map view coming soon!")}
                style={{
                  padding: "8px 16px",
                  backgroundColor: "#0088FF",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                  fontSize: "14px"
                }}
              >
                🗺 View Route Map
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ScheduledDeliveries;