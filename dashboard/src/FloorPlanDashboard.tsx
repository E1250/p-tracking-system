import React, { useState, useRef, useEffect, useMemo} from 'react'
import { Stage, Layer, Group, Image as KonvaImage} from 'react-konva';
import {produce} from 'immer'

// Components
import {IconButton} from './components/buttons';
import {FloorBackground} from './components/canvas';
import {EdgeNode, CameraNode, CircleNode} from './components/graph'; 

// Interfaces
import {Node, Room, Floor, EditorMode} from "./types/graph";

import { angleTo, eucleadianDistance, lerp } from './utils/equations';
import { isTooClose, alignedLine, findClosestEdgePoint, isOnEdge, StreamDetections } from './utils/nodes';
import {saveFloorsState, loadFloorsState, importFloors, exportFloors, clearFloorState} from './utils/storage'
import { handleUpload } from './utils/functions';

// CSS
import './design.css'
import {Assets} from "./assets/index"
import { ShortcutsPopup } from './components/popups';
import { useCameraStream } from './hooks/useCameraStream';

function FloorPlanEditor() {
  // This line is going to try to load the data from internal storage, if it didn't work, it is gonig to return the fallback (test or dummy data here. )
  const [floors, setFloor] = useState<Floor[]>(() =>  loadFloorsState<Floor[]>([{floorName:"Test", rooms: [], bgURL:""}]))
  const [currentFloorIdx, setFloorIdx] = useState<number>(0)
  const [selectedRoomIdx, setSelectedRoomIdx] = useState<number>(-1)

  const [mode, setMode] = useState<EditorMode>("view")
  const [isHovering, setHovering] = useState<boolean>(false)
  const [hoveringMousePos, setHoveringMousePos] = useState({x:0, y:0, angle:0})
  
  const [showShortcuts, setShowShortcuts] = useState(false)
  
  // Refs
  const uploadFloorBGRef = useRef<HTMLInputElement>(null)
  const importFloorsRef = useRef<HTMLInputElement>(null)
  const stageRef = useRef<Konva.Stage>(null)
  let currentFloor = floors[currentFloorIdx]
  let currentRoomNodes = currentFloor.rooms.at(selectedRoomIdx)?.nodes
  const camerasStream = useCameraStream("ws://127.0.0.1:8000/dashboard/stream") ?? {test_camera_id: {isDanger: false, detection_metadata: []}}
  console.log("local server connection", camerasStream)

  // TODO, Test this here, you ight need to set
  const popNode = () => {
    setFloor(produce(prev => {
      const room = prev[currentFloorIdx].rooms[selectedRoomIdx]
      const nodes = room.nodes

      if (nodes.length >= 2){
        const a = nodes[nodes.length - 2]
        const b = nodes[nodes.length - 1]

        room.cameras = room.cameras.filter(camera => !isOnEdge(a, b, camera))
      } 
      nodes.pop()
    }))}
  const popCamera = () => setFloor(produce(prev => {prev[currentFloorIdx].rooms.at(selectedRoomIdx)?.cameras.pop()}))
  const popNearestCamera = () => {
    if (selectedRoomIdx === -1) return 

    setFloor(produce(prev => {
      const cameras = prev[currentFloorIdx].rooms[selectedRoomIdx].cameras
      if (cameras.length === 0) return 

      let closesIdx = 0
      let minDist = Infinity

      cameras.forEach((camera, idx) => {
          const dist = eucleadianDistance(camera, hoveringMousePos)
          if (dist < minDist){
            minDist = dist
            closesIdx = idx
          }
      })
      cameras.splice(closesIdx, 1)
    }))
  }

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent){
      switch (e.key){
        case "Escape":
          setMode("view")
          setSelectedRoomIdx(-1)
          break
        case "Delete":
          clearFloorState()
          // Remove the whole stored dashboard.
          setFloor([{floorName:"test", bgURL:"", rooms:[]}])
          setFloorIdx(0)
          alert("Local Storage has been deleted sccessfully")
          break
      }
    }
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  })
  
  const handleStageClick = (e) => {
    const button = e.evt.button;
    if (button === 0){  // Left click
      // Check if there is any other close node, If so, Don't create dublicates.
      var newNodePos = {x: hoveringMousePos.x, y:hoveringMousePos.y}

      if (mode === "draw"){

        // The new point must align with the old one. 90Deg
        console.log(currentRoomNodes)
        if (currentRoomNodes?.length !== 0) newNodePos = alignedLine({x:currentRoomNodes.at(-1).x, y:currentRoomNodes.at(-1).y}, newNodePos)
         
        // Check if the current point is close to any other points
        if(isTooClose(newNodePos, currentRoomNodes)){
          alert("Node is already too close to another node, Ignoring this one....")
          return;
        }

        setFloor(produce(prev => {prev[currentFloorIdx].rooms.at(selectedRoomIdx)?.nodes.push({x: newNodePos.x, y:newNodePos.y})}))
        console.log("New node added.")
        
      }else if(mode === "camera"){
        if(isTooClose(newNodePos, currentFloor.rooms.at(-1)?.cameras)){return;}

        let cameraId = prompt("Enter Camera ID: ")
        if (cameraId !== null && cameraId !== ""){
          setFloor(produce(prev => {prev[currentFloorIdx].rooms.at(selectedRoomIdx)?.cameras.push({id: cameraId, x: newNodePos.x, y:newNodePos.y, angle: hoveringMousePos.angle})}))
          console.log("New camera added.")
        }
      }

    }else if (button === 2){  // Right click
      if (mode === "draw"){
        popNode()
        // TODO remove also the camera related to this node.
        console.log("Node has been removed")
      }else if(mode === "camera"){
        // popCamera()
        popNearestCamera()
        console.log("Camera has been removed")
      }
    }
  }
  
  const handleStageHover = (e) => {
    const stage = e.target.getStage()
    let pos = stage.getPointerPosition()
    if (mode === "draw"){
      setHovering(true)
      setHoveringMousePos({x: pos.x / window.innerWidth, y:pos.y / window.innerHeight, angle:0})
    } else if(mode === "camera"){
      setHovering(true)
      pos = {x: pos.x / window.innerWidth, y:pos.y / window.innerHeight}
      const closest = findClosestEdgePoint(pos, currentRoomNodes, 0.1)
      closest
      ? setHoveringMousePos({x: closest.point.x, y:closest.point.y, angle:angleTo(closest.point, pos)})
      : setHovering(false)
    }else{
      setHovering(false)
    }
  }

  const handleBackgroundUpload = async (e) => {
    const bg = await handleUpload(e)
    // TODO check this again, i feel a missing thing here.
    setFloor(produce(prev => {prev[currentFloorIdx].bgURL = bg}))
  }

  return (
    <div style={{}}>
      <div style={{display: "flex"}}>
        <div style={{flex: 5}}>
          <h2 style={{textAlign: "center"}}> Tracking Dashboard </h2>
          {mode !== "view" && <h5 style={{textAlign:"center", color:"gray"}}>Please Press `Esc` to Exit the current mode of {currentFloor.rooms.at(selectedRoomIdx)?.id}</h5>} 
        </div>
        <div style={{display:"flex"}}>
          <button onClick={() => {setShowShortcuts(true)}}
          // style={{position: "absolute"}}
          >
            i
          </button>
        </div>
      </div>
      <input type="file" accept="image/*" onChange={(e) => handleBackgroundUpload(e)} title='Uploading 2D Floor Plane' style={{display:"none"}} ref={uploadFloorBGRef}/> 
      <input type="file" accept=".json" onChange={(e) => importFloors(e, setFloor)} title='Import Floors' style={{display:"none"}} ref={importFloorsRef}/> 

      {showShortcuts && <ShortcutsPopup close={() => setShowShortcuts(false)} />}

      <Stage 
      ref={stageRef} 
      width={window.innerWidth} 
      height={window.innerHeight / 1.5} 
      onMouseDown={handleStageClick}
      onContextMenu={(e) => {e.evt.preventDefault()}}  // Removing the Right click tool bar.
      onMouseMove={handleStageHover}
      >
        <Layer>
          {currentFloor.bgURL && <FloorBackground bgURL={currentFloor.bgURL} width={window.innerWidth} height={window.innerHeight / 1.5} />}
        </Layer>

        {/* Canvas for Drawing Nodes and Edges */}
        <Layer>

          {/* ------- Drawing Nodes and Edges ----------- */}
          {currentFloor.rooms.map((polygon, i) => 
              <EdgeNode nodes={polygon.nodes} key={i} color={selectedRoomIdx === i? "darkblue" : "black"} />
          )}
          
          {currentFloor.rooms.map((polygon, roomIdx) => 
            polygon.nodes.map((node, idx) => 
              <CircleNode pos={node} mode={mode} key={idx} color={selectedRoomIdx === roomIdx ? "darkblue" : "black"} 
                // onDragEnd={(e) => {
                //       const xNew = e.target.x() / window.innerWidth
                //       const yNew = e.target.y() / window.innerHeight
                //       setFloor(produce(prev => {
                //         prev[currentFloorIdx].rooms[selectedRoomIdx].nodes.map((n, i) => i === idx ? {...n, x: xNew, y:yNew} : n)
                //       }))
                //     }
                // }
                onSelect={() => {
                  console.log(roomIdx)
                  if (mode === "edit")
                    setSelectedRoomIdx(roomIdx)
                    setMode("draw")
                    }
                }
              />
          ))}

          {currentFloor.rooms.map((room, _) => 
            room.cameras.map((camera, i) =>
              // TODO, this is wrong, i should not pass the currentNodes, but the nodes of the floor this camera on. 
              
              <CameraNode pos={camera} icon={Assets.VideoCamera} rotation={camera.angle} key={i} cameraData={camerasStream[camera.id!]} roomNodes={room.nodes} />

          ))}

          {/* ----- Hovering State ------------ */}
          {isHovering && mode === "draw" && <CircleNode pos={hoveringMousePos} key={-1} mode={mode} isHovering="True"/> }
          {isHovering && mode === "camera" && <CameraNode icon={Assets.VideoCamera} pos={hoveringMousePos} rotation={hoveringMousePos.angle} key={-1} isHovering="True" /> }
          
        </Layer>
      </Stage>

    
      {/* Action Buttons */}
      <div style={{display:"flex", gap:50}}>
        <fieldset style={{flex:3, flexWrap:"wrap", display: "flex"}}>
            <legend>Actions</legend>
              <IconButton label="Save Dashboard" onClick={() => saveFloorsState(floors)} icon={Assets.saveFloorDesign}/>
              <IconButton label="Upload Dashboard" onClick={() => importFloorsRef.current?.click()} icon={Assets.importFloors}/>
              <IconButton label="Export Dashboard" onClick={() => exportFloors(floors)} icon={Assets.export}/>
              <IconButton label="Create Floor" onClick={() => setFloor(prev => {
                setSelectedRoomIdx(-1)
                return [...prev, {floorName: "test", bgURL:"", rooms:[]}]
                })} icon={Assets.createFloor}/>
              <IconButton label="Delete Floor" onClick={() => setFloor(produce(prev => {(floors.length !==1) && prev.splice(currentFloorIdx, 1); setFloorIdx(0)}))} icon={Assets.deleteFloor}/>
              <IconButton label="Upload Floor Plane" onClick={() => uploadFloorBGRef.current!.click()} icon={Assets.UploadFloorPlane}/>
              <IconButton label="Clear Nodes" onClick={() => {setFloor(produce(prev => {
                const room = prev[currentFloorIdx].rooms.at(selectedRoomIdx)
                if (room){
                  room.nodes = []
                  room.cameras = []
                }
              }))}} icon={Assets.clear}/>
            

            {(floors.length > 1) &&  
            <>
              <IconButton label="Previous Floor" onClick={() => {
                setFloorIdx(Math.max(0, currentFloorIdx - 1))
                setSelectedRoomIdx(-1)
                setMode("view")
                }} icon={Assets.arrow}  imgStyle={{transform:"rotate(180deg)"}}/>
              <span style={{textAlign:"center", fontSize:50, alignContent:"center"}}>{currentFloorIdx + 1}-{floors.length}</span>
              <IconButton label="Next Floor" onClick={() => {
                setFloorIdx(Math.min(floors.length - 1, currentFloorIdx + 1))
                setSelectedRoomIdx(-1)
                setMode("view")
                }} icon={Assets.arrow}/>
            </>}
            
        </fieldset>

        {/* --------- Modes -------  */}
        <fieldset style={{flex:1, flexWrap:"wrap", display: "flex"}}>
          <legend>Modes</legend>

          <IconButton label="Draw Mode" onClick={() => {
            if (selectedRoomIdx === -1){
              let roomName = prompt("Enter Room Name/ID: ", "Room") ?? "Room"
              let room: Room = {id: roomName, cameras: [], nodes:[]}
              setFloor(produce(prev => {prev[currentFloorIdx].rooms.push(room)}))
              setSelectedRoomIdx(currentFloor.rooms.length)
            }
            setMode("draw")
            }} icon={Assets.drawMode}/>

          <IconButton label="Camera Mode" onClick={() => {
            setMode("camera")
            }} icon={Assets.cameraMode}/>

          <IconButton label="Edit Mode" onClick={() => {
            setMode("edit")
            }} icon={Assets.editMode}/>

        </fieldset>
      </div>
    </div>
  )
}

export default FloorPlanEditor