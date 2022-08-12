import React from 'react';
interface IQuery {
  errorMsg: string;
  method: 'GET' | 'POST';
  url: string;
}

type TSelector =
  | 'createDatabase'
  | 'createCollection'
  | 'createDocument'
  | 'getPatterns'
  | 'getCountries'

const queries: Record<TSelector, IQuery> = {
  createDatabase: {
    errorMsg: '',
    method: 'POST',
    url: 'http://localhost:5001/mongo-db-create'
  },
  createCollection: {
    errorMsg: '',
    method: 'POST',
    url: 'http://localhost:5001/mongo-db-create'
  },
  createDocument: {
    errorMsg: '',
    method: 'POST',
    url: 'http://localhost:5001/mongo-db-create'
  },
  getCountries: {
    errorMsg: '',
    method: 'GET',
    url:
      'https://raw.githubusercontent.com/dr5hn/' +
      'countries-states-cities-database/master/countries%2Bstates%2Bcities.json'
  },
  getPatterns: {
    errorMsg: '',
    method: 'GET',
    url: 'http://34.74.92.5:5000/patterns'
  }
};

const query = async(
  queryName: TSelector,
  setResponse: React.Dispatch<React.SetStateAction<Array<Record<string, string>>>>,
  jsonObject?: Record<string, string>
): Promise<void> => {
  const requestOptions = queries[queryName].method === 'GET' ? {
    method: 'GET'
  } : {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(jsonObject)
  };

  try {
    const response = await fetch(queries[queryName].url, requestOptions);

    if (response.status === 200) {
      const responseObj: Record<string, string>[] = await response.json();
      setResponse(responseObj);
    } else {
      setResponse([]);
    }
  } catch (error) {
    setResponse([]);
  }
};

export { query };
export type { TSelector };
