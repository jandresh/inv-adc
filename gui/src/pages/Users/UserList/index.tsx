import React, { useEffect, useState } from 'react';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import { query } from 'utils/queries';

const document = {
  'db_name': 'global',
  'coll_name': 'users'
};

export const UserList: React.FC = () => {
  const columns: GridColDef[] = [
    { field: 'org', headerName: 'Organization', flex: 100 },
    { field: 'user', headerName: 'User', flex: 100 },
    { field: 'name', headerName: 'Name', flex: 100 },
    { field: 'isActive', headerName: 'Is active', flex: 100 },
    { field: 'isAdmin', headerName: 'R&D', flex: 100 }
  ];
  const [users, setUsers] = useState<Record<string, string[]>[]>([]);
  const [user, setUser] = useState<Record<string, string[]>>({});

  function dialogContentOptions (user: string, org: string): any {
    return {
      activate: {
        accept: 'Activate',
        content: `If you press on activate, the user ${user} will be` +
          ` activated and the organization ${org}, will be created.`,
        reject: 'Cancel',
        title: `Do you want to active user ${user}?:`
      },
      deactivate: {
        accept: 'Deactivate',
        content: `If you press on deactivate, the user ${user} will be` +
          ` unable to access and the organization ${org} remains in standby.`,
        reject: 'Cancel',
        title: `Do you want to disable user ${user}?:`
      },
      researcher: {
        accept: 'Proceed',
        content: 'If you proceed, the researcher role will be assigned to' +
          ' the user.',
        reject: 'Cancel',
        title: `Do you want to assign researcher role to ${user}?:`
      },
      user: {
        accept: 'Proceed',
        content: 'If you proceed, the user role will be assigned to the ' +
          'user.',
        reject: 'Cancel',
        title: `Do you want to assign user role to ${user}?:`
      }
    };
  }

  const [dialogContent, setDialogContent] = useState({
    accept: '',
    content: '',
    reject: '',
    title: ''
  });

  const [isAdminModalOpen, setIsAdminModalOpen] = useState(false);
  const [isActiveModalOpen, setIsActiveModalOpen] = useState(false);
  const [email, setEmail] = useState('');

  const handleActiveAccept = () => {
    const activateDocument = {
      'db_name': 'global',
      'coll_name': 'users',
      'filter': { 'email': email },
      'document': { 'is_active': !user['is_active'] } };
    query('updateDocument', undefined, activateDocument);
    setIsActiveModalOpen(false);
    query('listDocuments', setUsers, document);
  };
  const handleAdminAccept = () => {
    const activateDocument = {
      'db_name': 'global',
      'coll_name': 'users',
      'filter': { 'email': email },
      'document': { 'is_admin': !user['is_admin'] } };
    query('updateDocument', undefined, activateDocument);
    setIsAdminModalOpen(false);
    query('listDocuments', setUsers, document);
  };
  const handleClose = () => {
    setIsActiveModalOpen(false);
    setIsAdminModalOpen(false);
  };

  const handleOnCellClick = (params: any) => {
    setEmail(params.row.user);
    setUser(users.filter((user): boolean => {
      return user['email'] === params.row.user;
    })[0]);
    if (params.colDef.field === 'isActive') {
      setDialogContent(
        dialogContentOptions(params.row.user, params.row.org)[
          params.row.isActive ? 'deactivate' : 'activate'
        ]
      );
      setIsActiveModalOpen(true);
    }
    if (params.colDef.field === 'isAdmin') {
      setDialogContent(
        dialogContentOptions(params.row.user, params.row.org)[
          params.row.isActive ? 'user' : 'researcher']
      );
      setIsAdminModalOpen(true);
    }
  };

  useEffect((): void => {
    const getUsers: () => Promise<void> = async () => {
      await query('listDocuments', setUsers, document);
    };
    getUsers();
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
        open={isActiveModalOpen}
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
          <Button onClick={handleActiveAccept}>{dialogContent.accept}</Button>
        </DialogActions>
      </Dialog>
      <Dialog
        open={isAdminModalOpen}
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
          <Button onClick={handleAdminAccept}>{dialogContent.accept}</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};
