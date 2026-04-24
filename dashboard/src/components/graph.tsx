import React, { useState } from "react"
import { Line, Circle, Image as KonvaImage, Stage, Layer, Text, Rect, Group } from "react-konva"
import useImage from "use-image"
import { Node } from "../types/graph"
import { placeDepthPointOnRay, placeDetectionPoint, StreamDetections } from "../utils/nodes"

// We created interface here, as this one is for a ui compoenent, and the input must be only one object, which is dict here. 
interface CircleNodeProps{pos, mode, key, color?:string, onDragEnd?: (e) => void, onSelect?: () => void, isHovering}
export function CircleNode({pos, mode, key, color="black", onDragEnd, onSelect, isHovering=false}: CircleNodeProps){
  // Note that i transfered x and y to percentages, and i return them back again here. 
  return (
    <Circle
      key={key+1}
      x={pos.x * window.innerWidth}
      y={pos.y * window.innerHeight}
      fill= {color}
      opacity={isHovering ? 0.5 : 1}
      stroke="gray"
      radius={12}
      // draggable={mode === "edit"} // TODO Fix this, also previous nodes in other rooms are draggable, fix this. 
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
        strokeWidth={7}
        lineJoin='round'
        lineCap='round'
        closed={true}
      />
    )
  }


export function CameraNode({icon, pos, rotation=0, key, isHovering=false, cameraData={is_danger: false, detection_metadata:[]} as StreamDetections, roomNodes=[] as Node[]}){
  const [image] = useImage(icon)
  let detectionPoints:Node[] | null = []
  // let [hoveringOnCamera, setHoveringOnCamera] = useState<boolean>(false)

  if (cameraData.detection_metadata !==0 && roomNodes.length !== 0) {
    detectionPoints = cameraData.detection_metadata
    .map((d) => placeDetectionPoint(pos, rotation, d, roomNodes))
    .filter((p): p is Node => p !== null)
  }

  return (
    <>
     {!isHovering && <StatusMark pos={pos} color={cameraData.is_danger ? "red" : "green"} />}
          
     <KonvaImage 
      image={image}
      x={pos.x * window.innerWidth}
      y={pos.y * window.innerHeight}
      alt='CameraNode'
      key={key + 1}
      opacity={isHovering? 0.7 : 1}
      rotation={rotation}
      offsetX={32.5}
      offsetY={32.5}  // This should be half the width
      width={65} 
      height={65}
      // onMouseEnter={() => {setHoveringOnCamera(true); console.log("in")}}
      // onMouseLeave={() => {setHoveringOnCamera(false); console.log("out")}}
      />

      {detectionPoints.map((pt, i) => (
        <Line 
          points={[
            pos.x * window.innerWidth,
            pos.y * window.innerHeight,
            pt.x * window.innerWidth,
            pt.y * window.innerHeight
          ]}
          stroke={cameraData.is_danger ? "red" : "green"}
          strokeWidth={1.5}
          dash={[6, 4]}
          opacity={0.5}
        />
      ))}

      {detectionPoints.map((pt, i) => (
        <Circle
          key={i}
          x = {pt.x * window.innerWidth}
          y = {pt.y * window.innerHeight}
          radius={8}
          fill={cameraData.is_danger ? "red" : "green"}
          stroke="black"
          opacity={0.9}
        />
     ))}
    </>
  )
}

export function StatusMark({pos, color="green"}){
  const radious = [70, 55, 40] 
  return (
    <>
    {radious.map((rad, i) => 
        <Circle key={i} x={pos.x * window.innerWidth} y={pos.y * window.innerHeight} fill={color} radius={rad} opacity={(i+1)/5}/>
    )}
    </>
  )  
}