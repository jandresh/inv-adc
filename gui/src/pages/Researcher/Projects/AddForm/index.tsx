import React, { useCallback, useContext, useState } from 'react';
import { AppContext } from 'contexts';
import { Formik, Form, Field } from 'formik';
import { TextField } from 'formik-mui';
import { Button, LinearProgress, Stack, Typography } from '@mui/material';
import { query } from 'utils/queries';
import Snackbar from '@mui/material/Snackbar';
import MuiAlert, { AlertProps } from '@mui/material/Alert';
import * as Yup from 'yup';

interface IProjectsForm {
  name: string;
  description: string;
  maxDocs: number;
  status: string;
}

export const AddForm = () => {
  const context = useContext(AppContext);
  const initialValues: IProjectsForm = {
    name: '',
    description: '',
    maxDocs: 50,
    status: 'Created'
  };
  const [findProjectResponse, setFindProjectResponse] = useState<
    Record<string, any>[]
  >([]);
  const [response, setResponse] = useState<Record<string, any>[]>([
    { exit: 1 }
  ]);
  const [open, setOpen] = useState(false);
  const handleSubmit = useCallback(
    async (values: IProjectsForm): Promise<void> => {
      const findProjectDocument = {
        'db_name': context.user.orgId.split('.')[0],
        'coll_name': 'projects',
        'query': {
          'name': values.name
        },
        'projection': {
          'name': 1
        }
      };
      const findProjectResult = await query(
        'findDocument',
        setFindProjectResponse,
        findProjectDocument
      );
      const {
        success: successProjectFind,
        responseObj: responseProjectFind
      } = findProjectResult;
      const registerDocument = {
        'db_name': context.user.orgId.split('.')[0],
        'coll_name': 'projects',
        document: {
          'name': values.name,
          'description': values.description,
          'maxDocs': Number(values.maxDocs),
          'status': values.status
        }
      };
      if (
        successProjectFind &&
        responseProjectFind.length === 0 &&
        findProjectResponse
      ) {
        const addProjectResult = await query(
          'createDocument',
          setResponse,
          registerDocument
        );
        const { success: successRegister } = addProjectResult;
        if (!successRegister) {
          setResponse([{ exit: 1 }]);
        }
      } else {
        setResponse([{ exit: 2 }]);
      }
      setOpen(true);
    },
    [context, findProjectResponse, setOpen, setResponse]
  );

  const handleClose = (
    event?: React.SyntheticEvent | Event,
    reason?: string
  ) => {
    if (reason === 'clickaway') {
      return;
    }

    setOpen(false);
  };

  const Alert = React.forwardRef<HTMLDivElement, AlertProps>(function Alert (
    props,
    ref
  ) {
    return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
  });

  const validationSchema = Yup.object().shape({
    name: Yup
      .string()
      .required('Project name is required')
      .max(20).
      min(2).
      matches(/^[a-zA-Z0-9]+$/, 'Only alphabets and numbers are allowed for this field'),
    description: Yup.string().required('Description is required').max(100).min(2),
    maxDocs: Yup.number().required('maxDocs is required').min(5).max(10000)
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
              name="name"
              label="Project Name"
              disabled={open}
            />
            <Field
              component={TextField}
              name="description"
              label="ProjectDescription"
              disabled={open}
            />
            <Field
              component={TextField}
              name="maxDocs"
              label="Maximum number of works by every search text"
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
            <Typography variant="h4">{`OrgId: ${context.user.orgId.split('.')[0]}`}</Typography>
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
                  Your project adding was success!
                </Alert>
              ) : (
                <Alert
                  onClose={handleClose}
                  severity="error"
                  sx={{ width: '100%' }}
                >
                  Your project adding was unsuccess.
                  You have another project with same name!
                </Alert>
              )}
            </Snackbar>
          </Stack>
        </Form>
      )}
    </Formik>
  );
};
