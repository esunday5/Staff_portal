import React from 'react';

const Sidebar = () => {
  return (
    <div className="sidebar">
      <ul>
        <li><a href="/dashboard">Dashboard Overview</a></li>
        <li><a href="/requests">My Requests</a></li>
        <li><a href="/logout">Logout</a></li>
      </ul>
    </div>
  );
};

export default Sidebar;
