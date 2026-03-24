import {eucleadianDistance, lerp} from "./equations"


export function isTooClose(newNodePosition, nodes){
    /**
     * Check if the new position is too close to any other node, to avoide overlapping. 
     * @param newNodePosition - Could be the current mouse pos
     * @param nodes - List of nodes to check 
     * @returns bool represents if there is already a node near this pos. 
     */
    for (const node of nodes){   // I just noticed that `of` differ from `in` unline python.  
        const distance = eucleadianDistance(newNodePosition, {x: node.x, y:node.y})
        const MIN_DISTANCE = 0.05
        if (distance < MIN_DISTANCE){
            return true;   // Node is too close to an existing one. 
        }
    }
    return false;  // Node is not close to any other one. 
}

export function alignedLine(oldPoint, newPoint){
    /**
     * Adding a calculated aligned node instead of just random node, it should be 90 aligned.
     * @param oldPoint - the old point module
     * @param newPoint - the new point module
     * @returns point aligned 90deg with it. 
     */
    const dx = Math.abs(oldPoint.x - newPoint.x)
    const dy = Math.abs(oldPoint.y - newPoint.y)
    if ((dx - dy) < 0) {
      return {x: oldPoint.x, y: newPoint.y}
    }
    return {x: newPoint.x, y: oldPoint.y}
  }

import { Node } from "../types/graph";
export function closestPointOnSegment(P:Node, A:Node, B:Node){
    /**
     * @param P - Represents the node around the segment. (Cursor Pos)
     * @param A - Represent the first point that represents the Segment. (Point on the edge)
     * @param B - Represent the second point that represents the Segment.
     * Note that the segment like a line with two ends (Nodes at the end.)
     * @returns point, t (place or percentage on that line.)
     */
    // AB = B - A
    const AB = {x: B.x - A.x, y: B.y - A.y}  // Edge direction vector A -> B
    // AP = P - A
    const AP = {x: P.x - A.x, y: P.y - A.y}  // Vector from A to Cursor (P)

    // AB.x ^ 2 + AB.y ^ 2
    const lengthSq = AB.x * AB.x + AB.y * AB.y

    // A, B are the same point. 
    if (lengthSq === 0) return {point: A, t: 0} 

    // How much AP piont in the direction of AB. 
    const dot = AP.x * AB.x + AP.y * AB.y
    // Normalizing
    const tRaw = dot / lengthSq

    // clamp to [0, 1]
    const t = Math.max(0, Math.min(1, tRaw))

    const point = {
        x: A.x + t * AB.x,
        y: A.y + t * AB.y
    }

    return {point, t}
}

export function isOnEdge(a:Node, b:Node, point:Node){
    /**
     * Is this camera point sitting on the line segment between a and b
     * This  is the question that this function is trying to answer
     * 
     */
    

    // Direction vector of a to b. 
    const ab = {x: b.x - a.x, y: b.y - a.y}
    // Direction vector of a to point 
    const ap = {x: point.x - a.x, y: point.y - a.y}

    // These two lines are to check if the point is really on the line.
    // const cross = ab.x * ap.y - ab.y * ap.x
    // const thresh = 0.01
    // if (Math.abs(cross) > thresh) return false

    const dot = ap.x * ab.x + ap.y * ab.y
    const lenSq = ab.x * ab.x + ab.y * ab.y

    // Confirming the point is behind a and beyond b
    // console.log(dot >= 2 && dot <= lenSq)
    return dot >= 0 && dot <= lenSq
  }

export function findClosestEdgePoint(cursor: Node, nodes: Node[], threshold = 0.05){
    if (nodes.length < 2) return null

    let closest
    let minDist = Infinity

    for (let i = 0; i < nodes.length; i++){
        // Creating the Segment. 
        const A = nodes.at(i - 1)
        const B = nodes[i]

        // Measure how far the cursor is from that closest point
        const {point} = closestPointOnSegment(cursor, A, B)
        const dist = eucleadianDistance(cursor, point)

        if (dist < minDist && dist < threshold){
            minDist = dist
            closest = {point, edgeIndex: i}
        }
    }
    return closest
}


export function placeDepthPointOnRay(
    cameraPos:Node,
    cameraAngleDeg:number,
    depthRatio: number,
    roomNodes: Node[]
  ): Node | null{
    /**
     * From the camera position, Calculate the distance till the edge of the room.
     * Place a point represents a detection based on depth ratio
     */
  
    // At leasat 3 points
    if (roomNodes.length < 3) return null
  
    // Clippting depthRatio just as validator to be in 0 to 1 ratio.
    const t = Math.max(0, Math.min(1, depthRatio))
  
    // Convert camera angle from degree to radian.
    const angleRad = (cameraAngleDeg * Math.PI) / 180
    // Unit direction
    const dir = {
      x: Math.cos(angleRad),
      y: Math.sin(angleRad)
    }

    // Nearest intersection on the ray
    let bestU = Number.POSITIVE_INFINITY
    let hit:Node | null = null
    
    for (let i = 0; i < roomNodes.length; i++){
        const A = roomNodes[i]
        const B = roomNodes[(i + 1) % roomNodes.length]

        // Edge vector
        const S = {x: B.x - A.x, y: B.y - A.y}

        const denom = dir.x * S.y - dir.y * S.x
        if (Math.abs(denom) < 1e-9) continue;

        const AC = {x: A.x - cameraPos.x, y: A.y - cameraPos.y}
        const u = (AC.x * S.y - AC.y * S.x) / denom
        const v = (AC.x * dir.y - AC.y * dir.x) / denom

        const uMin = 1e-4
        if (u >= uMin && v >= 0 && v <= 1 && u < bestU){
            bestU = u
            hit = {
                x: cameraPos.x + u * dir.x,
                y: cameraPos.y + u * dir.y
            }
        }
    }

    if (!hit) return null
    return {
        x: lerp(cameraPos.x, hit.x, t),
        y: lerp(cameraPos.y, hit.y, t)
    } 
  }