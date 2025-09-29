import React, { useEffect, useState } from "react";
import "./styles.css";

const DeliveryDetails = () => {
  const [deliveries, setDeliveries] = useState([]);

  // Example: Fetch deliveries from your microservice
  useEffect(() => {
    const fetchDeliveries = async () => {
      try {
        const res = await fetch("http://localhost:5000/api/deliveries"); // replace with your service URL
        const data = await res.json();
        setDeliveries(data);
      } catch (err) {
        console.error("Failed to fetch deliveries:", err);
      }
    };

    fetchDeliveries();
  }, []);

  return (
    <div className="deliveries-container">
      <div className="main-content">
        {/* Header */}
        <div className="header-section">
          <div className="back-button">←</div>
          <div className="title-section">
            <h1 className="page-title">Deliveries</h1>
          </div>
          <div className="action-section"></div>
        </div>

        {/* Today's Deliveries */}
        <div className="section-header">
          <h2 className="section-title">Today's Deliveries</h2>
        </div>

        {/* Loop through deliveries */}
        {deliveries.map((delivery, index) => (
          <div className="delivery-item" key={index}>
            <div className="delivery-info">
              <div className="customer-name">{delivery.name}</div>
              <div className="delivery-address">{delivery.address}</div>
            </div>
            <div className="start-button">
              <span className="start-text">Start</span>
            </div>
          </div>
        ))}

        {/* Spacer */}
        <div className="spacer" />
      </div>

      {/* Bottom navigation (same as before) */}
      <div className="bottom-navigation">
        {/* ... */}
      </div>
    </div>
  );
};

export default DeliveryDetails;
