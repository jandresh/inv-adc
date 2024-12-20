import React, { useEffect, useState } from 'react';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { query } from 'utils/queries';
import { Collections } from '../Collections';
import { Typography } from '@mui/material';

export const Databases: React.FC = () => {
  const columns: GridColDef[] = [
    { field: 'database', headerName: 'Database', flex: 100 }
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
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      <DataGrid
        rows={rows}
        columns={columns}
        getRowId={(row) => row.database}
        getRowHeight={() => 'auto'}
        initialState={
          {
            pagination: {
              paginationModel: { pageSize: 10 }
            }
          }
        }
        pageSizeOptions={[10, 50, 100]}
        onRowSelectionModelChange={(ids) => {
          setDatabase(ids.length > 0 ? ids[0].toString() : '');
        }}
      />
      <Typography variant="h4">Collections</Typography>
      {database === '' ? undefined : <Collections database={database} />}
    </div>
  );
};
