import React, { useEffect, useContext, useState } from 'react';
import { AppContext } from 'contexts';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { query } from 'utils/queries';

export const ProjectsTable = () => {
  const context = useContext(AppContext);
  const columns: GridColDef[] = [
    { field: '_id', headerName: 'ID', flex: 10 },
    { field: 'name', headerName: 'Project Name', flex: 10 },
    {
      field: 'description',
      headerName: 'Description',
      flex: 10
    },
    { field: 'maxDocs', headerName: 'Max Docs', flex: 10 },
    { field: 'status', headerName: 'Status', flex: 10 }
  ];

  const [projects, setProjects] = useState<Record<string, string>[]>([]);

  useEffect(() => {
    query(
      'listDocuments',
      setProjects,
      { 'db_name': context.user.orgId.split('.')[0], 'coll_name': 'projects' }
    );
  }, [context]);

  return (
    <DataGrid
      rows={projects}
      getRowId={(row) => row._id}
      getRowHeight={() => 'auto'}
      columns={columns}
      autoHeight={true}
      initialState={
        {
          pagination: {
            paginationModel: { pageSize: 10 }
          }
        }
      }
      pageSizeOptions={[10, 50, 100]}
    />
  );
};
