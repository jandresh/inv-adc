import {useEffect, useRef, useState} from 'react';
import './App.css';
import List from "./components/List"
import Form from "./components/Form"
import Table from './components/Table';
import {Patterns, Sub} from "./types"
// import { Graph } from "react-d3-graph";
import {
  ForceGraph2D,
  ForceGraph3D,
  ForceGraphVR,
  ForceGraphAR
} from 'react-force-graph';

interface AppState {
  subs: Array<Sub>
  newSubsNumber: number
}

// type AppStateSubs = Array<Sub>

const INITIAL_STATE = [
  {
    nick: "Jaime Hurtado",
    subMonths: 3,
    avatar: "https://i.pravatar.cc/150?u=jhurtado",
    description: "System administrator"
  },
  {
    nick: "Oswaldo Solarte",
    subMonths: 3,
    avatar: "https://i.pravatar.cc/150?u=osw",
    description: "System administrator"
  }
]

function App() {
  const [subs, setSubs] = useState<AppState["subs"]>([])
  const[newSubsNumber, setNewSubsNumber] = useState<AppState["newSubsNumber"]>(INITIAL_STATE.length)
  const divRef = useRef<HTMLDivElement>(null)

  const [number, setNumber] = useState<number>(5)

  const changeNumber = () => {
    setNumber(number+1)
  }

  const [patterns, setPatterns] = useState<Array<Patterns>>([])

  const mapFromApi = (apiResponse: Array<Patterns>): Array<Patterns> => {
    return apiResponse.map(patternFromApi =>{
      const {
        db: db,
        description: description,
        patternid: patternid,
        pattern: pattern
      } = patternFromApi
      return {
        db,
        description,
        patternid,
        pattern
      }
    })
  }

  const [pattern100, setPattern100] =useState("")
  useEffect(()=>{
    setSubs(INITIAL_STATE)
    const fetchPatterns = async (): Promise<Array<Patterns>> => {
      return await fetch("http://34.74.92.5:5000/patterns", {
        method: 'GET'
    }).then(response => response.json())
    }
    fetchPatterns().then(response => {
      setPatterns(mapFromApi(response))
    })
  }, [])



  const handleNewSub = (newSub: Sub): void => {
    setSubs(subs => [...subs, newSub])
    setNewSubsNumber(n => n + 1)
  }


const myConfig = {
  nodeHighlightBehavior: true,
  node: {
    color: "lightgreen",
    size: 800,
    highlightStrokeColor: "blue",
  },
  link: {
    highlightColor: "lightblue",
  },
};

const onClickNode = function(nodeId: any) {
  window.alert(`Clicked node ${nodeId}`);
};

const onClickLink = function(source: any, target: any) {
  window.alert(`Clicked link between ${source} and ${target}`);
};


  return (
    <div className="App" ref={divRef}>
      <h1>Users</h1>
      <List subs={subs} />
      Users count: {newSubsNumber}
      <Form onNewSub={handleNewSub}/>
      {number}
      <button onClick={changeNumber}>ChangeNumber</button>
      <h1>Patterns</h1>
      <Table patterns={patterns} />
    </div>
  );
}

export default App;
