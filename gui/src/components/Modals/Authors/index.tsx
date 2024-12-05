import React, { useEffect, useState } from 'react';
import { Modal, Box, Typography } from '@mui/material';
import { query } from 'utils/queries';

interface Info {
  [key: string]: any;
}

const style = {
  position: 'absolute' as 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: 400,
  bgcolor: 'background.paper',
  boxShadow: 24,
  p: 4,
  maxHeight: '80vh',
  overflow: 'auto'
};

const DataModal: React.FC<{
  graphType: string,
  node: string | number | undefined,
  open: boolean,
  organization: string,
  project: string,
  pattern: string,
  setOpen: React.Dispatch<React.SetStateAction<boolean>>
}> = ({ graphType, node, open, organization, project, pattern, setOpen }) => {
  const entity = graphType === 'countries' ? 'country' : graphType.slice(0, -1);
  const [info, setInfo] = useState<Info[]>([]);
  const handleClose = () => setOpen(false);

  useEffect(() => {
    const findDocument = {
      'db_name': organization,
      'coll_name': `${entity}_info#${project}#${pattern}`,
      'query': {
        [entity]: node
      }
    };
    query(
      'findDocument',
      setInfo,
      findDocument
    );
  }, [node, organization, pattern, project, entity]);

  if (node === undefined || info.length < 1) return <></>;

  return (
    <div>
      <Modal
        open={open}
        onClose={handleClose}
        aria-labelledby="modal-title"
        aria-describedby="modal-description"
      >
        <Box sx={style}>
          <Typography id="modal-title" variant="h6" component="h2">
              Data Information
          </Typography>
          <Box id="modal-description" sx={{ mt: 2 }}>
            {Object.entries(info[0]).map(([key, value]) => (
              <Typography key={key} sx={{ mb: 1 }}>
                <strong>{key}:</strong> {Array.isArray(value) ? value.join(', ') : value}
              </Typography>
            ))}
          </Box>
        </Box>
      </Modal>
    </div>
  );
};

export default DataModal;
