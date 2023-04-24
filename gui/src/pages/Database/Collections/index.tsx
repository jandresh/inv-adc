import React, { useEffect, useState } from 'react';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { query } from 'utils/queries';
import { Documents } from '../Documents';
import { Typography } from '@mui/material';

export const Collections: React.FC<{ database: string }> = ({ database }) => {
  const columns: GridColDef[] = [
    {
      field: 'collection',
      headerName: 'Collection',
      flex: 100,
      resizable: true
    }
  ];

  const [collection, setCollection] = useState('');
  const [collections, setCollections] = useState<Record<string, string[]>[]>(
    []
  );

  useEffect(() => {
    query('listCollections', setCollections, { 'db_name': database });
  }, [database]);

  if (!collections) {
    return <div></div>;
  }

  return (
    <>
      <DataGrid
        rows={
          collections[0]
            ? collections[0]['collections'].map(
              (coll: string): Record<string, string> => {
                return { collection: coll };
              }
            )
            : []
        }
        columns={columns}
        autoHeight={true}
        getRowId={(row) => row.collection}
        initialState={{ pagination: { pageSize: 10 } }}
        onSelectionModelChange={(ids) => {
          setCollection(ids.length > 0 ? ids[0].toString() : '');
        }}
        rowsPerPageOptions={[10, 50, 100]}
      />
      <Typography variant="h4">Documents</Typography>
      {database === '' || collection === ''
        ? undefined
        : <Documents
          database={database}
          collection={collection}
        />}
    </>
  );
};
