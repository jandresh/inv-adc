import React, { useEffect, useContext, useState } from 'react';
import { AppContext } from 'contexts';
import { query } from 'utils/queries';
import { ProjectSelector } from './ProjectSelector';
import { PatternSelector } from './PaternSelector';
import { Card, CardContent, CardMedia, Typography } from '@mui/material';
import _ from 'lodash';
import { ForceGraph2D, ForceGraph3D } from 'react-force-graph';
import { GraphTypeSelector } from './graphTypeSelector';

export const NetworkSelector = () => {
  const context = useContext(AppContext);

  const [graphType, setGraphType] = useState<string>('');
  const [project, setProject] = useState<string>('');
  const [pattern, setPattern] = useState<string>('');
  const [networkData, setNetworkData] = useState<Record<string, any>[]>([]);
  // function openTab (url: string) {
  //   console.log("openTab");
  //   window.open(url, '_blank');
  // }

  useEffect(() => {
    if (graphType && project && pattern) {
      query(
        'runAdjacencyPipeline',
        setNetworkData,
        {
          'organization': context.user.orgId.split('.')[0],
          'project': project,
          'pattern': pattern,
          'graph_type': graphType
        }
      );
    }
  }, [context, graphType, pattern, project]);

  return (
    <>
      <Typography variant="h5">Select Graph Type</Typography>
      <GraphTypeSelector setGraphType={setGraphType}/>
      <Typography variant="h5">Select Project</Typography>
      <ProjectSelector setProject={setProject}/>
      <Typography variant="h5">Select Pattern</Typography>
      <PatternSelector project={project} setPattern={setPattern}/>
      {!_.isUndefined(networkData[0]) && (
        <>
          <Typography variant="h4">WordCloud Graph</Typography>
          <Card sx={{ maxWidth: 'fit-content' }}>
            <CardMedia
              component='img'
              src={networkData[0]['wordcloud_image']}
              title="Network"
            />
          </Card>
          <Typography variant="h4">NetworkX Graph</Typography>
          <Card sx={{ maxWidth: 'fit-content' }}>
            <CardMedia
              component='img'
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
          <ForceGraph3D
            graphData={networkData[0]['node_link_data']}
            nodeColor={'group'}
            nodeLabel={'id'}
            // onNodeClick={node => {openTab(node.id as string)}}
          />
          <Typography variant="h4">ForceGraph2D</Typography>
          <ForceGraph2D
            graphData={networkData[0]['node_link_data']}
            nodeLabel={'id'}
          />
        </>)}
    </>
  );
};
