import { Button, Stack, Typography } from '@mui/material';
import React, { useContext } from 'react';
import { Helmet } from 'react-helmet';

import { AppContext } from '../../contexts';
import { APP_TITLE, PAGE_TITLE_HOME } from '../../utils/constants';

export const Home = () => {
  const context = useContext(AppContext);

  return (
    <>
      <Helmet>
        <title>
          {PAGE_TITLE_HOME} | {APP_TITLE}z
        </title>
      </Helmet>
      <Stack spacing={2}>
        <Typography variant="h4">{`Hello, ${context.user.name}`}</Typography>
        <Button variant="contained">Login</Button>
        <Button variant="outlined">Register</Button>
      </Stack>
    </>
  );
};
