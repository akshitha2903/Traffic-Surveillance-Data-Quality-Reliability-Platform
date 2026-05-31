import asyncio
import random
from datetime import datetime, timezone
import httpx

# Configuration
BACKEND_URL = "http://localhost:8000"
SIMULATION_INTERVAL = 10.0  # seconds between sends

CAMERAS = [
    {
        "id": "cam-kr-puram",
        "name": "KR Puram Hanging Bridge",
        "location": "KR Puram",
        "base_traffic": 120,
        "base_speed": 40.0,
    },
    {
        "id": "cam-tc-palya",
        "name": "TC Palya Junction",
        "location": "TC Palya",
        "base_traffic": 80,
        "base_speed": 45.0,
    },
    {
        "id": "cam-silk-board",
        "name": "Silk Board Junction",
        "location": "Silk Board",
        "base_traffic": 250,
        "base_speed": 12.0,  # High traffic, slow speed!
    },
    {
        "id": "cam-indiranagar",
        "name": "Indiranagar 100ft Rd",
        "location": "Indiranagar",
        "base_traffic": 90,
        "base_speed": 35.0,
    },
    {
        "id": "cam-mvit-sadahalli",
        "name": "MVIT Sadahalli Gate",
        "location": "Sadahalli",
        "base_traffic": 40,
        "base_speed": 75.0,  # Highway speed!
    },
]


async def register_cameras(client: httpx.AsyncClient):
    """Register all defined cameras with the backend on startup."""
    print("--- Registering Cameras ---")
    for cam_info in CAMERAS:
        payload = {
            "id": cam_info["id"],
            "name": cam_info["name"],
            "location": cam_info["location"],
            "status": "active",
            "is_active": True,
        }
        try:
            response = await client.post(f"{BACKEND_URL}/api/cameras", json=payload)
            if response.status_code in [200, 201]:
                print(f"✔ Registered camera: {cam_info['id']} ({cam_info['name']})")
            else:
                print(f"❌ Failed to register {cam_info['id']}: Status {response.status_code}")
        except httpx.RequestError as e:
            print(f"❌ Connection error registering {cam_info['id']}: {e}")
            raise SystemExit("Ensure the backend server is running before starting the simulator.")
    print("---------------------------\n")


async def simulate_camera(client: httpx.AsyncClient, cam_info: dict):
    """Simulate telemetry and heartbeat updates for a single camera."""
    cam_id = cam_info["id"]
    print(f"Starting simulation loop for: {cam_id}")

    while True:
        try:
            # 1. Decide Status & Latency
            # Simulate occasional transient issues (5% chance of degradation, 2% error)
            rand_val = random.random()
            if rand_val < 0.02:
                status = "error"
            elif rand_val < 0.07:
                status = "degraded"
            else:
                status = "ok"

            latency = random.randint(10, 150)
            
            # Send Heartbeat
            heartbeat_payload = {
                "camera_id": cam_id,
                "status": status,
                "latency_ms": latency,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            await client.post(f"{BACKEND_URL}/api/heartbeats", json=heartbeat_payload)
            print(f"[{cam_id}] Heartbeat: status={status}, latency={latency}ms")

            # 2. Simulate Traffic Telemetry if status is not 'error' (offline)
            if status != "error":
                # Add some random variance to vehicle count and speed
                traffic_variance = random.randint(-20, 20)
                vehicle_count = max(0, cam_info["base_traffic"] + traffic_variance)

                speed_variance = random.uniform(-5.0, 5.0)
                average_speed = max(2.0, cam_info["base_speed"] + speed_variance)

                # Inject occasional anomalies for testing (3% chance of high counts/speeds)
                anomaly_roll = random.random()
                if anomaly_roll < 0.02:
                    # High traffic anomaly
                    vehicle_count = 550
                    print(f"[{cam_id}] ⚠️ Simulating high vehicle count anomaly!")
                elif anomaly_roll < 0.04:
                    # High speed anomaly
                    average_speed = 165.0
                    print(f"[{cam_id}] ⚠️ Simulating high speed anomaly!")

                traffic_payload = {
                    "camera_id": cam_id,
                    "vehicle_count": vehicle_count,
                    "average_speed": round(average_speed, 2),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                traffic_res = await client.post(f"{BACKEND_URL}/api/traffic", json=traffic_payload)
                
                # Check response to see if it flagged an anomaly
                if traffic_res.status_code == 201:
                    data = traffic_res.json()
                    if data.get("anomalous"):
                        print(f"[{cam_id}] Alert: Backend flagged data as anomalous! Reason: {data.get('anomaly_reason')}")
                    else:
                        print(f"[{cam_id}] Traffic: {vehicle_count} cars, avg speed {traffic_payload['average_speed']} km/h")

        except httpx.RequestError as e:
            print(f"[{cam_id}] Ingestion network error: {e}")

        # Sleep before sending the next telemetry batch
        await asyncio.sleep(SIMULATION_INTERVAL + random.uniform(-1.0, 1.0))


async def main():
    print("==================================================")
    print("   Traffic Quality Platform - Camera Simulator")
    print("==================================================")
    
    # We use a persistent HTTPX client connection pool
    async with httpx.AsyncClient(timeout=5.0) as client:
        # First register all cameras
        await register_cameras(client)
        
        # Start simulation loop for all cameras concurrently
        tasks = [simulate_camera(client, cam) for cam in CAMERAS]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSimulator stopped by user.")
