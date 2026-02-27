import React from "react";
import { useDroppable } from "@dnd-kit/core";

export default function DroppableSlot({slotIndex}){
  //isOver - when a draggable item is over the drop zone
    const { setNodeRef, isOver } = useDroppable({ id: `slot-${slotIndex}`}); //useDroppable - from DnD kit, turns component into a drop zone. id = "slot-xxx"

    //This div creates the drop zone
    return (
      <div ref={setNodeRef} className={`drop-slot ${isOver ? "drop-slot--active" : ""}`}/>
    );
  }