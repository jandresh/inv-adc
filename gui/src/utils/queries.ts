interface IQuery {
  'CREATE_USER_DB': {
    url: string;
    response:Record<string, string>;
  }
}

type selectorType = 'CREATE_USER_DB' | 'CREATE_USER_COLL' | 'CREATE_USER_DOCUMENT'

const query = async (
  selector: selectorType,
  setResponse: React.Dispatch<React.SetStateAction<Record<string, string>>[] | undefined>
): Promise<void> => {
  const url =
    "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/countries%2Bstates%2Bcities.json";
  const errorMsg = "Couldn't fetch countries, states and cities database";

  try {
    const response = await fetch(url);

    if (response.status === 200) {
      const countriesObj: Record<string, string>[] = await response.json();
      setResponse(countriesObj);
    } else {
      setResponse(undefined);
    }
  } catch (error) {
    setResponse(undefined);
  }
};

export { query };
export type { IQuery };

// curl -X POST -H "Content-type: application/json" -d '{"db_name" : "adccali", "coll_name" : "Breast", "document" : {"doc_id" : "123456", "doc_name" : "Breast cancer history"}}' http://localhost:5001/mongo-doc-insert


// export const Queries = async() : Promise<void> => {
//   // POST request using fetch with error handling
//   const requestOptions = {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify({"db_name" : "user", "coll_name" : "inv-adc", "document" : {"name" : "Jaime Hurtado", "email" : "jandresh@gmail.com", "password": "Azul0244953729"}})
//   };
//   fetch('http://localhost:5001/mongo-doc-insert', requestOptions)
//       .then(async response => {
//           const isJson = response.headers.get('content-type')?.includes('application/json');
//           const data = isJson && await response.json();

//           // check for error response
//           if (!response.ok) {
//               // get error message from body or default to response status
//               const error = (data && data.message) || response.status;
//               return Promise.reject(error);
//           }

//           setState({ postId: data.id })
//       })
//       .catch(error => {
//           setState({ errorMessage: error.toString() });
//           console.error('There was an error!', error);
//       });
// }
