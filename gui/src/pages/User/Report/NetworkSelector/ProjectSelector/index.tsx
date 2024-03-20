import React, { useEffect, useContext, useState } from 'react';
import { AppContext } from 'contexts';
import { query } from 'utils/queries';
import _ from 'lodash';
import MenuItem from '@mui/material/MenuItem';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import Stack from '@mui/material/Stack';

export const ProjectSelector: React.FC<{
  setProject: React.Dispatch<React.SetStateAction<string>>
}> = ({ setProject }) => {
  const context = useContext(AppContext);
  const [projects, setProjects] = useState<Record<string, string>[]>([]);

  useEffect(() => {
    query(
      'listDocuments',
      setProjects,
      { 'db_name': context.user.orgId.split('.')[0], 'coll_name': 'projects' }
    );
  }, [context]);

  const handleChange = (event: SelectChangeEvent<unknown>) => {
    if (_.isString(event.target.value)) {
      setProject(event.target.value);
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
        {projects.map(
          (selectedProject): JSX.Element => (
            <MenuItem
              key={selectedProject['_id']}
              value={selectedProject['name']}
            >
              {selectedProject['name']}
            </MenuItem>
          )
        )}
      </Select>
    </Stack>
  );
};
