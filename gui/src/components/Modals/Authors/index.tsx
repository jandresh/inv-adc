import React, { useEffect, useState } from 'react';
import { Modal, Box, Typography, Button } from '@mui/material';
import { query } from 'utils/queries';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';


interface Info {
  [key: string]: any;
}

const style = {
  position: 'absolute' as const,
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

const wideStyle = {
  ...style,
  position: 'absolute' as const,
  top: '50%',
  left: '70%',
  width: 600
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
  const [secondModalOpen, setSecondModalOpen] = useState(false);
  const [detailedInfo, setDetailedInfo] = useState<Info[]>([]);
  const handleClose = () => setOpen(false);

  useEffect(() => {
    const findDocument = {
      'db_name': organization,
      'coll_name': `${entity}_info#${project}#${pattern}`,
      query: {
        [entity]: node
      }
    };
    query(
      'findDocument',
      setInfo,
      findDocument
    );
  }, [node, organization, pattern, project, entity]);

  const handleValueClick = (key: string, value: string | number) => {
    setSecondModalOpen(true);

    const getSingular = (word: string) => {
      if (word === 'countries') return 'country';
      if (word === 'doc_id') return 'dbid';
      if (word.endsWith('s')) return word.slice(0, -1);
      return word;
    };

    const detailedQuery = ['doc_id', 'doi'].includes(key) ? {
      'db_name': organization,
      'coll_name': `metadata#${project}#${pattern}`,
      query: {
        [getSingular(key)]: value
      }
    } : {
      'db_name': organization,
      'coll_name': `${getSingular(key)}_info#${project}#${pattern}`,
      query: {
        [getSingular(key)]: value
      }
    };

    query('findDocument', setDetailedInfo, detailedQuery);
  };

  if (node === undefined || info.length < 1) return <></>;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
      <Modal
        open={open}
        onClose={handleClose}
        aria-labelledby="modal-title"
        aria-describedby="modal-description"
      >
        <Box sx={style}>
          <Typography id="modal-title" variant="h6" component="h2">
              Node metadata
          </Typography>
          <Box id="modal-description" sx={{ mt: 2 }}>
            {Object.entries(info[0]).map(([key, value]) => (
              <Typography key={key} sx={{ mb: 1 }}>
                <strong>{key}:</strong>{' '}
                {Array.isArray(value) ? (
                  value.map((item, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleValueClick(key, item)}
                    >
                      {item}
                    </button>
                  ))
                ) : (
                  <button
                    onClick={() => handleValueClick(key, value)}
                  >
                    {value}
                  </button>
                )}
              </Typography>
            ))}
          </Box>
        </Box>
      </Modal>
      <Modal
        open={secondModalOpen}
        onClose={() => setSecondModalOpen(false)}
        aria-labelledby="second-modal-title"
        aria-describedby="second-modal-description"
      >
        <Box sx={wideStyle}>
          <Typography id="second-modal-title" variant="h6" component="h2">
            Detailed Information
          </Typography>
          <Box id="second-modal-description" sx={{ mt: 2 }}>
            {detailedInfo.length > 0 ? (
              Object.entries(detailedInfo[0])
                .filter(([key]) => key !== '_id')
                .map(([field, value]) => (
                  <Box key={field} sx={{ mb: 2 }}>
                    <Typography>
                      <strong>{field === 'url' ? 'Download' : field}:</strong>
                    </Typography>
                    {Array.isArray(value) ? (
                      value.map((item) => (
                        <Box key={item} sx={
                          { display: 'flex', alignItems: 'center', gap: 2, mt: 1 }}>
                          {field === 'url' ? (
                            <Button
                              startIcon={<PictureAsPdfIcon style={{ color: 'red' }} /> }
                              onClick={() => window.open(item, '_blank')}
                            >
                              <Typography>{value}</Typography>
                            </Button>
                          ) : (
                            <Typography>{item}</Typography>
                          )}
                        </Box>
                      ))
                    ) : field === 'url' ? (
                      <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
                        <Button
                          startIcon={<PictureAsPdfIcon style={{ color: 'red', fontSize: 60 }} /> }
                          onClick={() => window.open(value, '_blank')}
                        />
                      </Box>
                    ) : (
                      <Typography>{value}</Typography>
                    )}
                  </Box>
                ))
            ) : (
              <Typography>Not available</Typography>
            )}
          </Box>
        </Box>
      </Modal>
    </div>
  );
};

export default DataModal;
