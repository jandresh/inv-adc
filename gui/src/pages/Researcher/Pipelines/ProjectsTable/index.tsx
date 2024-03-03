import React, { useEffect, useContext, useState } from 'react';
import { AppContext } from 'contexts';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { query } from 'utils/queries';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';

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
  const [project, setProject] = useState<string>('');
  const [dialogContent, setDialogContent] = useState({
    accept: '',
    content: '',
    reject: '',
    title: ''
  });
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleRunPipeline = async () => {
    const pipelineDocument = {
      'organization': context.user.orgId.split('.')[0],
      'project': project
    };
    await query('runMetadataPipeline', undefined, pipelineDocument);
    setIsModalOpen(false);
    await query(
      'listDocuments',
      setProjects,
      { 'db_name': context.user.orgId.split('.')[0], 'coll_name': 'projects' }
    );
  };
  const handleClose = () => {
    setIsModalOpen(false);
  };
  const handleOnCellClick = (params: any) => {
    setProject(params.row.name);
    if (params.colDef.field === 'status') {
      setDialogContent({
        accept: 'Run Pipeline',
        content: `If you press on Run Pipeline, the project ${params.row.name} will be` +
          ' executed.',
        reject: 'Cancel',
        title: `Do you want to run ${params.row.name} project?:`
      }
      );
      setIsModalOpen(true);
    }
  };

  useEffect(() => {
    query(
      'listDocuments',
      setProjects,
      { 'db_name': context.user.orgId.split('.')[0], 'coll_name': 'projects' }
    );
  }, [context]);

  return (
    <>
      <DataGrid
        rows={projects}
        getRowId={(row) => row._id}
        columns={columns}
        autoHeight={true}
        initialState={{ pagination: { pageSize: 10 } }}
        onCellClick={handleOnCellClick}
        rowsPerPageOptions={[10, 50, 100]}
      />
      <Dialog
        open={isModalOpen}
        onClose={handleClose}
        aria-labelledby='alert-dialog-title'
        aria-describedby='alert-dialog-description'
      >
        <DialogTitle id='alert-dialog-title'>
          {dialogContent.title}
        </DialogTitle>
        <DialogContent>
          <DialogContentText id='alert-dialog-description'>
            {dialogContent.content}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>{dialogContent.reject}</Button>
          <Button onClick={handleRunPipeline}>{dialogContent.accept}</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};
