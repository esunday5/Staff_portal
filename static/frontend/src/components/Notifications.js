import React from 'react';

const Notifications = ({ message, type }) => {
  return (
    message && (
      <div className={`notification ${type}`}>
        {message}
      </div>
    )
  );
};

export default Notifications;
