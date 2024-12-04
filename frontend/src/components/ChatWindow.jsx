import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import MessageBubble from "./MessageBubble";
import InputBox from "./InputBox";
import "../styles/ChatWindow.css";

function ChatWindow() {
    const [messages, setMessages] = useState([
        { sender: "bot", message: "Hi! I'm ChatBot. How can I assist you today?", timestamp: new Date() },
    ]);
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef(null);

    // State for theme toggle
    const [isDarkMode, setIsDarkMode] = useState(false);

    const toggleTheme = () => {
        setIsDarkMode((prevMode) => !prevMode);
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSendMessage = async (userMessage) => {
        setMessages((prevMessages) => [
            ...prevMessages,
            { sender: "user", message: userMessage, timestamp: new Date() },
        ]);

        setIsTyping(true); // Show typing indicator
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
                timestamp: new Date(),
            }));

            setMessages((prevMessages) => [...prevMessages, ...botMessages]);
        } catch (error) {
            console.error("Error communicating with Rasa:", error);
            setMessages((prevMessages) => [
                ...prevMessages,
                { sender: "bot", message: "Oops! Something went wrong.", timestamp: new Date() },
            ]);
        } finally {
            setIsTyping(false); // Hide typing indicator
        }
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
                    <MessageBubble
                        key={index}
                        sender={msg.sender}
                        message={msg.message}
                        timestamp={msg.timestamp}
                    />
                ))}
                {isTyping && <div className="typing-indicator">ChatBot is typing...</div>}
                <div ref={messagesEndRef} />
            </div>
            <InputBox onSend={handleSendMessage} />
        </div>
    );
}

export default ChatWindow;
