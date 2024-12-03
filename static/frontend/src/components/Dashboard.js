import React from 'react';
import Sidebar from './Sidebar';
import RequestTable from './RequestTable';
import CashAdvanceForm from './CashAdvanceForm';

const Dashboard = () => {
  return (
    <div className="dashboard-container">
      <Sidebar />
      <div className="dashboard-content">
        <h1>Officer Dashboard</h1>
        <CashAdvanceForm />
        <RequestTable />
      </div>
    </div>
  );
};

export default Dashboard;
