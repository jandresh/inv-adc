import React, { useEffect, useState } from 'react';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { query } from 'utils/queries';
import { CollList } from '../CollList';
import { Typography } from '@mui/material';

export const DbList: React.FC = () => {
  const columns: GridColDef[] = [
    { field: 'database', headerName: 'Database', flex: 100, resizable: true }
  ];
  const [database, setDatabase] = useState('');
  const [databases, setDatabases] = useState<Record<string, string[]>[]>([]);

  useEffect(() => {
    query('listDatabases', setDatabases);
  }, []);

  if (!databases) {
    return <div></div>;
  }

  const rows = databases[0]
    ? databases[0]['databases'].map((db: string): Record<string, string> => {
        return { database: db };
      })
    : [];

  return (
    <>
      <DataGrid
        rows={rows}
        columns={columns}
        autoHeight={true}
        getRowId={(row) => row.database}
        initialState={{ pagination: { pageSize: 10 } }}
        rowsPerPageOptions={[10, 50, 100]}
        onSelectionModelChange={(ids) => {
          setDatabase('');
          setDatabase(ids[0].toString());
        }}
      />
      <Typography variant="h4">Collections</Typography>
      {database === '' ? undefined : <CollList database={database} />}
    </>
  );
};
