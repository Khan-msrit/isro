// // import React from "react";
// // import "../styles/MessageBubble.css";

// // function MessageBubble({ message, sender, timestamp }) {
// //     const formattedTime = timestamp
// //         ? new Date(timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
// //         : "";

// //     return (
// //         <div className={`message-bubble ${sender === "user" ? "user" : "bot"}`}>
// //             <p>{message}</p>
// //             <span className="timestamp">{formattedTime}</span>
// //         </div>
// //     );
// // }

// // export default MessageBubble;

// import React from "react";
// import {
//     LineChart,
//     Line,
//     XAxis,
//     YAxis,
//     CartesianGrid,
//     Tooltip,
//     Legend,
// } from "recharts";
// import "../styles/MessageBubble.css";

// function MessageBubble({ message, sender, timestamp, graphData }) {
//     const formattedTime = timestamp
//         ? new Date(timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
//         : "";

//     return (
//         <div className={`message-bubble ${sender === "user" ? "user" : "bot"}`}>
//             {graphData ? (
//                 <div className="graph-container">
//                     <LineChart width={300} height={200} data={graphData}>
//                         <CartesianGrid strokeDasharray="3 3" />
//                         <XAxis dataKey="name" />
//                         <YAxis />
//                         <Tooltip />
//                         <Legend />
//                         <Line type="monotone" dataKey="value" stroke="#8884d8" />
//                     </LineChart>
//                 </div>
//             ) : (
//                 <p>{message}</p>
//             )}
//             <span className="timestamp">{formattedTime}</span>
//         </div>
//     );
// }

// export default MessageBubble;
// import React from "react";
// import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts";
// import "../styles/MessageBubble.css";

// function MessageBubble({ message, sender, timestamp, graphData }) {
//     const formattedTime = timestamp
//         ? new Date(timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
//         : "";

//     return (
//         <div className={`message-bubble ${sender === "user" ? "user" : "bot"}`}>
//             {graphData ? (
//                 <div className="graph-container">
//                     <LineChart width={300} height={200} data={graphData}>
//                         <CartesianGrid strokeDasharray="3 3" />
//                         <XAxis dataKey="name" />
//                         <YAxis />
//                         <Tooltip />
//                         <Legend />
//                         <Line type="monotone" dataKey="value" stroke="#8884d8" />
//                     </LineChart>
//                 </div>
//             ) : (
//                 <p>{message}</p>
//             )}
//             <span className="timestamp">{formattedTime}</span>
//         </div>
//     );
// }

// export default MessageBubble;


// import React, { useState } from "react";
// import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts";
// import "../styles/MessageBubble.css";

// function MessageBubble({ message, sender, timestamp, graphData }) {
//     const [isModalOpen, setIsModalOpen] = useState(false); // Modal state

//     const formattedTime = timestamp
//         ? new Date(timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
//         : "";

//     // Open the modal
//     const openModal = () => {
//         if (graphData) setIsModalOpen(true);
//     };

//     // Close the modal
//     const closeModal = () => setIsModalOpen(false);

//     // Download graph as an image
//     const downloadGraph = () => {
//         const canvas = document.querySelector("canvas"); // Target the chart's canvas
//         const link = document.createElement("a");
//         link.href = canvas.toDataURL("image/png");
//         link.download = "graph.png"; // Default download file name
//         link.click();
//     };

//     return (
//         <div className={`message-bubble ${sender === "user" ? "user" : "bot"}`}>
//             {graphData ? (
//                 <div className="graph-container" onClick={openModal} style={{ cursor: "pointer" }}>
//                     <LineChart width={300} height={200} data={graphData}>
//                         <CartesianGrid strokeDasharray="3 3" />
//                         <XAxis dataKey="name" />
//                         <YAxis />
//                         <Tooltip />
//                         <Legend />
//                         <Line type="monotone" dataKey="value" stroke="#8884d8" />
//                     </LineChart>
//                     <p style={{ fontSize: "small", textAlign: "center" }}>Click to enlarge</p>
//                 </div>
//             ) : (
//                 <p>{message}</p>
//             )}
//             <span className="timestamp">{formattedTime}</span>

