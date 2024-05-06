import React, { useCallback, useEffect, useContext, useState, ChangeEvent } from 'react';
import { AppContext } from 'contexts';
import { Formik, Form, Field } from 'formik';
import { Select } from 'formik-mui';
import { Box, Button, LinearProgress, Stack } from '@mui/material';
import { query } from 'utils/queries';
import MenuItem from '@mui/material/MenuItem';
import Snackbar from '@mui/material/Snackbar';
import MuiAlert, { AlertProps } from '@mui/material/Alert';
import * as Yup from 'yup';
import UploadFileIcon from '@mui/icons-material/UploadFile';

interface IPatternsForm {
  project: string;
}

export const AddFileForm = () => {
  const context = useContext(AppContext);
  const initialValues: IPatternsForm = {
    project: ''
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
  const [fileData, setFileData] = useState<string[]>([]);
  const [unsavedPatterns, setUnsavedPatterns] = useState<string[]>([]);
  const [filename, setFilename] = useState('');

  const handleSubmit = useCallback(
    async (values: IPatternsForm): Promise<void> => {
      let unsuccessPatterns = [];
      for (var index in fileData) {
        const pattern = fileData[index]
          .replace('á', 'a')
          .replace('é', 'e')
          .replace('í', 'i')
          .replace('ó', 'o')
          .replace('ú', 'u')
          .replace(/[^a-zA-Z0-9 ]/g, '');
        const findProjectDocument = {
          'db_name': context.user.orgId.split('.')[0],
          'coll_name': `patterns#${values.project}`,
          'query': {
            'pattern': pattern
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
            'pattern': pattern
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
          unsuccessPatterns.push(pattern);
        }
      }
      if (unsuccessPatterns) setResponse([{ exit: 2 }]);
      setUnsavedPatterns(unsuccessPatterns);
      setOpen(true);
    },
    [context, fileData, findPatternResponse, setOpen, setResponse, setUnsavedPatterns]
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
      matches(/^[a-zA-Z0-9]+$/, 'Only alphabets and numbers are allowed for this field')
  });

  const handleFileUpload = (e: ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) {
      return;
    }
    const file = e.target.files[0];
    const { name } = file;
    setFilename(name);

    const reader = new FileReader();
    reader.onload = (evt) => {
      if (!evt?.target?.result) {
        return;
      }
      const { result } = evt.target;
      setFileData(result.toString().split('\n'));
    };
    reader.readAsText(file);
  };

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
            <Button
              component="label"
              variant="outlined"
              startIcon={<UploadFileIcon />}
              sx={{ marginRight: '1rem' }}
            >
              Upload File
              <input type="file" accept=".txt" hidden onChange={handleFileUpload} />
            </Button>
            <Box>{filename}</Box>
            <Box>{fileData.join('\n')}</Box>
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
                  Your file patterns adding was success!
                </Alert>
              ) : (
                <Alert
                  onClose={handleClose}
                  severity="error"
                  sx={{ width: '100%' }}
                >
                  Your file adding was unsuccess.
                  Some patterns already exits!:
                  {unsavedPatterns.join('\n')}
                </Alert>
              )}
            </Snackbar>
          </Stack>
        </Form>
      )}
    </Formik>
  );
};
