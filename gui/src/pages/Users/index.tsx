import { Typography } from '@mui/material';
import React from 'react';
import { Helmet } from 'react-helmet';
import { APP_TITLE, PAGE_TITLE_HOME } from '../../utils/constants';
import { UserList } from './UserList';

export const Users = () => {
  return (
    <>
      <Helmet>
        <title>
          {PAGE_TITLE_HOME} | {APP_TITLE}
        </title>
      </Helmet>
      <Typography variant="h4">Users</Typography>
      <UserList />
    </>
  );
};
