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
      flex: 100
    }
  ];

  const [collection, setCollection] = useState('');
  const [collections, setCollections] = useState<Record<string, string[]>[]>(
    []
  );

  useEffect(() => {
    const getCollections: () => Promise<void> = async () => {
      await query('listCollections', setCollections, { 'db_name': database });
    };
    getCollections();
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
        getRowHeight={() => 'auto'}
        initialState={
          {
            pagination: {
              paginationModel: { pageSize: 10 }
            }
          }
        }
        onRowSelectionModelChange={(ids) => {
          setCollection(ids.length > 0 ? ids[0].toString() : '');
        }}
        pageSizeOptions={[10, 50, 100]}
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
