import { Typography } from '@mui/material';
import React, { useContext, useEffect, useState } from 'react';
import { Helmet } from 'react-helmet';
import { AppContext } from '../../contexts';
import { APP_TITLE, PAGE_TITLE_HOME } from '../../utils/constants';
import { Table } from '../../components/Table';
import type { Patterns } from '../../types';

export const Database = () => {
  const context = useContext(AppContext);

  const [patterns, setPatterns] = useState<Array<Patterns>>([]);

  const mapFromApi = (apiResponse: Array<Patterns>): Array<Patterns> => {
    return apiResponse.map((patternFromApi) => {
      const {
        db: db,
        description: description,
        patternid: patternid,
        pattern: pattern
      } = patternFromApi;
      return {
        db,
        description,
        patternid,
        pattern
      };
    });
  };

  useEffect(() => {
    const fetchPatterns = async(): Promise<Array<Patterns>> => {
      return await fetch('http://34.74.92.5:5000/patterns', {
        method: 'GET'
      }).then((response) => response.json());
    };
    fetchPatterns().then((response) => {
      setPatterns(mapFromApi(response));
    });
  }, []);

  return (
    <>
      <Helmet>
        <title>
          {PAGE_TITLE_HOME} | {APP_TITLE}
        </title>
      </Helmet>
      <Typography variant="h4">{`Hello, ${context.user.name}`}</Typography>
      <Table patterns={patterns} />
    </>
  );
};
