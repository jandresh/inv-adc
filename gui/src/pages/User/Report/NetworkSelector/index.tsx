import React, { useEffect, useContext, useState } from 'react';
import { AppContext } from 'contexts';
import { query } from 'utils/queries';
import { ProjectSelector } from './ProjectSelector';
import { PatternSelector } from './PaternSelector';
import { Card, CardContent, CardMedia, Typography } from '@mui/material';
import _ from 'lodash';
import { ForceGraph2D, ForceGraph3D } from 'react-force-graph';

export const NetworkSelector = () => {
  const context = useContext(AppContext);

  const [project, setProject] = useState<string>('');
  const [pattern, setPattern] = useState<string>('');
  const [networkData, setNetworkData] = useState<Record<string, any>[]>([]);

  useEffect(() => {
    if (project && pattern) {
      query(
        'runAdjacencyPipeline',
        setNetworkData,
        { 'organization': context.user.orgId.split('.')[0], 'project': project, 'pattern': pattern }
      );
    }
  }, [context, pattern, project]);

  return (
    <>
      <Typography variant="h5">Select Project</Typography>
      <ProjectSelector setProject={setProject}/>
      <Typography variant="h5">Select Pattern</Typography>
      <PatternSelector project={project} setPattern={setPattern}/>
      {!_.isUndefined(networkData[0]) && (
        <>
          <Typography variant="h4">NetworkX Graph</Typography>
          <Card sx={{ maxWidth: 'fit-content' }}>
            <CardMedia
              component='img'
              // eslint-disable-next-line max-len
              src={networkData[0]['b64_image']}
              title="Network"
            />
            <CardContent>
              <Typography gutterBottom variant="h5" component="div">
                Network Data
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Nodes: {networkData[0]['nodes']}
                <br />
                Edges: {networkData[0]['edges']}
              </Typography>
            </CardContent>
          </Card>
          <Typography variant="h4">ForceGraph3D</Typography>
          <ForceGraph3D graphData={networkData[0]['node_link_data']}/>
          <Typography variant="h4">ForceGraph2D</Typography>
          <ForceGraph2D graphData={networkData[0]['node_link_data']}/>
        </>)}
    </>
  );
};
