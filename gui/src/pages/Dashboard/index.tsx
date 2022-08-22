import { Typography } from '@mui/material';
import React, {
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState
} from 'react';
import { Helmet } from 'react-helmet';
import { AppContext } from '../../contexts';
import { APP_TITLE, PAGE_TITLE_HOME } from '../../utils/constants';
import { ForceGraph3D } from 'react-force-graph';
import { query } from 'utils/queries';

export const Dashboard = () => {
  const context = useContext(AppContext);

  const fgRef: any = useRef();

  const handleClick = useCallback(
    (node: any) => {
      // Aim at node from outside it
      const distance = 200;
      const distRatio = 1 + distance / Math.hypot(node.x, node.y, node.z);

      if (fgRef.current !== undefined) {
        fgRef.current.cameraPosition(
          {
            x: node.x * distRatio,
            y: node.y * distRatio,
            z: node.z * distRatio
          }, // new position
          node, // lookAt ({ x, y, z })
          3000 // ms transition duration
        );
      }
    },
    [fgRef]
  );

  const [data, setData] = useState<Record<string, any>[]>([]);

  useEffect(() => {
    query('listDocument', setData);
  }, [setData]);

  return (
    <>
      <Helmet>
        <title>
          {PAGE_TITLE_HOME} | {APP_TITLE}
        </title>
      </Helmet>
      <Typography variant="h4">{`Hello, ${context.user.firstName}`}</Typography>
      <h1>Authors Network Graph</h1>
      <ForceGraph3D
        ref={fgRef}
        graphData={data[0]['graph_data']}
        linkAutoColorBy="related"
        linkLabel="related"
        linkWidth={(link) =>
          data[0]['graph_data'].links.filter(
            (item: any) =>
              item.source === link.source && item.target === link.target
          )[0].related **
            3 /
          1000
        }
        nodeAutoColorBy="works"
        nodeLabel={(node) =>
          `${
            data[0]['graph_data'].nodes[parseInt(node.id as string, 10)].name
          } ${
            data[0]['graph_data'].nodes[parseInt(node.id as string, 10)].works
          } works`
        }
        nodeRelSize={0.05}
        nodeVal={(node) =>
          data[0]['graph_data'].nodes[parseInt(node.id as string, 10)].works **
          4
        }
        onNodeClick={handleClick}
        onLinkClick={(link) => {
          alert(`linkClick ${link.source?.toString}`);
        }}
        onNodeDragEnd={(node) => {
          node.fx = node.x;
          node.fy = node.y;
          node.fz = node.z;
        }}
      />
    </>
  );
};
