import asyncio
import websockets
import json

async def test_websocket():
    try:
        print("Connecting to ws://localhost:8002/ws...")
        ws = await asyncio.wait_for(
            websockets.connect('ws://localhost:8002/ws'), 
            timeout=5
        )
        print("✅ Connected!")
        
        # Receive initial message
        msg = await asyncio.wait_for(ws.recv(), timeout=5)
        print(f"📩 Received: {msg}")
        
        # Wait for a price update
        print("Waiting for price update...")
        msg = await asyncio.wait_for(ws.recv(), timeout=10)
        print(f"📩 Received: {msg}")
        
        await ws.close()
        print("✅ Test complete")
        
    except asyncio.TimeoutError:
        print("❌ Timeout - WebSocket not responding")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
