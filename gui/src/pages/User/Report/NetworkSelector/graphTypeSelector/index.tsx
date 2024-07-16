import React, { useState } from 'react';
import _ from 'lodash';
import MenuItem from '@mui/material/MenuItem';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import Stack from '@mui/material/Stack';

export const GraphTypeSelector: React.FC<{
  setGraphType: React.Dispatch<React.SetStateAction<string>>
}> = ({ setGraphType }) => {
  const graphTypes: Record<string, string>[] = [
    { '_id': '1', 'name': 'Authors', 'value': 'authors' },
    { '_id': '2', 'name': 'Keywords', 'value': 'keywords' },
    { '_id': '3', 'name': 'Organizations', 'value': 'organizations' },
    { '_id': '4', 'name': 'Countries', 'value': 'countries' }
  ];
  const [selectedValue, setSelectedValue] = useState('');

  const handleChange = (event: SelectChangeEvent<unknown>) => {
    if (_.isString(event.target.value)) {
      setGraphType(event.target.value);
      setSelectedValue(event.target.value);
    }
  };

  return (
    <Stack spacing={2}>
      <Select
        labelId="demo-simple-select-label"
        id="demo-simple-select"
        label="project"
        onChange={handleChange}
        value={selectedValue}
      >
        {graphTypes.map(
          (selectedType): JSX.Element => (
            <MenuItem
              key={selectedType['_id']}
              value={selectedType['value']}
            >
              {selectedType['name']}
            </MenuItem>
          )
        )}
      </Select>
    </Stack>
  );
};
