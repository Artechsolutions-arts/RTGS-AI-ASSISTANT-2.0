import subprocess
import time

print("=== Creating Unified Dashboard API ===\n")

# Step 1: Delete ALL Dashboard API workflows
print("Step 1: Deleting all old Dashboard API workflows...")
result = subprocess.run(
    ["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "list:workflow"],
    capture_output=True,
    text=True
)

lines = result.stdout.strip().split('\n')
for line in lines:
    if '08 - Dashboard API' in line or 'Dashboard API' in line:
        wf_id = line.split('|')[0].strip()
        print(f"  Deleting {wf_id}...")
        subprocess.run(
            ["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "remove:workflow", f"--id={wf_id}"],
            capture_output=True
        )

# Step 2: Restart n8n
print("\nStep 2: Restarting n8n...")
subprocess.run(["docker", "restart", "ai-assist-n8n"], capture_output=True)
print("Waiting 30 seconds...")
time.sleep(30)

# Step 3: Import the new unified workflow
print("\nStep 3: Importing unified Dashboard API...")
subprocess.run(
    ["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "import:workflow", "--input=/workflows/shared/08-dashboard-api-unified.json"],
    capture_output=True
)

print("\n=== DONE ===")
print("\nThe new workflow uses a SINGLE webhook endpoint:")
print("  http://localhost:5678/webhook/dashboard-data?type=messages&district=ntr-district")
print("  http://localhost:5678/webhook/dashboard-data?type=calendar&district=ntr-district")
print("  http://localhost:5678/webhook/dashboard-data?type=appointments&district=ntr-district")
print("\nGo to n8n UI and activate 'Dashboard API - Unified'")
