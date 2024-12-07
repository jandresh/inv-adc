/* eslint-disable max-len */
import React, { useEffect, useContext, useState, useCallback, useRef } from 'react';
import { AppContext } from 'contexts';
import { query } from 'utils/queries';
import { ProjectSelector } from './ProjectSelector';
import { PatternSelector } from './PaternSelector';
import { Card, CardContent, CardMedia, Typography, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import { DataGrid, GridAutosizeOptions, GridColDef, GridRowParams } from '@mui/x-data-grid';
import _ from 'lodash';
import { ForceGraph2D, ForceGraph3D } from 'react-force-graph';
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
  const [sizeBy, setSizeBy] = useState<string>('none');
  const [selectedNode, setSelectedNode] = useState<string | number | undefined>('');
  const [openModal, setOpenModal] = useState<boolean>(false);
  const fgRef = useRef<any>(null);
  const [screenHeight, setScreenHeight] = useState<number>(window.innerHeight);
  const [screenWidth, setScreenWidth] = useState<number>(window.innerWidth);

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
    const handleResize = () => {
      setScreenHeight(window.innerHeight);
      setScreenWidth(window.innerWidth);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
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
    { field: 'id', headerName: 'ID', flex: 2 },
    { field: 'degree', headerName: 'Degree', flex: 1, align: 'center', headerAlign: 'center' },
    { field: 'closeness', headerName: 'Closeness', flex: 1, align: 'center', headerAlign: 'center' },
    { field: 'betweenness', headerName: 'Betweenness', flex: 1, align: 'center', headerAlign: 'center' },
    { field: 'community', headerName: 'Community', flex: 1, align: 'center', headerAlign: 'center' }
  ];

  const rows = networkData[0]?.node_link_data?.nodes?.map((node: NodeObject$1) => ({
    id: node.id,
    degree: node.degree,
    closeness: node.closeness ? node.closeness.toFixed(5) : 0,
    betweenness: node.betweenness ? node.betweenness.toFixed(5) : 0,
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

  const autosizeOptions: GridAutosizeOptions = {
    includeOutliers: true,
    includeHeaders: true
  };

  const getMaxMetrics = (nodes: NodeObject$1[]) => {
    return {
      degree: Math.max(...nodes.map(node => node.degree ?? 0)),
      closeness: Math.max(...nodes.map(node => node.closeness ?? 0)),
      betweenness: Math.max(...nodes.map(node => node.betweenness ?? 0))
    };
  };

  const maxMetrics = networkData[0]?.node_link_data?.nodes
    ? getMaxMetrics(networkData[0].node_link_data.nodes)
    : { degree: 1, closeness: 1, betweenness: 1 };

  return (
    <>
      <Card sx={{ width: screenWidth * 0.95 }}>
        <Typography variant="h4">Network selector</Typography>
        <Typography variant="h5">Select Graph Type</Typography>
        <GraphTypeSelector setGraphType={setGraphType}/>
        <Typography variant="h5">Select Project</Typography>
        <ProjectSelector setProject={setProject}/>
        <Typography variant="h5">Select Pattern</Typography>
        <PatternSelector project={project} setPattern={setPattern}/>
      </Card>
      {!_.isUndefined(networkData[0]) && (
        <>
          <Card>
            <Typography variant="h4">WordCloud Graph</Typography>
            <CardMedia
              width={screenWidth * 0.95}
              component='img'
              src={networkData[0]['wordcloud_image']}
              title="Network"
            />
          </Card>
          <Card sx={{ height: '70vh', overflow: 'auto' }}>
            <Typography variant="h4">NetworkX Graph</Typography>
            <CardMedia
              width={screenWidth * 0.95}
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
          <Card>
            <Typography variant="h4">Network Graph</Typography>
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
              height={screenHeight * 0.7}
              width={screenWidth * 0.95}
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
              nodeAutoColorBy={'community'}
              // nodeVal={node => Math.pow((node.closeness ?? 0.000001) * 20, 3) / 100 } Org
              // nodeVal={node => Math.pow((node.closeness ?? 0.000001) * 100, 3) } Authors
              // nodeVal={node => Math.pow((node.betweenness ?? 0.00001), 0.4) * 1000} Authors
              // nodeVal={node => Math.pow((node.betweenness ?? 0) * 1000, 4) / 100000000} Org
              nodeVal={(node) =>
                sizeBy === 'none' ? 1 : Math.pow((node[sizeBy] ?? 0) / maxMetrics[sizeBy as keyof typeof maxMetrics] * 100000, 2) / 1000000000
              }
              linkOpacity={0.15}
              linkWidth={0.1}
              onNodeClick={handleClick}
            />
          </Card>
          <Card>
            <Typography variant="h4">Community Graph</Typography>
            <ForceGraph2D
              height={screenHeight * 0.7}
              width={screenWidth * 0.95}
              graphData={networkData[0]['node_link_data']}
              nodeLabel={'id'}
              nodeVal={(node) =>
                sizeBy === 'none' ? 1 : Math.pow((node[sizeBy] ?? 0) / maxMetrics[sizeBy as keyof typeof maxMetrics] * 100000, 2) / 1000000000
              }
              nodeAutoColorBy={'community'}
            />
            <Typography variant="h5" marginTop={2}>
              Node Metrics
            </Typography>
            <Typography variant="h6">Max Metrics</Typography>
            <Typography>Max Degree: {maxMetrics.degree}</Typography>
            <Typography>Max Closeness: {maxMetrics.closeness.toFixed(5)}</Typography>
            <Typography>Max Betweenness: {maxMetrics.betweenness.toFixed(5)}</Typography>
          </Card>
          <Card sx={{ width: screenWidth * 0.95 }}>
            <DataGrid
              rows={rows}
              columns={columns}
              onRowClick={handleTableRowClick}
              density="compact"
              autosizeOptions={autosizeOptions}
              getRowHeight={() => 'auto'}
              initialState={
                {
                  pagination: {
                    paginationModel: { pageSize: 50 }
                  }
                }
              }
              pageSizeOptions={[10, 50, 100]}
            />
          </Card>
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
