import React from 'react';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export const NotFound = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate('/');
    }, 3000);

    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div>
      <h1>Resource not available</h1>
      <p>You will be redirected to the homepage ...</p>
    </div>
  );
};
