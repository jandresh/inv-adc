import { Typography } from '@mui/material';
import React from 'react';
import { Helmet } from 'react-helmet';
import { APP_TITLE, PAGE_TITLE_HOME } from '../../utils/constants';
import { Patterns } from './Patterns';
import { DbList } from './DbList';

export const Database = () => {
  return (
    <>
      <Helmet>
        <title>
          {PAGE_TITLE_HOME} | {APP_TITLE}
        </title>
      </Helmet>
      <Typography variant="h4">Patterns</Typography>
      <Patterns />
      <Typography variant="h4">Databases</Typography>
      <DbList />
    </>
  );
};
