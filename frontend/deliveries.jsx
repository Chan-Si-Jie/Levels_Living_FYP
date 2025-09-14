import React, { useEffect, useState } from "react";
import "./styles.css";

const deliveriesData = [
  { date: "2025-09-15", count: 12 },
  { date: "2025-09-16", count: 10 },
  { date: "2025-09-17", count: 15 },
  { date: "2025-09-18", count: 8 }
];

const formatDate = (dateStr) => {
  const options = { weekday: "short", month: "short", day: "numeric" };
  return new Date(dateStr).toLocaleDateString("en-US", options);
};

const DeliveryCard = ({ date, count }) => (
  <div className="delivery-card">
    <div className="card-content">
      <div className="icon-container">
        <div className="calendar-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path
              d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z"
              fill="#121417"
            />
          </svg>
        </div>
      </div>
      <div className="card-info">
        <div className="date-info">
          <h3 className="date-text">{formatDate(date)}</h3>
          <p className="delivery-count">{count} deliveries</p>
        </div>
      </div>
    </div>
    <div className="card-action">
      <div className="action-icon-small">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path
            d="M8.59 16.59L13.17 12L8.59 7.41L10 6L16 12L10 18L8.59 16.59Z"
            fill="#121417"
          />
        </svg>
      </div>
    </div>
  </div>
);

const DeliveryPage = () => {
  const [deliveries, setDeliveries] = useState([]);

  useEffect(() => {
    // For now we use static data. Later, replace with fetch API call
    setDeliveries(deliveriesData);
  }, []);

  const today = deliveries.slice(0, 1); // first item as Today
  const upcoming = deliveries.slice(1); // the rest as Upcoming

  return (
    <div className="deliveries-container">
      <div className="main-content">
        {/* Header */}
        <div className="header-section">
          <div className="profile-section">
            <div className="profile-image-container">
              <div className="profile-image"></div>
            </div>
          </div>
          <div className="title-section">
            <h1 className="page-title">Deliveries</h1>
          </div>
          <div className="action-section">
            <div className="action-button">
              <svg
                className="action-icon"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
              >
                <path
                  d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"
                  fill="#121417"
                />
              </svg>
            </div>
          </div>
        </div>

        {/* Today */}
        <div className="section-header">
          <h2 className="section-title">Today</h2>
        </div>
        {today.map((d, idx) => (
          <DeliveryCard key={idx} date={d.date} count={d.count} />
        ))}

        {/* Upcoming */}
        <div className="section-header">
          <h2 className="section-title">Upcoming</h2>
        </div>
        {upcoming.map((d, idx) => (
          <DeliveryCard key={idx} date={d.date} count={d.count} />
        ))}

        <div className="spacer"></div>
      </div>

      {/* Bottom Navigation */}
      <div className="bottom-navigation">
        {/* Same as your HTML */}
      </div>
    </div>
  );
};

export default DeliveryPage;
