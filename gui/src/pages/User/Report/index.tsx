import { Grid } from '@mui/material';
import React from 'react';
import { Helmet } from 'react-helmet';
import { APP_TITLE, PAGE_TITLE_HOME } from 'utils/constants';
import { NetworkSelector } from './NetworkSelector';

export const Report = () => {
  return (
    <>
      <Helmet>
        <title>
          {PAGE_TITLE_HOME} | {APP_TITLE}
        </title>
      </Helmet>
      <Grid container spacing={2} gap={2}>
        <NetworkSelector />
      </Grid>
    </>
  );
};
