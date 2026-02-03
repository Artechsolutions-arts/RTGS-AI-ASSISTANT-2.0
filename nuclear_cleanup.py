import subprocess
import time

print("=== NUCLEAR OPTION: Delete ALL Dashboard API workflows ===\n")

# Get all Dashboard API workflow IDs
result = subprocess.run(
    ["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "list:workflow"],
    capture_output=True,
    text=True
)

lines = result.stdout.strip().split('\n')
dashboard_api_ids = []

for line in lines:
    if '08 - Dashboard API' in line:
        wf_id = line.split('|')[0].strip()
        dashboard_api_ids.append(wf_id)

print(f"Found {len(dashboard_api_ids)} Dashboard API workflows")

# Delete ALL of them
for wf_id in dashboard_api_ids:
    print(f"Deleting {wf_id}...")
    subprocess.run(
        ["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "remove:workflow", f"--id={wf_id}"],
        capture_output=True
    )

print("\nStopping n8n...")
subprocess.run(["docker", "stop", "ai-assist-n8n"], capture_output=True)

print("Waiting 5 seconds...")
time.sleep(5)

print("Starting n8n...")
subprocess.run(["docker", "start", "ai-assist-n8n"], capture_output=True)

print("\nWaiting 30 seconds for n8n to start...")
time.sleep(30)

print("\nNow importing the clean workflow...")
subprocess.run(
    ["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "import:workflow", "--input=/workflows/shared/08-dashboard-api.json"],
    capture_output=True
)

print("\nDone! Check the n8n UI - there should be only ONE Dashboard API workflow now.")
print("Open it and click Publish.")
