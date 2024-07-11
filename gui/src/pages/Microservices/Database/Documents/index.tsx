import React, { useEffect, useState } from 'react';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { query } from 'utils/queries';

export const Documents: React.FC<{ database: string, collection: string }> = (
  { database, collection }
) => {
  const [documents, setDocuments] = useState<Record<string, string>[]>(
    []
  );
  const columns = documents && documents.length > 0
    ? (Object.keys(documents[0])).map((key: string): GridColDef => {
      return {
        field: key,
        headerName: key
      };
    })
    : [];

  useEffect(() => {
    if (collection) {
      query(
        'listDocuments',
        setDocuments,
        { 'db_name': database, 'coll_name': collection }
      );
    }
  }, [collection, database]);

  if (!documents) {
    return <div></div>;
  }

  return (
    <DataGrid
      rows={documents ? documents : []}
      columns={columns}
      getRowId={(row) => row._id}
      autoHeight
      pageSizeOptions={[10, 50, 100]}
    />
  );
};
