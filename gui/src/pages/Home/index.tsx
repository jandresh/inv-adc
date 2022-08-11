import { Button, Stack, Typography } from '@mui/material';
import React, { useContext, useState } from 'react';
import { Helmet } from 'react-helmet';
import { AppContext } from '../../contexts';
import { APP_TITLE, PAGE_TITLE_HOME } from '../../utils/constants';
import { Register } from 'components/Register';

interface IAccess {
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
        <Typography variant="h4">{`Hello, ${context.user.name}`}</Typography>
        {access === 'GUEST' && (
          <React.Fragment>
            <Button variant="contained" onClick={loginClick} >Login</Button>
            <Button variant="outlined" onClick={registerClick}>Register</Button>
          </React.Fragment>)}
        {access === 'REGISTER' && <Register/>}
      </Stack>
    </>
  );
};
