import React, { useEffect, useState } from 'react';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { query } from 'utils/queries';

export const Patterns = () => {

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

  const [patterns, setPatterns] = useState<Record<string, string>[]>([]);

  useEffect(() => {
    query('getPatterns', setPatterns);
  }, []);

  return (
    <DataGrid
      rows={patterns}
      columns={columns}
      autoHeight={true}
      initialState={ { pagination: { pageSize: 10 } } }
      rowsPerPageOptions={[10, 50, 100]}
    />
  );
};
