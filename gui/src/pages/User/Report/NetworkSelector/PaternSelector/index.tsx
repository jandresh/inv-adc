import React, { useEffect, useContext, useState } from 'react';
import { AppContext } from 'contexts';
import { query } from 'utils/queries';
import _ from 'lodash';
import MenuItem from '@mui/material/MenuItem';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import Stack from '@mui/material/Stack';

export const PatternSelector: React.FC<{
  project: string
  setPattern: React.Dispatch<React.SetStateAction<string>>
}> = ({ project, setPattern }) => {
  const context = useContext(AppContext);
  const [patterns, setPatterns] = useState<Record<string, string>[]>([]);

  useEffect(() => {
    query(
      'listDocuments',
      setPatterns,
      { 'db_name': context.user.orgId.split('.')[0], 'coll_name': `patterns#${project}` }
    );
  }, [context, project]);

  const handleChange = (event: SelectChangeEvent<unknown>) => {
    if (_.isString(event.target.value)) {
      setPattern(event.target.value);
    }
  };

  return (
    <Stack spacing={2}>
      <Select
        labelId="demo-simple-select-label"
        id="demo-simple-select"
        label="project"
        onChange={handleChange}
      >
        <MenuItem key={'global'} value={'global'}>
          Global
        </MenuItem>
        {patterns.map(
          (selectedPattern): JSX.Element => (
            <MenuItem
              key={selectedPattern['_id']}
              value={selectedPattern['_id']}
            >
              {selectedPattern['pattern']}
            </MenuItem>
          )
        )}
      </Select>
    </Stack>
  );
};
