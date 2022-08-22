import React, { useEffect, useState } from 'react';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { query } from 'utils/queries';

export const CollList: React.FC<{ database: string }> = ({ database }) => {
  const columns: GridColDef[] = [
    {
      field: 'collection',
      headerName: 'Collection',
      flex: 100,
      resizable: true
    }
  ];

  const [collections, setCollections] = useState<Record<string, string[]>[]>(
    []
  );

  useEffect(() => {
    query('listCollections', setCollections, { db_name: database });
  }, []);

  if (!collections) {
    return <div></div>;
  }

  return (
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
      rowsPerPageOptions={[10, 50, 100]}
    />
  );
};
