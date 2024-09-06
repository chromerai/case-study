from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import json
from .workflow import workflow_app, State


fastapi_app = FastAPI()

# Add CORS middleware
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@fastapi_app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        state = State(
            user_input=[],
            conversation_history=[],
            extracted_info={},
            tool_output={},
            next_step=[],
            tool_explanation=[],
            generated_response=[],
            feedback=""
        )

        
        while True:
            user_input = await websocket.receive_text()
            user_input = json.loads(user_input)
            user_input = user_input["data"]
            if user_input.lower() == "exit":
                state["next_step"] = "end"
                break
            
            state["user_input"].append(user_input)
            state["next_step"].append("central_agent")

            # Invoke the workflow
            for step in workflow_app.stream(state):
                
                if state["next_step"][-1] == "central_agent":
                    print(f"state: `{state}`")
                    print(json.dumps({
                        "type": "intermediate",
                        "message": state["generated_response"][-1]
                    }))
                    # Send intermediate response to frontend
                    await websocket.send_text(json.dumps({
                        "type": "intermediate",
                        "message": state["generated_response"][-1]
                    }))
                    
                    user_input = await websocket.receive_text()
                    user_input = json.loads(user_input)
                    user_input = user_input["data"]
                    if user_input.lower() == "exit":
                        state["next_step"] = "end"
                    state["user_input"].append(user_input)
                    state["next_step"].append("central_agent")

    
            if state["next_step"][-1] == 'end':
                print("Sending final message:", state["generated_response"][-1])
                # Send final response to frontend
                await websocket.send_text(json.dumps({
                    "type": "final",
                    "message": state["generated_response"][-1]
                }))
                

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)