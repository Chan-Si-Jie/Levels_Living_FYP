import { useState } from "react";
import { useNavigate } from "react-router-dom"; // 👈 add this for navigation
import "../styles.css";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const navigate = useNavigate(); // 👈 hook from react-router

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    try {
      // Call UserMS via Kong API Gateway
      const response = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email: email,
          password: password
        })
      });

      const data = await response.json();

      if (response.ok && data.access_token) {
        console.log("Login successful:", data.user);

        // Store JWT token in localStorage
        localStorage.setItem("jwt_token", data.access_token);
        localStorage.setItem("refresh_token", data.refresh_token);
        localStorage.setItem("user_email", data.user.email);
        localStorage.setItem("user_role", data.user.role);

        // Redirect to deliveries page
        navigate("/deliveries");
      } else {
        setError(data.error || "Login failed. Please check your credentials.");
      }
    } catch (err) {
      console.error("Login error:", err);
      setError("Unable to connect to server. Please try again.");
    }
  };

  return (
    <div className="login-container">
      <div className="login-content">
        {/* Logo Section */}
        <div className="logo-section">
          <div className="logo-container">
            <img src="../logo.png" alt="Logo" className="logo" />
          </div>
        </div>

        {/* Welcome Text */}
        <div className="welcome-section">
          <div className="welcome-container">
            <h1 className="welcome-text">Welcome</h1>
          </div>
        </div>

        {/* Form Section */}
        <form className="form-section" onSubmit={handleSubmit}>
          {/* Email Input */}
          <div className="input-group">
            <div className="input-container">
              <div className="input-field">
                <input
                  type="email"
                  placeholder="Email"
                  className="email-input"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
            </div>
          </div>

          {/* Password Input */}
          <div className="input-group">
            <div className="input-container">
              <div className="input-field">
                <input
                  type="password"
                  placeholder="Password"
                  className="password-input"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
            </div>
          </div>

          {/* Bottom Section */}
          <div className="bottom-section">
            {/* Sign In Button */}
            <div className="button-group">
              <div className="button-container">
                <button type="submit" className="signin-button">
                  <span className="signin-text">Sign in</span>
                </button>
              </div>
            </div>

            {/* Error message */}
            {error && <p style={{ color: "red" }}>{error}</p>}

            {/* Forgot Password Link */}
            <div className="forgot-password-group">
              <a href="#" className="forgot-password-link">
                Forgot password?
              </a>
            </div>

            {/* Spacer */}
            <div className="spacer"></div>
          </div>
        </form>
      </div>
    </div>
  );
}