//             {/* Modal for Full-Screen Graph */}
//             {isModalOpen && (
//                 <div
//                     style={{
//                         position: "fixed",
//                         top: 0,
//                         left: 0,
//                         width: "100vw",
//                         height: "100vh",
//                         backgroundColor: "rgba(0, 0, 0, 0.8)",
//                         display: "flex",
//                         justifyContent: "center",
//                         alignItems: "center",
//                         zIndex: 1000,
//                     }}
//                     onClick={closeModal}
//                 >
//                     <div
//                         style={{
//                             position: "relative",
//                             backgroundColor: "#fff",
//                             padding: "20px",
//                             borderRadius: "10px",
//                             width: "90%",
//                             height: "90%",
//                             overflow: "auto",
//                         }}
//                         onClick={(e) => e.stopPropagation()} // Prevent modal close on content click
//                     >
//                         <LineChart width={800} height={600} data={graphData}>
//                             <CartesianGrid strokeDasharray="3 3" />
//                             <XAxis dataKey="name" />
//                             <YAxis />
//                             <Tooltip />
//                             <Legend />
//                             <Line type="monotone" dataKey="value" stroke="#8884d8" />
//                         </LineChart>
//                         <button
//                             onClick={downloadGraph}
//                             style={{
//                                 position: "absolute",
//                                 top: "10px",
//                                 right: "10px",
//                                 backgroundColor: "#007BFF",
//                                 color: "white",
//                                 border: "none",
//                                 padding: "10px 20px",
//                                 borderRadius: "5px",
//                                 cursor: "pointer",
//                             }}
//                         >
//                             Download
//                         </button>
//                         <button
//                             onClick={closeModal}
//                             style={{
//                                 position: "absolute",
//                                 top: "10px",
//                                 left: "10px",
//                                 backgroundColor: "red",
//                                 color: "white",
//                                 border: "none",
//                                 padding: "10px 20px",
//                                 borderRadius: "5px",
//                                 cursor: "pointer",
//                             }}
//                         >
//                             Close
//                         </button>
//                     </div>
//                 </div>
//             )}
//         </div>
//     );
// }

// export default MessageBubble;

import React, { useState } from "react";
import Modal from "react-modal"; // Import the modal library
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts";
import "../styles/MessageBubble.css";

// Modal styling (can be customized further)
const modalStyles = {
    overlay: {
        backgroundColor: "rgba(0, 0, 0, 0.7)",
        zIndex: 1000,
    },
    content: {
        top: "50%",
        left: "50%",
        right: "auto",
        bottom: "auto",
        marginRight: "-50%",
        transform: "translate(-50%, -50%)",
        backgroundColor: "#fff",
        padding: "20px",
        borderRadius: "8px",
        width: "90%",
        maxWidth: "900px", // Limit max width for large screens
        height: "auto",
        maxHeight: "90vh", // Limit height to fit within viewport
        overflow: "auto", // Scroll if content overflows
    },
};

function MessageBubble({ message, sender, timestamp, graphData }) {
    const [isModalOpen, setIsModalOpen] = useState(false);

    const formattedTime = timestamp
        ? new Date(timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
        : "";

    const handleOpenModal = () => setIsModalOpen(true);
    const handleCloseModal = () => setIsModalOpen(false);

    return (
        <div className={`message-bubble ${sender === "user" ? "user" : "bot"}`}>
            {/* Render graph */}
            {graphData && (
                <>
                    <div className="graph-container" onClick={handleOpenModal} style={{ cursor: "pointer" }}>
                        <LineChart width={300} height={200} data={graphData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line type="monotone" dataKey="value" stroke="#8884d8" />
                        </LineChart>
                        <p className="enlarge-tip">Click to enlarge</p>
                    </div>

                    {/* Modal for enlarged graph */}
                    <Modal isOpen={isModalOpen} onRequestClose={handleCloseModal} style={modalStyles} ariaHideApp={false}>
                        <h3 style={{ textAlign: "center" }}>Detailed Graph View</h3>
                        <LineChart width={800} height={500} data={graphData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line type="monotone" dataKey="value" stroke="#8884d8" />
                        </LineChart>
                        <button className="close-modal" onClick={handleCloseModal}>
                            Close
                        </button>
                    </Modal>
                </>
            )}

            {/* Render table */}
            {graphData && (
                <div className="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Timestamp</th>
                                <th>Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            {graphData.map((row, index) => (
                                <tr key={index}>
                                    <td>{row.name}</td>
                                    <td>{row.value}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {/* Fallback for messages without graph or table data */}
            {!graphData && <p>{message}</p>}
            <span className="timestamp">{formattedTime}</span>
        </div>
    );
}

export default MessageBubble;
