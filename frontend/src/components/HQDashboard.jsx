import React, { useState, useEffect } from "react";
import axios from "axios";
// Optional: Chart library
import { Bar, Pie } from "react-chartjs-2";

const HQDashboard = () => {
  const [deliveries, setDeliveries] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const deliveryRes = await axios.get("http://localhost:8000/api/deliveries");// replace with your service URL
        const driverRes = await axios.get("http://localhost:8000/api/drivers");// replace with your service URL
        setDeliveries(deliveryRes.data);
        setDrivers(driverRes.data);
        generateAlerts(deliveryRes.data);
        setLoading(false);
      } catch (err) {
        console.error(err);
        setError("Failed to fetch data");
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const generateAlerts = (deliveries) => {
    const delayed = deliveries.filter(d => d.status === "Delayed");
    const highPriority = deliveries.filter(d => d.priority === "High");
    setAlerts([...delayed, ...highPriority]);
  };

  if (loading) return <p>Loading HQ Dashboard...</p>;
  if (error) return <p>{error}</p>;

  // Summary Stats
  const pending = deliveries.filter(d => d.status === "Pending").length;
  const inProgress = deliveries.filter(d => d.status === "In Progress").length;
  const delivered = deliveries.filter(d => d.status === "Delivered").length;

  // Chart Data
  const statusData = {
    labels: ["Pending", "In Progress", "Delivered"],
    datasets: [
      {
        label: "Deliveries",
        data: [pending, inProgress, delivered],
        backgroundColor: ["#FFA500", "#1E90FF", "#32CD32"],
      },
    ],
  };

  return (
    <div className="hq-dashboard">
      <h1>Headquarters Dashboard</h1>

      {/*  Overview / Summary Stats */}
      <div className="stats">
        <div className="stat-card"><h2>{pending}</h2><p>Pending</p></div>
        <div className="stat-card"><h2>{inProgress}</h2><p>In Progress</p></div>
        <div className="stat-card"><h2>{delivered}</h2><p>Delivered</p></div>
        <div className="stat-card"><h2>{drivers.length}</h2><p>Total Drivers</p></div>
      </div>

      {/* Visual Analytics */}
      <div className="charts">
        <h2>Delivery Status Overview</h2>
        <Pie data={statusData} />
      </div>

      {/* Delivery Monitoring */}
      <div className="deliveries">
        <h2>Ongoing Deliveries</h2>
        <ul>
          {deliveries.filter(d => d.status !== "Delivered").map(d => (
            <li key={d.id}>
              {d.customer} - {d.address} ({d.status}) | Driver: {d.driverName}
            </li>
          ))}
        </ul>
      </div>

      {/*  Operational Controls */}
      <div className="operations">
        <h2>Assign / Reassign Deliveries</h2>
        {/* Placeholder for assigning delivery logic */}
        <p>Drag & drop or assign deliveries to drivers here.</p>
      </div>

      {/*  Reports & Export */}
      <div className="reports">
        <h2>Generate Reports</h2>
        <button onClick={() => console.log("Generate PDF")}>Export PDF</button>
        <button onClick={() => console.log("Generate CSV")}>Export CSV</button>
      </div>

      {/*  Alerts / Notifications */}
      <div className="alerts">
        <h2>Alerts</h2>
        <ul>
          {alerts.map(d => (
            <li key={d.id}>
              ⚠ {d.customer} - {d.address} ({d.status || d.priority})
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default HQDashboard;
