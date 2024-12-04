import React from "react";
import "../styles/MessageBubble.css";

function MessageBubble({ message, sender, timestamp }) {
    const formattedTime = timestamp
        ? new Date(timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
        : "";

    return (
        <div className={`message-bubble ${sender === "user" ? "user" : "bot"}`}>
            <p>{message}</p>
            <span className="timestamp">{formattedTime}</span>
        </div>
    );
}

export default MessageBubble;
