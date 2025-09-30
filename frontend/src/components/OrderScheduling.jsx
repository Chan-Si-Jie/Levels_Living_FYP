import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../styles.css";

const OrderScheduling = () => {
  const [orders, setOrders] = useState([]);
  const [selectedOrders, setSelectedOrders] = useState([]);
  const [scheduleDate, setScheduleDate] = useState("");
  const [driverId, setDriverId] = useState("");
  const [team, setTeam] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const navigate = useNavigate();

  // Fetch unscheduled orders from OrderMS
  useEffect(() => {
    fetchUnscheduledOrders();
  }, []);

  const fetchUnscheduledOrders = async () => {
    try {
      setLoading(true);
      setError("");

      // TODO: Replace with actual JWT token from login
      const token = localStorage.getItem("jwt_token") || "mock-token";

      const response = await fetch("http://localhost:5005/orders/unscheduled", {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch orders: ${response.statusText}`);
      }

      const data = await response.json();
      setOrders(data.orders || []);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching unscheduled orders:", err);
      setError(err.message);
      setLoading(false);
    }
  };

  // Handle order selection (checkbox)
  const handleOrderSelect = (orderId) => {
    setSelectedOrders(prev => {
      if (prev.includes(orderId)) {
        return prev.filter(id => id !== orderId);
      } else {
        // Check 18 location limit
        if (prev.length >= 18) {
          alert("Maximum 18 locations per day (3rd party delivery agreement)");
          return prev;
        }
        return [...prev, orderId];
      }
    });
  };

  // Handle select all
  const handleSelectAll = () => {
    if (selectedOrders.length === orders.length) {
      setSelectedOrders([]);
    } else {
      const allOrderIds = orders.slice(0, 18).map(o => o.order_id);
      setSelectedOrders(allOrderIds);
    }
  };

  // Handle schedule creation
  const handleCreateSchedule = async () => {
    if (selectedOrders.length === 0) {
      alert("Please select at least one order");
      return;
    }

    if (!scheduleDate) {
      alert("Please select a schedule date");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setSuccess("");

      const token = localStorage.getItem("jwt_token") || "mock-token";

      const response = await fetch("http://localhost:5005/orders/schedule", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          order_ids: selectedOrders,
          schedule_date: scheduleDate,
          driver_id: driverId || null,
          team: team || null
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to create schedule");
      }

      const data = await response.json();
      setSuccess(`Schedule created successfully! ${data.total_locations} locations scheduled.`);

      // Reset form
      setSelectedOrders([]);
      setScheduleDate("");
      setDriverId("");
      setTeam("");

      // Refresh orders list
      setTimeout(() => {
        fetchUnscheduledOrders();
        setSuccess("");
      }, 2000);

    } catch (err) {
      console.error("Error creating schedule:", err);
      setError(err.message);
      setLoading(false);
    }
  };

  // Get order type badge style
  const getOrderTypeBadge = (orderType) => {
    const badges = {
      asap: { text: "ASAP", color: "#FF4444", bg: "#FFE5E5" },
      adhoc: { text: "Adhoc", color: "#FF8800", bg: "#FFF3E5" },
      pre_order: { text: "Pre-order", color: "#0088FF", bg: "#E5F3FF" },
      custom_date: { text: "Custom Date", color: "#8800FF", bg: "#F3E5FF" }
    };

    const badge = badges[orderType] || badges.pre_order;

    return (
      <span style={{
        padding: "4px 8px",
        borderRadius: "4px",
        fontSize: "12px",
        fontWeight: "600",
        color: badge.color,
        backgroundColor: badge.bg
      }}>
        {badge.text}
      </span>
    );
  };

  if (loading && orders.length === 0) {
    return <div className="loading-container">Loading orders...</div>;
  }

  return (
    <div className="scheduling-container" style={{ padding: "20px", maxWidth: "1200px", margin: "0 auto" }}>
      {/* Header */}
      <div style={{ marginBottom: "30px" }}>
        <button onClick={() => navigate("/deliveries")} style={{ marginBottom: "10px" }}>
          ← Back
        </button>
        <h1 style={{ fontSize: "28px", fontWeight: "bold", marginBottom: "10px" }}>
          Order Scheduling
        </h1>
        <p style={{ color: "#666" }}>
          Select up to 18 orders to schedule for delivery (sorted by priority)
        </p>
      </div>

      {/* Error/Success Messages */}
      {error && (
        <div style={{ padding: "15px", backgroundColor: "#FFE5E5", color: "#FF0000", borderRadius: "8px", marginBottom: "20px" }}>
          ⚠ {error}
        </div>
      )}

      {success && (
        <div style={{ padding: "15px", backgroundColor: "#E5FFE5", color: "#00AA00", borderRadius: "8px", marginBottom: "20px" }}>
          ✓ {success}
        </div>
      )}

      {/* Scheduling Form */}
      <div style={{ backgroundColor: "#F8F9FA", padding: "20px", borderRadius: "8px", marginBottom: "30px" }}>
        <h3 style={{ marginBottom: "15px" }}>Schedule Details</h3>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "15px" }}>
          <div>
            <label style={{ display: "block", marginBottom: "5px", fontWeight: "600" }}>
              Schedule Date *
            </label>
            <input
              type="date"
              value={scheduleDate}
              onChange={(e) => setScheduleDate(e.target.value)}
              min={new Date().toISOString().split('T')[0]}
              style={{
                width: "100%",
                padding: "10px",
                borderRadius: "4px",
                border: "1px solid #DDD"
              }}
            />
          </div>

          <div>
            <label style={{ display: "block", marginBottom: "5px", fontWeight: "600" }}>
              Driver ID (Optional)
            </label>
            <input
              type="text"
              value={driverId}
              onChange={(e) => setDriverId(e.target.value)}
              placeholder="e.g., DRV001"
              style={{
                width: "100%",
                padding: "10px",
                borderRadius: "4px",
                border: "1px solid #DDD"
              }}
            />
          </div>

          <div>
            <label style={{ display: "block", marginBottom: "5px", fontWeight: "600" }}>
              Team (Optional)
            </label>
            <input
              type="text"
              value={team}
              onChange={(e) => setTeam(e.target.value)}
              placeholder="e.g., Team A"
              style={{
                width: "100%",
                padding: "10px",
                borderRadius: "4px",
                border: "1px solid #DDD"
              }}
            />
          </div>
        </div>

        <div style={{ marginTop: "20px", display: "flex", gap: "10px", alignItems: "center" }}>
          <button
            onClick={handleCreateSchedule}
            disabled={selectedOrders.length === 0 || !scheduleDate}
            style={{
              padding: "12px 24px",
              backgroundColor: selectedOrders.length === 0 || !scheduleDate ? "#CCC" : "#4CAF50",
              color: "white",
              border: "none",
              borderRadius: "6px",
              fontWeight: "600",
              cursor: selectedOrders.length === 0 || !scheduleDate ? "not-allowed" : "pointer"
            }}
          >
            Create Schedule ({selectedOrders.length} orders)
          </button>

          <span style={{ color: "#666" }}>
            {18 - selectedOrders.length} slots remaining
          </span>
        </div>
      </div>

      {/* Orders Table */}
      <div style={{ backgroundColor: "white", borderRadius: "8px", boxShadow: "0 2px 4px rgba(0,0,0,0.1)" }}>
        {/* Table Header */}
        <div style={{ padding: "20px", borderBottom: "1px solid #EEE", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h3>Unscheduled Orders ({orders.length})</h3>
          <button
            onClick={handleSelectAll}
            style={{
              padding: "8px 16px",
              backgroundColor: "#F0F0F0",
              border: "1px solid #DDD",
              borderRadius: "4px",
              cursor: "pointer"
            }}
          >
            {selectedOrders.length === orders.length ? "Deselect All" : "Select All"}
          </button>
        </div>

        {/* Table */}
        {orders.length === 0 ? (
          <div style={{ padding: "40px", textAlign: "center", color: "#999" }}>
            No unscheduled orders found
          </div>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead style={{ backgroundColor: "#F8F9FA" }}>
                <tr>
                  <th style={{ padding: "12px", textAlign: "left", fontWeight: "600" }}>Select</th>
                  <th style={{ padding: "12px", textAlign: "left", fontWeight: "600" }}>Order No</th>
                  <th style={{ padding: "12px", textAlign: "left", fontWeight: "600" }}>Type</th>
                  <th style={{ padding: "12px", textAlign: "left", fontWeight: "600" }}>Customer</th>
                  <th style={{ padding: "12px", textAlign: "left", fontWeight: "600" }}>Postal Code</th>
                  <th style={{ padding: "12px", textAlign: "left", fontWeight: "600" }}>Address</th>
                  <th style={{ padding: "12px", textAlign: "left", fontWeight: "600" }}>Preferred Time</th>
                  <th style={{ padding: "12px", textAlign: "left", fontWeight: "600" }}>Items</th>
                  <th style={{ padding: "12px", textAlign: "left", fontWeight: "600" }}>Value</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((order, index) => (
                  <tr
                    key={order.order_id}
                    style={{
                      borderBottom: "1px solid #EEE",
                      backgroundColor: selectedOrders.includes(order.order_id) ? "#F0F8FF" : "white"
                    }}
                  >
                    <td style={{ padding: "12px" }}>
                      <input
                        type="checkbox"
                        checked={selectedOrders.includes(order.order_id)}
                        onChange={() => handleOrderSelect(order.order_id)}
                        style={{ width: "18px", height: "18px", cursor: "pointer" }}
                      />
                    </td>
                    <td style={{ padding: "12px", fontWeight: "600" }}>{order.order_no}</td>
                    <td style={{ padding: "12px" }}>{getOrderTypeBadge(order.order_type)}</td>
                    <td style={{ padding: "12px" }}>
                      <div>{order.customer_name}</div>
                      <div style={{ fontSize: "12px", color: "#666" }}>{order.customer_contact}</div>
                    </td>
                    <td style={{ padding: "12px", fontWeight: "600" }}>{order.customer_postal_code}</td>
                    <td style={{ padding: "12px", fontSize: "13px" }}>
                      {order.customer_street} {order.customer_unit}
                    </td>
                    <td style={{ padding: "12px" }}>
                      {order.preferred_delivery_time || "-"}
                    </td>
                    <td style={{ padding: "12px", textAlign: "center" }}>{order.total_items}</td>
                    <td style={{ padding: "12px" }}>${parseFloat(order.order_value).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Info Box */}
      <div style={{ marginTop: "20px", padding: "15px", backgroundColor: "#FFF9E5", borderLeft: "4px solid #FFD700", borderRadius: "4px" }}>
        <strong>ℹ Note:</strong> Orders are automatically sorted by priority (ASAP → Adhoc → Pre-order → Custom Date) and then by postal code (East to West).
      </div>
    </div>
  );
};

export default OrderScheduling;