import * as React from 'react';
import { Formik, Form, Field } from 'formik';
import { TextField } from 'formik-mui';
import { Button, LinearProgress, Stack } from '@mui/material';

interface IRegister {
  name: string;
  email: string;
  password: string;
}

export const Register: React.FC<{}> = () => {
  const initialValues: IRegister = {
    name: '',
    email: '',
    password: ''
  };

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={() => {}}
    >
      {({ submitForm, isSubmitting }) => (
        <Form>
          <Stack spacing={2}>
            <Field
              component={TextField}
              name="name"
              type="name"
              label="name"
            />
            <Field
              component={TextField}
              name="email"
              type="email"
              label="Email"
            />
            <Field
              component={TextField}
              type="password"
              label="Password"
              name="password"
            />
            {isSubmitting && <LinearProgress />}
            <Button
              variant="contained"
              color="primary"
              disabled={isSubmitting}
              onClick={submitForm}
            >
              Submit
            </Button>
          </Stack>
        </Form>
      )}
    </Formik>
  );
};
