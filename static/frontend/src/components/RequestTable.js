import React, { useEffect, useState } from 'react';

const RequestTable = () => {
  const [requests, setRequests] = useState([]);

  useEffect(() => {
    fetch('/api/requests')
      .then(response => response.json())
      .then(data => setRequests(data));
  }, []);

  return (
    <table>
      <thead>
        <tr>
          <th>Request ID</th>
          <th>Amount</th>
          <th>Purpose</th>
          <th>Status</th>
          <th>Date</th>
        </tr>
      </thead>
      <tbody>
        {requests.map((request) => (
          <tr key={request.id}>
            <td>{request.id}</td>
            <td>{request.amount}</td>
            <td>{request.purpose}</td>
            <td>{request.status}</td>
            <td>{new Date(request.request_date).toLocaleDateString()}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default RequestTable;
