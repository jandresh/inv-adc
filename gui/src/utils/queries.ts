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
  | 'findDocument'
  | 'getPatterns'
  | 'getCountries'
  | 'listCollections'
  | 'listDatabases'
  | 'listDocument';

const host = {
  localDb: 'http://localhost:5001',
  remoteDb: 'http://34.74.92.5:5000'
};

const queries: Record<TSelector, IQuery> = {
  createDatabase: {
    errorMsg: '',
    method: 'POST',
    url: `${host.remoteDb}/mongo-db-create`
  },
  createCollection: {
    errorMsg: '',
    method: 'POST',
    url: `${host.remoteDb}/mongo-db-create`
  },
  createDocument: {
    errorMsg: '',
    method: 'POST',
    url: `${host.remoteDb}/mongo-doc-insert`
  },
  findDocument: {
    errorMsg: '',
    method: 'POST',
    url: `${host.remoteDb}/mongo-doc-find`
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
    url: `${host.remoteDb}/patterns`
  },
  listCollections: {
    errorMsg: '',
    method: 'POST',
    url: `${host.remoteDb}/mongo-coll-list`
  },
  listDatabases: {
    errorMsg: '',
    method: 'GET',
    url: `${host.remoteDb}/mongo-db-list`
  },
  listDocument: {
    errorMsg: '',
    method: 'POST',
    url: `${host.remoteDb}/mongo-doc-list`
  }
};

const query = async (
  queryName: TSelector,
  setResponse: React.Dispatch<React.SetStateAction<Array<Record<string, any>>>>,
  jsonObject?: Record<string, any>
): Promise<{ success: boolean; responseObj: any }> => {
  const requestOptions =
    queries[queryName].method === 'GET'
      ? {
          method: 'GET'
        }
      : {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(jsonObject)
        };

  try {
    const response = await fetch(queries[queryName].url, requestOptions);

    if (response.status === 200) {
      const responseObj: Record<string, string>[] = await response.json();
      setResponse(responseObj);
      return { success: true, responseObj: responseObj };
    } else {
      return { success: false, responseObj: [] };
    }
  } catch (error) {
    return { success: false, responseObj: [] };
  }
};

export { query };
export type { TSelector };
