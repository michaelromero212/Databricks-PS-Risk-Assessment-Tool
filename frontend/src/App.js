import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import EngagementOverview from './pages/EngagementOverview';
import EngagementDetail from './pages/EngagementDetail';
import Dashboard from './pages/Dashboard';
import ImportData from './pages/ImportData';
import Feedback from './pages/Feedback';

/**
 * Header Component with navigation
 */
function Header() {
    return (
        <header className="app-header">
            <div className="header-content">
                <div className="header-logo">
                    <div className="header-logo-icon">PS</div>
                    <div>
                        <div className="header-title">Risk Assessment Tool</div>
                        <div className="header-subtitle">Databricks Professional Services</div>
                    </div>
                </div>
                <nav className="header-nav" role="navigation" aria-label="Main navigation">
                    <NavLink
                        to="/"
                        className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                        end
                    >
                        Overview
                    </NavLink>
                    <NavLink
                        to="/dashboard"
                        className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                    >
                        Dashboard
                    </NavLink>
                    <NavLink
                        to="/import"
                        className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                    >
                        Import Data
                    </NavLink>
                    <NavLink
                        to="/feedback"
                        className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                    >
                        Feedback
                    </NavLink>
                </nav>
            </div>
        </header>
    );
}

/**
 * Main App Component
 */
function App() {
    return (
        <Router>
            <div className="app-container">
                {/* Skip link for accessibility */}
                <a href="#main-content" className="skip-link">
                    Skip to main content
                </a>

                <Header />

                <main id="main-content" className="main-content">
                    <Routes>
                        <Route path="/" element={<EngagementOverview />} />
                        <Route path="/engagement/:id" element={<EngagementDetail />} />
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/import" element={<ImportData />} />
                        <Route path="/feedback" element={<Feedback />} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App;
