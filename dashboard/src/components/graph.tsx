import React from "react"
import { Line, Circle, Image as KonvaImage, Stage, Layer } from "react-konva"
import useImage from "use-image"
import { Node } from "../types/graph"
import { placeDepthPointOnRay } from "../utils/nodes"

// We created interface here, as this one is for a ui compoenent, and the input must be only one object, which is dict here. 
interface CircleNodeProps{pos, mode, key, color?:string, onDragEnd?: (e) => void, onSelect?: () => void}
export function CircleNode({pos, mode, key, color="black", onDragEnd, onSelect}: CircleNodeProps){
  // Note that i transfered x and y to percentages, and i return them back again here. 
  return (
    <Circle
      key={key+1}
      x={pos.x * window.innerWidth}
      y={pos.y * window.innerHeight}
      fill= {color}
      opacity={key === -1 ? 0.1 : 1}
      stroke="gray"
      radius={10}
      draggable={mode === "edit"} // TODO Fix this, also previous nodes in other rooms are draggable, fix this. 
      onDragEnd={onDragEnd}
      onclick={onSelect}
    />
  )
}

export function EdgeNode({nodes, key, color="black"}){
    return (
      <Line
        points={nodes.flatMap(node => [node.x * window.innerWidth, node.y * window.innerHeight])}
        stroke={color}
        key={key+1}
        strokeWidth={3}
        lineJoin='round'
        lineCap='round'
        closed={true}
      />
    )
  }


export function CameraNode({icon, pos, rotation=0, key, cameraData={hasDanger: false, depthPoints:[] as number[]}, roomNodes=[] as Node[]}){
  const [image] = useImage(icon)
  let depthPoints:Node[] | null = []
  console.log("Camera Nodes", cameraData)
  console.log("Room Nodes", roomNodes)

  if (cameraData.depthPoints.length !== 0 && roomNodes.length !== 0) {
    for (let depth of cameraData.depthPoints){
      const p = placeDepthPointOnRay(pos, rotation, Number(depth), roomNodes)
      p !== null && depthPoints.push(p)
    }
  }
  console.log(depthPoints)
  return (
    <>
     <StatusMark pos={pos} color={cameraData.hasDanger ? "red" : "green"} />
          
     <KonvaImage 
      image={image} 
      x={pos.x * window.innerWidth}
      y={pos.y * window.innerHeight}
      alt='CameraNode'
      key={key+1}
      opacity={key === -1 ? 0.5 : 1}
      rotation={rotation}
      offsetX={25}
      offsetY={25}
      width={50} 
      height={50}
      />

      {depthPoints.map((pt, i) => (
        <Circle
          key={i}
          x = {pt.x * window.innerWidth}
          y = {pt.y * window.innerHeight}
          radius={8}
          fill="black"
          stroke="black"
          opacity={0.9}
        />
     ))}
    </>
   
  )
}
export function StatusMark({pos, color="green"}){
  const radious = [60, 45, 30] 
  return (
    <>
    {radious.map((rad, i) => 
        <Circle key={i} x={pos.x * window.innerWidth} y={pos.y * window.innerHeight} fill={color} radius={rad} opacity={(i+1)/10}/>
    )}
    </>
  )  
}
