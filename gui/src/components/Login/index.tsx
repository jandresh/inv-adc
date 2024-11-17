import React, { useCallback, useContext, useState } from 'react';
import { Formik, Form, Field } from 'formik';
import { TextField } from 'formik-mui';
import { Button, LinearProgress, Stack } from '@mui/material';
import { query } from 'utils/queries';
import type { IAccess } from 'pages/Home';
import Snackbar from '@mui/material/Snackbar';
import MuiAlert, { AlertProps } from '@mui/material/Alert';
import * as Yup from 'yup';
import { AppContext } from 'contexts';
import { Buffer } from 'buffer';
import { User } from 'types';

interface ILogin {
  email: string;
  password: string;
}

export const Login: React.FC<{
  setAccess: React.Dispatch<React.SetStateAction<IAccess['access']>>;
}> = ({ setAccess }) => {
  const initialValues: ILogin = {
    email: '',
    password: ''
  };

  const [response, setResponse] = useState<Record<string, any>[]>([]);
  const [open, setOpen] = useState([false, false]);
  const context = useContext(AppContext);

  const handleSubmit = useCallback(
    async (values: ILogin): Promise<void> => {
      const document = {
        'db_name': 'global',
        'coll_name': 'users',
        'query': {
          'email': values.email,
          'password': Buffer.from(values.password, 'binary').toString('base64')
        },
        'projection': {
          'org_id': 1,
          'first_name': 1,
          'last_name': 1,
          'email': 1,
          'created': 1,
          'updated': 1,
          'is_admin': 1,
          'is_active': 1,
          'is_verified': 1
        }
      };
      const { success, responseObj } = await query(
        'findDocument',
        setResponse,
        document
      );
      if (
        success &&
        responseObj.length > 0 &&
        response &&
        responseObj[0]['is_active']
      ) {
        const userData: User = {
          id: responseObj[0]['_id'],
          orgId: responseObj[0]['org_id'],
          firstName: responseObj[0]['first_name'],
          lastName: responseObj[0]['last_name'],
          email: responseObj[0]['email'],
          createdAt: responseObj[0]['created'],
          updatedAt: responseObj[0]['updated'],
          isActive: responseObj[0]['is_active'],
          isAdmin: responseObj[0]['is_admin'],
          isVerified: responseObj[0]['is_verified'],
          role: responseObj[0]['is_admin'] ? 'researcher' : 'user'
        };
        context.setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
        setAccess('LOGGED');
      } else if (
        success &&
        values.email === 'admin@adccali.com' &&
        values.password === 'admin'
      ) {
        const adminData: User = {
          id: '',
          orgId: 'adc-cali',
          firstName: 'Admin',
          lastName: 'adc Cali',
          email: 'admin@adccali.com',
          createdAt: new Date(),
          updatedAt: new Date(),
          isActive: true,
          isAdmin: true,
          isVerified: false,
          role: 'admin'
        };
        context.setUser(adminData);
        localStorage.setItem('user', JSON.stringify(adminData));
        setAccess('LOGGED');
      } else {
        setOpen([true, success]);
      }
    },
    [context, response, setAccess, setOpen]
  );

  const onCancel = () => {
    setAccess('GUEST');
  };

  const handleClose = (
    event?: React.SyntheticEvent | Event,
    reason?: string
  ) => {
    if (reason === 'clickaway') {
      return;
    }

    setOpen([false, false]);
  };

  const Alert = React.forwardRef<HTMLDivElement, AlertProps>(function Alert (
    props,
    ref
  ) {
    return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
  });

  const validationSchema = Yup.object().shape({
    email: Yup.string().required('email is required').email(),
    password: Yup.string().required('Password is required').min(4).max(20)
  });

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={handleSubmit}
      validationSchema={validationSchema}
    >
      {({ submitForm, isSubmitting }) => (
        <Form>
          <Stack spacing={2}>
            <Field
              component={TextField}
              name="email"
              type="email"
              label="Email"
              disabled={open[0]}
            />
            <Field
              component={TextField}
              type="password"
              label="Password"
              name="password"
              disabled={open[0]}
            />
            {isSubmitting && <LinearProgress />}
            <Button
              variant="contained"
              color="primary"
              disabled={isSubmitting || open[0]}
              onClick={submitForm}
            >
              Submit
            </Button>
            <Button variant="text" disabled={open[0]} onClick={onCancel}>
              Cancel
            </Button>
            <Snackbar
              anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
              open={open[0]}
              autoHideDuration={20000}
              onClose={handleClose}
            >
              {open[1] ? (
                <Alert
                  onClose={handleClose}
                  severity="error"
                  sx={{ width: '100%' }}
                >
                  User is inactive or provided email/password are invalid!
                </Alert>
              ) : (
                <Alert
                  onClose={handleClose}
                  severity="error"
                  sx={{ width: '100%' }}
                >
                  Server error, please try again latter!
                </Alert>
              )}
            </Snackbar>
          </Stack>
        </Form>
      )}
    </Formik>
  );
};
