import React, { useState, useEffect } from "react";
import axios from "axios";

const Dashboard = () => {
  const [deliveries, setDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    // Replace with your backend API endpoint
    axios
      .get("http://localhost:8000/api/deliveries") //// replace with your service URL
      .then((response) => {
        setDeliveries(response.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError("Failed to fetch deliveries");
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Loading deliveries...</p>;
  if (error) return <p>{error}</p>;

  // Compute stats
  const pending = deliveries.filter(d => d.status === "Pending").length;
  const inProgress = deliveries.filter(d => d.status === "In Progress").length;
  const delivered = deliveries.filter(d => d.status === "Delivered").length;

  return (
    <div className="dashboard">
      <h1>Driver Dashboard</h1>

      <div className="stats">
        <div className="stat-card">
          <h2>{pending}</h2>
          <p>Pending Deliveries</p>
        </div>
        <div className="stat-card">
          <h2>{inProgress}</h2>
          <p>In Progress</p>
        </div>
        <div className="stat-card">
          <h2>{delivered}</h2>
          <p>Delivered</p>
        </div>
      </div>

      <h2>Upcoming Deliveries</h2>
      <ul>
        {deliveries
          .filter(d => d.status !== "Delivered")
          .map(d => (
            <li key={d.id}>
              {d.customer} - {d.address} at {d.scheduledTime} ({d.status})
            </li>
          ))}
      </ul>
    </div>
  );
};

export default Dashboard;
