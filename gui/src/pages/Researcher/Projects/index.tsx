import { Typography } from '@mui/material';
import React from 'react';
import { Helmet } from 'react-helmet';
import { APP_TITLE, PAGE_TITLE_HOME } from 'utils/constants';
import { ProjectsTable } from './ProjectsTable';
import { AddForm } from './AddForm';

export const Projects = () => {
  return (
    <>
      <Helmet>
        <title>
          {PAGE_TITLE_HOME} | {APP_TITLE}
        </title>
      </Helmet>
      <Typography variant="h4">Projects</Typography>
      <ProjectsTable />
      <Typography variant="h4">Add Project</Typography>
      <AddForm />
    </>
  );
};
