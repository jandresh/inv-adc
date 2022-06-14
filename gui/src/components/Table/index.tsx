import React from 'react';
import { Patterns } from '../../types';

interface Props {
  patterns: Array<Patterns>;
}

const Table = ({ patterns }: Props) => {
  const renderTable = (): JSX.Element[] => {
    return patterns.map((item) => {
      return (
        <tr key={item.patternid}>
          <td>{item.patternid}</td>
          <td>{item.db}</td>
          <td>{item.description}</td>
          <td>{item.pattern.toString()}</td>
        </tr>
      );
    });
  };

  return (
    <table>
      <thead>
        <tr>
          <th>id</th>
          <th>Database</th>
          <th>Description</th>
          <th>Query</th>
        </tr>
      </thead>
      <tbody>{renderTable()}</tbody>
    </table>
  );
};

export { Table };
