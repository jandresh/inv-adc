import React, { useEffect, useContext, useState } from 'react';
import { AppContext } from 'contexts';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { query } from 'utils/queries';
import { ProjectSelector } from './ProjectSelector';

export const PatternsTable = () => {
  const context = useContext(AppContext);
  const columns: GridColDef[] = [
    { field: '_id', headerName: 'ID', flex: 10 },
    { field: 'pattern', headerName: 'Pattern', flex: 10 }
  ];

  const [project, setProject] = useState<string>('');
  const [projects, setProjects] = useState<Record<string, string>[]>([]);

  useEffect(() => {
    query(
      'listDocuments',
      setProjects,
      { 'db_name': context.user.orgId.split('.')[0], 'coll_name': `patterns#${project}` }
    );
  }, [context, project]);

  return (
    <>
      <ProjectSelector setProject={setProject}/>
      <DataGrid
        rows={projects}
        getRowId={(row) => row._id}
        columns={columns}
        autoHeight={true}
        initialState={{ pagination: { pageSize: 10 } }}
        rowsPerPageOptions={[10, 50, 100]}
      />
    </>
  );
};
