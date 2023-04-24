import React, { useCallback, useState } from 'react';
import { Formik, Form, Field } from 'formik';
import { TextField } from 'formik-mui';
import { Button, LinearProgress, Stack } from '@mui/material';
import { query } from 'utils/queries';
import type { IAccess } from 'pages/Home';
import Snackbar from '@mui/material/Snackbar';
import MuiAlert, { AlertProps } from '@mui/material/Alert';
import * as Yup from 'yup';
import { Buffer } from 'buffer';

interface IRegister {
  firstName: string;
  lastName: string;
  org: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export const Register: React.FC<{
  setAccess: React.Dispatch<React.SetStateAction<IAccess['access']>>;
}> = ({ setAccess }) => {
  const initialValues: IRegister = {
    firstName: '',
    lastName: '',
    org: '',
    email: '',
    password: '',
    confirmPassword: ''
  };

  const [findEmailResponse, setFindEmailResponse] = useState<
    Record<string, any>[]
  >([]);
  const [findOrgIdResponse, setFindOrgIdResponse] = useState<
    Record<string, any>[]
  >([]);
  const [response, setResponse] = useState<Record<string, any>[]>([
    { exit: 1 }
  ]);
  const [open, setOpen] = useState(false);
  const [orgExist, setOrgExist] = useState({ exist: false, name: '' });
  const handleSubmit = useCallback(
    async (values: IRegister): Promise<void> => {
      const findEmailDocument = {
        'db_name': 'global',
        'coll_name': 'users',
        'query': {
          'email': values.email
        },
        'projection': {
          'email': 1
        }
      };
      const findOrgIdDocument = {
        'db_name': 'global',
        'coll_name': 'users',
        'query': {
          'org_id': values.email.split('@')[1]
        },
        'projection': {
          'email': 1,
          'org':1
        }
      };
      const findEmailResult = await query(
        'findDocument',
        setFindEmailResponse,
        findEmailDocument
      );
      const {
        success: successEmailFind,
        responseObj: responseEmailFind
      } = findEmailResult;
      const findOrgIdResult = await query(
        'findDocument',
        setFindOrgIdResponse,
        findOrgIdDocument
      );
      const {
        success: successOrgIdFind,
        responseObj: responseOrgIdFind
      } = findOrgIdResult;
      setOrgExist({
        exist: (
          (successOrgIdFind ? true : false) &&
          responseOrgIdFind.length > 0 &&
          (findOrgIdResponse ? true : false)
        ),
        name: findOrgIdResponse && responseOrgIdFind.length > 0
          ? findOrgIdResponse[0]['org']
          : ''
      });
      const registerDocument = {
        'db_name': 'global',
        'coll_name': 'users',
        document: {
          'first_name': values.firstName,
          'last_name': values.lastName,
          'org': orgExist.exist ? orgExist.name : values.org,
          'org_id': values.email.split('@')[1],
          'email': values.email,
          'password': Buffer.from(values.password, 'binary').toString('base64'),
          'created': new Date(),
          'updated': new Date(),
          'is_admin': true,
          'is_active': values.email === 'admin@adccali.com' ? true : false,
          'is_verified': false
        }
      };
      if (
        successEmailFind &&
        responseEmailFind.length === 0 &&
        findEmailResponse &&
        values.email !== 'admin@adccali.com'
      ) {
        const registerResult = await query(
          'createDocument',
          setResponse,
          registerDocument
        );
        const { success: successRegister } = registerResult;
        if (!successRegister) {
          setResponse([{ exit: 1 }]);
        }
      } else if (responseEmailFind.length === 0) {
        setResponse([{ exit: 1 }]);
      } else {
        setResponse([{ exit: 2 }]);
      }
      setOpen(true);
    },
    [findEmailResponse, findOrgIdResponse, orgExist, setOpen, setResponse]
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

    setOpen(false);
    if (response[0]['exit'] !== 2) {
      setAccess('GUEST');
    }
  };

  const Alert = React.forwardRef<HTMLDivElement, AlertProps>(function Alert (
    props,
    ref
  ) {
    return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
  });

  const validationSchema = Yup.object().shape({
    firstName: Yup.string().required('First Name is required').max(100).min(2),
    lastName: Yup.string().required('Last Name is required').max(100).min(2),
    org: Yup.string()
      .required('Institution is required')
      .max(100)
      .min(2),
    email: Yup.string().required('email is required').email(),
    password: Yup.string().required('Password is required').min(4).max(20),
    confirmPassword: Yup.string()
      .required('Password confirmation is required')
      .min(2)
      .max(20)
      .oneOf([Yup.ref('password'), null], 'Passwords not match')
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
              name="firstName"
              type="name"
              label="First Name"
              disabled={open}
            />
            <Field
              component={TextField}
              name="lastName"
              type="name"
              label="Last Name"
              disabled={open}
            />
            <Field
              component={TextField}
              name="org"
              type="name"
              label="Organization"
              disabled={open}
            />
            <Field
              component={TextField}
              name="email"
              type="email"
              label="Email"
              disabled={open}
            />
            <Field
              component={TextField}
              type="password"
              label="Password"
              name="password"
              disabled={open}
            />
            <Field
              component={TextField}
              type="password"
              label="Confirm Password"
              name="confirmPassword"
              disabled={open}
            />
            {isSubmitting && <LinearProgress />}
            <Button
              variant="contained"
              color="primary"
              disabled={isSubmitting || open}
              onClick={submitForm}
            >
              Submit
            </Button>
            <Button variant="text" disabled={open} onClick={onCancel}>
              Cancel
            </Button>
            <Snackbar
              anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
              open={open}
              autoHideDuration={20000}
              onClose={handleClose}
            >
              {response[0]['exit'] === 0 ? (
                <Alert
                  onClose={handleClose}
                  severity="success"
                  sx={{ width: '100%' }}
                >
                  Your registration was successful. To access the system you
                  must wait for an administrator to authorize and activate your
                  account!
                  {
                    orgExist.exist && '\nNote: As your domain was registered ' +
                    `previously, you have added to the ${orgExist.name} ` +
                    'organization.'
                  }
                </Alert>
              ) : response[0]['exit'] === 2 ? (
                <Alert
                  onClose={handleClose}
                  severity="error"
                  sx={{ width: '100%' }}
                >
                  Your registration was unsuccess. your email is already
                  registered!
                </Alert>
              ) : (
                <Alert
                  onClose={handleClose}
                  severity="error"
                  sx={{ width: '100%' }}
                >
                  Your registration was unsuccess. Please try again latter!
                </Alert>
              )}
            </Snackbar>
          </Stack>
        </Form>
      )}
    </Formik>
  );
};
