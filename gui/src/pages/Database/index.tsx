import { Typography } from '@mui/material';
import React, { useContext, useEffect, useState } from 'react';
import { Helmet } from 'react-helmet';
import { AppContext } from '../../contexts';
import { APP_TITLE, PAGE_TITLE_HOME } from '../../utils/constants';
import type { Patterns } from '../../types';
import { DataGrid, GridColDef } from '@mui/x-data-grid';

export const Database = () => {
  const context = useContext(AppContext);

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', flex: 10 },
    { field: 'patternid', headerName: 'Pattern Id', flex: 10 },
    { field: 'db', headerName: 'Database', flex: 10 },
    {
      field: 'description',
      headerName: 'Description',
      flex: 10,
      resizable: true
    },
    { field: 'pattern', headerName: 'Query', flex: 100, resizable: true }
  ];

  const [patterns, setPatterns] = useState<Array<Patterns>>([]);

  useEffect(() => {
    const fetchPatterns = async(): Promise<Array<Patterns>> => {
      return await fetch('http://34.74.92.5:5000/patterns', {
        method: 'GET'
      }).then((response) => response.json());
    };
    fetchPatterns().then((response) => {
      setPatterns(response);
    });
  }, []);

  return (
    <>
      <Helmet>
        <title>
          {PAGE_TITLE_HOME} | {APP_TITLE}
        </title>
      </Helmet>
      <Typography variant="h4">{`Hello, ${context.user.name}`}</Typography>
      <DataGrid rows={patterns} columns={columns} autoHeight={true} />
    </>
  );
};
