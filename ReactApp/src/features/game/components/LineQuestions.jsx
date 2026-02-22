import React from "react";
import DroppableSlot from "./DroppableSlot";

export default function LineQuestions({lineQuestions}){ //takes in the cards that are already placed on the number line 
    return (
      <>
        {lineQuestions.map((item, index) => ( //goes through each question already on the line; item (id, question), index(position in the array)
          <React.Fragment key={item.id}> {/* key required to track which card is which */}
            <DroppableSlot slotIndex={index} /> {/* renders teh droppable slot before the question, slotIndex decideds where to put it in the array */}
            <div className="number-box line-question-box">
              {item.question?.question ?? "Question"} {/* if question exists - show it, if not just show  the word "Question" to avoid crashes*/}
            </div>
          </React.Fragment>
        ))}

        {/* Final slot after the last question */}
        <DroppableSlot slotIndex={lineQuestions.length} />
      </>
    );
  }