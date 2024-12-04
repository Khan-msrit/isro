import React from "react";
import "../styles/MessageBubble.css";

function MessageBubble({ message, sender }) {
  return (
    <div className={`message-bubble ${sender === "user" ? "user" : "bot"}`}>
      <p>{message}</p>
    </div>
  );
}

export default MessageBubble;
