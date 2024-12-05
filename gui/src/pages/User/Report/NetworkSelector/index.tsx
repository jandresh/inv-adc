/* eslint-disable max-len */
import React, { useEffect, useContext, useState, useCallback, useRef } from 'react';
import { AppContext } from 'contexts';
import { query } from 'utils/queries';
import { ProjectSelector } from './ProjectSelector';
import { PatternSelector } from './PaternSelector';
import { Card, CardContent, CardMedia, Typography, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import { DataGrid, GridColDef, GridRowParams } from '@mui/x-data-grid';
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
  const [colorBy, setColorBy] = useState<string>('community');
  const [sizeBy, setSizeBy] = useState<string>('none');
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

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 150 },
    { field: 'degree', headerName: 'Degree', width: 100 },
    { field: 'closeness', headerName: 'Closeness', width: 100 },
    { field: 'betweenness', headerName: 'Betweenness', width: 150 },
    { field: 'community', headerName: 'Community', width: 120 }
  ];

  const rows = networkData[0]?.node_link_data?.nodes?.map((node: NodeObject$1) => ({
    id: node.id,
    degree: node.degree,
    closeness: node.closeness,
    betweenness: node.betweenness,
    community: node.community
  })) || [];

  const handleTableRowClick = useCallback((params: GridRowParams) => {
    const node = networkData[0]?.node_link_data?.nodes.find(
      (n: NodeObject$1) => n.id === params.row.id
    );

    if (node) {
      handleClick(node); // Usa la función `handleClick` ya implementada para enfocar el nodo.
    }
  }, [networkData, handleClick]);

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
          <Typography variant="h5">Graph Configuration</Typography>
          <FormControl fullWidth margin="normal">
            <InputLabel>Color By</InputLabel>
            <Select value={colorBy} onChange={(e) => setColorBy(e.target.value)}>
              <MenuItem value="community">Community</MenuItem>
              <MenuItem value="degree">Degree</MenuItem>
              <MenuItem value="closeness">Closeness</MenuItem>
              <MenuItem value="betweenness">Betweenness</MenuItem>
            </Select>
          </FormControl>
          <FormControl fullWidth margin="normal">
            <InputLabel>Size By</InputLabel>
            <Select value={sizeBy} onChange={(e) => setSizeBy(e.target.value)}>
              <MenuItem value="none">None</MenuItem>
              <MenuItem value="degree">Degree</MenuItem>
              <MenuItem value="closeness">Closeness</MenuItem>
              <MenuItem value="betweenness">Betweenness</MenuItem>
            </Select>
          </FormControl>
          <ForceGraph3D
            ref={fgRef}
            graphData={networkData[0]['node_link_data']}
            nodeLabel={node => `
              <div style="text-align: center; font-size: 14px;">
                <strong>${node.id}</strong><br/>
                Community: <span style="color: ${node.color || 'blue'}">${node.community}</span><br/>
                Degree: ${node.degree ?? 0}<br/>
                Betweenness: ${(node.betweenness ?? 0).toFixed(5)}<br/>
                Closeness: ${(node.closeness ?? 0).toFixed(5)}<br/>
              </div>
            `}
            nodeAutoColorBy={colorBy}
            // nodeVal={node => Math.pow((node.closeness ?? 0.000001) * 20, 3) / 100 } Org
            // nodeVal={node => Math.pow((node.closeness ?? 0.000001) * 100, 3) } Authors
            // nodeVal={node => Math.pow((node.betweenness ?? 0.00001), 0.4) * 1000} Authors
            // nodeVal={node => Math.pow((node.betweenness ?? 0) * 1000, 4) / 100000000} Org
            nodeVal={(node) =>
              sizeBy === 'none' ? 1 : node[sizeBy] ?? 1
            }
            linkOpacity={0.18}
            linkWidth={0.4}
            onNodeClick={handleClick}
          />
          {/* <Typography variant="h4">ForceGraph2D</Typography>
          <ForceGraph2D
            graphData={networkData[0]['node_link_data']}
            nodeLabel={'id'}
          /> */}
          <Typography variant="h5" marginTop={2}>
            Node Metrics
          </Typography>
          <DataGrid
            rows={rows}
            columns={columns}
            autoHeight
            onRowClick={handleTableRowClick}
          />
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
