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
            raw_input = await websocket.receive_text()
            print("Raw input:", raw_input)
            user_input = json.loads(raw_input)
            user_input = user_input["data"]
            print("User input:", user_input)
            if user_input.lower() == "exit":
                state["next_step"].append("end")
                break
            
            state["user_input"].append(user_input)
            state["next_step"].append("central_agent")

            # Invoke the workflow
            for step in workflow_app.stream(state):
                
                if state["next_step"][-1] == "central_agent":
                    # Send intermediate response to frontend
                    await websocket.send_text(json.dumps({
                        "type": "intermediate",
                        "message": state["generated_response"][-1]
                    }))
                    
                    user_input = await websocket.receive_text()
                    user_input = json.loads(user_input)
                    user_input = user_input["data"]
                    if user_input.lower() == "exit":
                        state["next_step"].append("end")
                        break
                    state["user_input"].append(user_input)
                    state["next_step"].append("central_agent")
            
            if user_input.lower() == "exit":
                break
    
            if state['generated_response']:
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