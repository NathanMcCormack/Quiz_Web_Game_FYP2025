import React from "react";
import { useDraggable } from "@dnd-kit/core";

export default function CurrentQuestionCard({question, isDisabled}){
    //attributes - , listneers - event handlers (cursor change...), setNodeRef - pass this to the element uou want to be draggable (DnD Kit), transform - how far its being dragged, isDragging - Boolean (useful fo rCSS)
    const { attributes, listeners, setNodeRef, transform, isDragging } = 
      useDraggable({
        id: "current-card", //unique id for draggable card 
        disabled: !question || isDisabled, // dont drag when no question
    });

    const style = {
      transform: transform ? `translate3d(${transform.x}px, ${transform.y}px, 0)` : undefined, //if transform exists (how far the item has been dragged), move the element by Xpx & Ypx
      opacity: isDragging ? 0.8 : 1, //if dragging opacacity becomes .8 to be more obvious that user is dragging card
      cursor: question ? "grab" : "default", //if the cursor is over the question, it will have a grab icon 
    };

  return (
    <div ref={setNodeRef} style={style} className="current-question" {...attributes} {...(question ? listeners : {})}> {/* attributes - nice to have for accessibility features for DnD kit */}
      <strong>Current question:</strong>                                             {/* if a question exists it becomes listeners (event handlers are attached), if not - nothing */}
      <div className="current-question-text">
        {question ? question.question : "Loading..."}
      </div>
      <p className="current-question-hint">
        Drag this card and drop it between 0 and ∞
      </p>
    </div>
  );
  }