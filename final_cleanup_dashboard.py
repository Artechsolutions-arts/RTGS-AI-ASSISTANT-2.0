import subprocess
import time

print("=== FINAL CLEANUP - DELETE ALL DASHBOARD API DUPLICATES ===\n")

# Get all workflow IDs
result = subprocess.run(
    ["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "list:workflow"],
    capture_output=True,
    text=True
)

lines = result.stdout.strip().split('\n')
dashboard_api_ids = []

for line in lines:
    if 'Dashboard API - Final' in line:
        wf_id = line.split('|')[0].strip()
        dashboard_api_ids.append(wf_id)

print(f"Found {len(dashboard_api_ids)} Dashboard API workflows: {dashboard_api_ids}")

# Delete ALL of them
for wf_id in dashboard_api_ids:
    print(f"  Deleting {wf_id}...")
    subprocess.run(
        ["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "remove:workflow", f"--id={wf_id}"],
        capture_output=True
    )

# Restart n8n
print("\nRestarting n8n...")
subprocess.run(["docker", "restart", "ai-assist-n8n"], capture_output=True)
time.sleep(40)

# Import ONE clean copy
print("\nImporting single clean workflow...")
subprocess.run(
    ["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "import:workflow", "--input=/workflows/shared/08-dashboard-api-final.json"],
    capture_output=True,
    text=True
)

# Activate it
print("\nActivating workflow...")
result = subprocess.run(
    ["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "list:workflow"],
    capture_output=True,
    text=True
)

for line in result.stdout.strip().split('\n'):
    if 'Dashboard API - Final' in line:
        wf_id = line.split('|')[0].strip()
        print(f"  Activating {wf_id}...")
        subprocess.run(
            ["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "update:workflow", "--active=true", f"--id={wf_id}"],
            capture_output=True
        )
        break

print("\n=== DONE ===")
print("Verifying final state...")
subprocess.run(["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "list:workflow"])
