import React, { useEffect, useState } from 'react';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import { query } from 'utils/queries';

export const UserList: React.FC = () => {
  const columns: GridColDef[] = [
    { field: 'org', headerName: 'Organization', flex: 100 },
    { field: 'user', headerName: 'User', flex: 100 },
    { field: 'name', headerName: 'Name', flex: 100 },
    { field: 'isActive', headerName: 'Is active', flex: 100 },
    { field: 'isAdmin', headerName: 'R&D', flex: 100 }
  ];
  const [users, setUsers] = useState<Record<string, string[]>[]>([]);

  const document = {
    'db_name': 'global',
    'coll_name': 'users'
  };

  function dialogContentOptions (user: string, org: string): any {
    return {
      activate: {
        accept: 'Activate',
        content: `If your agree, the user ${user} will be activated an the` +
          `organization ${org}, will be created in database.`,
        reject: 'Cancel',
        title: `Do you want to active user ${user}?:`
      },
      deactivate: {
        accept: 'Deactivate',
        content: '',
        reject: 'Cancel',
        title: ''
      },
      researcher: {
        accept: 'Proceed',
        content: 'Proceed',
        reject: 'Cancel',
        title: ''
      },
      user: {
        accept: 'Proceed',
        content: 'Proceed',
        reject: 'Cancel',
        title: ''
      }
    };
  }

  const [dialogContent, setDialogContent] = useState({
    accept: '',
    content: '',
    reject: '',
    title: ''
  });

  const [open, setOpen] = useState(false);
  const [email, setEmail] = useState('');

  const handleClose = () => {
    const activateDocument = {
      'db_name': 'global',
      'coll_name': 'users',
      'filter': { 'email': email },
      'document': { 'is_active': true } };
    query('updateDocument', undefined, activateDocument);
    setOpen(false);
  };

  const handleOnCellClick = (params: any) => {
    setEmail(params.row.user);
    if (params.colDef.field === 'isActive') {
      setDialogContent(
        dialogContentOptions(params.row.user, params.row.org)['activate']
      );
      setOpen(true);
      // eslint-disable-next-line
      console.log(params);
    }
    if (params.colDef.field === 'isAdmin') {
      setOpen(true);
      // eslint-disable-next-line
      console.log(params);
    }
  };

  useEffect(() => {
    query('listDocuments', setUsers, document);
  }, []);

  if (!users) {
    return <div></div>;
  }

  const rows = users[0]
    ? users.map((user: any): Record<string, string> => {
      return {
        org: user['org'],
        user: user['email'],
        name: `${user['last_name']}, ${user['first_name']}`,
        isActive: user['is_active'],
        isAdmin: user['is_admin']
      };
    })
    : [];

  return (
    <>
      <DataGrid
        rows={rows}
        columns={columns}
        autoHeight={true}
        getRowId={(row) => row.user}
        initialState={{ pagination: { pageSize: 10 } }}
        onCellClick={handleOnCellClick}
        rowsPerPageOptions={[10, 50, 100]}
      />
      <Dialog
        open={open}
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
          <Button onClick={handleClose}>{dialogContent.accept}</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};
