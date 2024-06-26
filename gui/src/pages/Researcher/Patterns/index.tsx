import { Typography } from '@mui/material';
import React from 'react';
import { Helmet } from 'react-helmet';
import { APP_TITLE, PAGE_TITLE_HOME } from 'utils/constants';
import { PatternsTable } from './PatternsTable';
import { AddForm } from './AddForm';
import { AddFileForm } from './AddFileForm';

export const Patterns = () => {
  return (
    <>
      <Helmet>
        <title>
          {PAGE_TITLE_HOME} | {APP_TITLE}
        </title>
      </Helmet>
      <Typography variant="h4">Patterns</Typography>
      <Typography variant="h5">Select Project</Typography>
      <PatternsTable />
      <Typography variant="h4">Add Pattern</Typography>
      <AddForm />
      <Typography variant="h4">Add Patterns File</Typography>
      <AddFileForm />
    </>
  );
};
