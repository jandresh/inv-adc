import { Button, Stack, Typography } from '@mui/material';
import React, { useContext, useState } from 'react';
import { Helmet } from 'react-helmet';
import { AppContext } from '../../contexts';
import { APP_TITLE, PAGE_TITLE_HOME } from '../../utils/constants';
import { Register } from 'components/Register';
import { Login } from 'components/Login';

export interface IAccess {
  access: 'GUEST' | 'REGISTER' | 'LOGIN' | 'LOGGED';
}

export const Home = () => {
  const context = useContext(AppContext);
  const [access, setAccess] = useState<IAccess['access']>('GUEST');
  const loginClick = ()=>{
    setAccess('LOGIN');
  };
  const registerClick = ()=>{
    setAccess('REGISTER');
  };

  return (
    <>
      <Helmet>
        <title>
          {PAGE_TITLE_HOME} | {APP_TITLE}
        </title>
      </Helmet>
      <Stack spacing={2}>
        {access === 'GUEST' && (
          <React.Fragment>
            <Typography variant="h4">Welcome</Typography>
            <Button variant="contained" onClick={loginClick} >Login</Button>
            <Button variant="outlined" onClick={registerClick}>Register</Button>
          </React.Fragment>)}
        {access === 'REGISTER' && (
          <React.Fragment>
            <Typography variant="h4">Registration</Typography>
            <Register setAccess={setAccess}/>
          </React.Fragment>
        )}
        {access === 'LOGIN' && (
          <React.Fragment>
            <Typography variant="h4">Login</Typography>
            <Login setAccess={setAccess}/>
          </React.Fragment>
        )}
        {access === 'LOGGED' && (
          <React.Fragment>
            <Typography variant="h3">
              {`${context.user.firstName} ${context.user.lastName}`}
            </Typography>
            <Typography variant="h4">{`UserId: ${context.user.id}`}</Typography>
            <Typography variant="h4">{`email: ${context.user.email}`}</Typography>
            <Typography variant="h4">{`CreatedAt: ${context.user.createdAt}`}</Typography>
            <Typography variant="h4">{`UpdatedAt: ${context.user.updatedAt}`}</Typography>
            <Typography variant="h4">{`IsAdmin: ${context.user.isAdmin}`}</Typography>
            <Typography variant="h4">{`IsActive: ${context.user.isActive}`}</Typography>
            <Typography variant="h4">{`IsVerified: ${context.user.isVerified}`}</Typography>
          </React.Fragment>
        )}
      </Stack>
    </>
  );
};
