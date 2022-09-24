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
// import { query } from 'utils/queries';

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

  function relatedVerify (related: number, min: number): number {
    if (related >= min) {
      return related;
    }

    return 0.001;
  }
  const [data, setData] = useState<Record<string, any>[]>([]);

  useEffect(() => {
    // query('listDocuments', setData, {
    //   'db_name': 'arrays',
    //   'coll_name': 'authors_global'
    // });
    var jsonData = require('./authors_global.json');
    setData(jsonData);
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
      {data[0] && (
        <ForceGraph3D
          ref={fgRef}
          graphData={data[0]['graph_data']}
          linkAutoColorBy="related"
          linkLabel={(link) =>
            data[0]['graph_data'].links
              .filter(
                (item: any) =>
                  item.source === link.source && item.target === link.target
              )
              .map(
                (item: any) =>
                  `${item.source} <=> ${item.target} / ${item.related} works`
              )[0]
              .toString()
          }
          linkWidth={(link) =>
            relatedVerify(data[0]['graph_data'].links.filter(
              (item: any) =>
                item.source === link.source && item.target === link.target
            )[0].related, 200) **
              3 /
            800
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
          // nodeVal={(node) =>
          //   data[0]['graph_data'].nodes[parseInt(node.id as string, 10)]
          //     .works ** 4
          // }
          nodeVal={(node) =>
            data[0]['graph_data'].nodes[parseInt(node.id as string, 10)]
              .works === 34 ? 50000 : 100
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
      )}
    </>
  );
};
