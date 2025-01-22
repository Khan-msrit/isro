import React from "react";

function GraphDisplay() {
  return (
    <div>
      <h2>Graph Output</h2>
      {/* Update the src URL to match your backend graph endpoint */}
      <img
        src="http://localhost:5055/static/graphs/graph_output.png"
        alt="Graph Output"
        style={{ maxWidth: "100%", height: "auto", border: "1px solid #ddd" }}
      />
    </div>
  );
}

export default GraphDisplay;
