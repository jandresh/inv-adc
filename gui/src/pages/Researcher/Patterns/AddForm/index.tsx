import React, { useCallback, useEffect, useContext, useState } from 'react';
import { AppContext } from 'contexts';
import { Formik, Form, Field } from 'formik';
import { Select, TextField } from 'formik-mui';
import { Button, LinearProgress, Stack } from '@mui/material';
import { query } from 'utils/queries';
import MenuItem from '@mui/material/MenuItem';
import Snackbar from '@mui/material/Snackbar';
import MuiAlert, { AlertProps } from '@mui/material/Alert';
import * as Yup from 'yup';

interface IPatternsForm {
  project: string;
  pattern: string;
}

export const AddForm = () => {
  const context = useContext(AppContext);
  const initialValues: IPatternsForm = {
    project: '',
    pattern: ''
  };
  const [projects, setProjects] = useState<Record<string, string>[]>([]);

  useEffect(() => {
    query(
      'listDocuments',
      setProjects,
      { 'db_name': context.user.orgId.split('.')[0], 'coll_name': 'projects' }
    );
  }, [context]);

  const [findPatternResponse, setFindPatternResponse] = useState<
    Record<string, any>[]
  >([]);
  const [response, setResponse] = useState<Record<string, any>[]>([
    { exit: 1 }
  ]);
  const [open, setOpen] = useState(false);
  const handleSubmit = useCallback(
    async (values: IPatternsForm): Promise<void> => {
      const findProjectDocument = {
        'db_name': context.user.orgId.split('.')[0],
        'coll_name': `patter#${values.project}`,
        'query': {
          'pattern': values.pattern
        },
        'projection': {
          'pattern': 1
        }
      };
      const findProjectResult = await query(
        'findDocument',
        setFindPatternResponse,
        findProjectDocument
      );
      const {
        success: successProjectFind,
        responseObj: responseProjectFind
      } = findProjectResult;
      const registerDocument = {
        'db_name': context.user.orgId.split('.')[0],
        'coll_name': `patterns#${values.project}`,
        document: {
          'pattern': values.pattern
        }
      };
      if (
        successProjectFind &&
        responseProjectFind.length === 0 &&
        findPatternResponse
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
    [context, findPatternResponse, setOpen, setResponse]
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
    project: Yup
      .string()
      .required('Project name is required')
      .max(20).
      min(2).
      matches(/^[a-zA-Z0-9]+$/, 'Only alphabets and numbers are allowed for this field'),
    pattern: Yup
      .string()
      .required('Pattern is required')
      .max(100)
      .min(2)
      .matches(/^[a-zA-Z0-9 ]+$/, 'Only alphabets, numbers and spaces are allowed')
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
              component={Select}
              name="project"
              label="Project Name"
              disabled={open}
            >
              {projects.map(
                (selectedProject): JSX.Element => (
                  <MenuItem key={selectedProject['_id']} value={selectedProject['name']}>
                    {selectedProject['name']}
                  </MenuItem>
                )
              )}
            </Field>
            <Field
              component={TextField}
              name="pattern"
              label="Pattern string"
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
