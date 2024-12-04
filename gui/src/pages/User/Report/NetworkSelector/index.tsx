import React, { useEffect, useContext, useState, useCallback, useRef } from 'react';
import { AppContext } from 'contexts';
import { query } from 'utils/queries';
import { ProjectSelector } from './ProjectSelector';
import { PatternSelector } from './PaternSelector';
import { Card, CardContent, CardMedia, Typography } from '@mui/material';
import _ from 'lodash';
import { ForceGraph3D } from 'react-force-graph';
import { GraphTypeSelector } from './graphTypeSelector';
import DataModal from 'components/Modals/Authors';

type NodeObject$1 = object & {
  id?: string | number;
  degree?: number;
  betweenness?: number;
  closeness?: number;
  community?: number;
  x?: number;
  y?: number;
  z?: number;
  vx?: number;
  vy?: number;
  vz?: number;
  fx?: number;
  fy?: number;
  fz?: number;
};

export const NetworkSelector = () => {
  const context = useContext(AppContext);
  const organization = context.user.orgId.split('.')[0];

  const [graphType, setGraphType] = useState<string>('');
  const [project, setProject] = useState<string>('');
  const [pattern, setPattern] = useState<string>('');
  const [networkData, setNetworkData] = useState<Record<string, any>[]>([]);
  const [selectedNode, setSelectedNode] = useState<string | number | undefined>('');
  const [openModal, setOpenModal] = useState<boolean>(false);
  const fgRef = useRef<any>(null);

  useEffect(() => {
    if (graphType && project && pattern) {
      query(
        'runAdjacencyPipeline',
        setNetworkData,
        {
          'organization': organization,
          'project': project,
          'pattern': pattern,
          'graph_type': graphType
        }
      );
    }
  }, [graphType, organization, pattern, project]);

  const handleClick = useCallback((node: NodeObject$1) => {
    const distance = 40;
    const distRatio = 1 + distance / Math.hypot(node.x ?? 1, node.y ?? 1, node.z ?? 1);

    if (node.x && node.y && node.z && fgRef.current && 'cameraPosition' in fgRef.current) {
      fgRef.current.cameraPosition(
        {
          x: node.x * distRatio,
          y: node.y * distRatio,
          z: node.z * distRatio
        },
        node,
        3000
      );
    }

    setSelectedNode(node.id);
    setOpenModal(true);
  }, [fgRef]);

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
            ref={fgRef}
            graphData={networkData[0]['node_link_data']}
            nodeLabel={'id'}
            nodeAutoColorBy={'community'}
            nodeVal={node => Math.pow((node.degree ?? 1) / 40, 2)}
            linkOpacity={0.15}
            linkWidth={0.3}
            onNodeClick={handleClick}
          />
          {/* <Typography variant="h4">ForceGraph2D</Typography>
          <ForceGraph2D
            graphData={networkData[0]['node_link_data']}
            nodeLabel={'id'}
          /> */}
          <DataModal
            graphType={graphType}
            node={selectedNode}
            open={openModal}
            organization={organization}
            project={project}
            pattern={pattern}
            setOpen={setOpenModal}
          />
        </>)}
    </>
  );
};
