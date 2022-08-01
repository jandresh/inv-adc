interface IQuery {
  'CREATE_USER_DB': {
    url: string;
    response:Record<string, string>;
  }
}

type selectorType = 'CREATE_USER_DB' | 'CREATE_USER_COLL' | 'CREATE_'

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
