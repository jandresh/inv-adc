import { Typography, Box } from '@mui/material';
import React from 'react';
import { useLocation } from 'react-router';

import { PageTitle } from '../PageTitle';

export const PageDefault = () => {
  const location = useLocation();
  return (
    <>
      <PageTitle title={location.pathname.replaceAll('/', ' ').trimStart()} />
      <Box sx={{ p: 3 }}>
        <Typography paragraph>
          Cali, Colombia. Cancer data analytics.
        </Typography>
        <Typography paragraph>Universidad del Valle</Typography>
      </Box>
    </>
  );
};
