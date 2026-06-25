import asyncio
import sys

async def test_websocket():
    try:
        import websockets
    except ImportError:
        print("[ERROR] 'websockets' package is not installed in this Python environment.")
        print("Please run: pip install websockets")
        return

    uri = "ws://localhost:8080/api/v1/documents/test-doc-id/ws"
    print(f"Attempting to connect to: {uri}")
    try:
        async with websockets.connect(uri) as websocket:
            print("[SUCCESS] Connected to WebSocket successfully!")
            # Send a dummy message to see if connection holds
            await websocket.send("ping")
            print("Sent ping.")
            # Connection will hold or close
            await asyncio.sleep(1)
    except Exception as e:
        print(f"[FAILED] Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
