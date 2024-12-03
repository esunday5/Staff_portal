import React, { useState } from 'react';

const CashAdvanceForm = () => {
  const [amount, setAmount] = useState('');
  const [purpose, setPurpose] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const request = { amount, purpose, user_id: 1, request_date: new Date() };

    fetch('/api/requests', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(request)
    })
    .then(response => response.json())
    .then(data => console.log(data));
  };

  return (
    <form onSubmit={handleSubmit}>
      <label>Amount</label>
      <input type="number" value={amount} onChange={(e) => setAmount(e.target.value)} required />
      <label>Purpose</label>
      <textarea value={purpose} onChange={(e) => setPurpose(e.target.value)} required></textarea>
      <button type="submit">Submit Cash Advance</button>
    </form>
  );
};

export default CashAdvanceForm;
