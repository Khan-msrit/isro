import React, { useState } from "react";
import axios from "axios";
import MessageBubble from "./MessageBubble";
import InputBox from "./InputBox";
import "../styles/ChatWindow.css";

function ChatWindow() {
  const [messages, setMessages] = useState([
    { sender: "bot", message: "Hi! I'm ChatBot. How can I assist you today?" },
  ]);
  const [isDarkMode, setIsDarkMode] = useState(false);

  const handleSendMessage = async (userMessage) => {
    setMessages((prevMessages) => [
      ...prevMessages,
      { sender: "user", message: userMessage },
    ]);

    try {
      const response = await axios.post(
        "http://localhost:5005/webhooks/rest/webhook",
        {
          sender: "user",
          message: userMessage,
        }
      );

      const botMessages = response.data.map((msg) => ({
        sender: "bot",
        message: msg.text,
      }));

      setMessages((prevMessages) => [...prevMessages, ...botMessages]);
    } catch (error) {
      console.error("Error communicating with Rasa:", error);
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          sender: "bot",
          message: "Oops! Something went wrong. Please try again later.",
        },
      ]);
    }
  };

  const toggleTheme = () => {
    setIsDarkMode((prevMode) => !prevMode);
  };

  return (
    <div className={`chat-window ${isDarkMode ? "dark-mode" : "light-mode"}`}>
      <div className="header">
        ChatBot
        <button className="theme-toggle" onClick={toggleTheme}>
          {isDarkMode ? "Light Mode" : "Dark Mode"}
        </button>
      </div>
      <div className="messages">
        {messages.map((msg, index) => (
          <MessageBubble key={index} sender={msg.sender} message={msg.message} />
        ))}
      </div>
      <InputBox onSend={handleSendMessage} />
    </div>
  );
}

export default ChatWindow;
