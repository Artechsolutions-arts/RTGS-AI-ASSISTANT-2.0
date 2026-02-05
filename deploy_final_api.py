import subprocess
import time

print("=== Deploying Dashboard API Final ===\n")

# Step 1: Detect and Delete ONLY the 'Dashboard API - Final' or similar
print("Step 1: Cleaning up old Dashboard API workflows...")
result = subprocess.run(
    ["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "list:workflow"],
    capture_output=True,
    text=True
)

lines = result.stdout.strip().split('\n')
for line in lines:
    if 'Dashboard API - Final' in line or '08 - Dashboard API' in line:
        wf_id = line.split('|')[0].strip()
        print(f"  Deleting {wf_id}...")
        subprocess.run(
            ["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "remove:workflow", f"--id={wf_id}"],
            capture_output=True
        )

# Step 2: Restart n8n
print("\nStep 2: Restarting n8n...")
subprocess.run(["docker", "restart", "ai-assist-n8n"], capture_output=True)
print("Waiting 30 seconds for stability...")
time.sleep(30)

# Step 3: Import the FINAL workflow
print("\nStep 3: Importing Dashboard API - Final...")
import_res = subprocess.run(
    ["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "import:workflow", "--input=/workflows/shared/08-dashboard-api-final.json"],
    capture_output=True,
    text=True
)
print(import_res.stdout)

# Step 4: List and Activate
result = subprocess.run(
    ["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "list:workflow"],
    capture_output=True,
    text=True
)
lines = result.stdout.strip().split('\n')
for line in lines:
    if 'Dashboard API - Final' in line:
        wf_id = line.split('|')[0].strip()
        print(f"  Activating {wf_id}...")
        subprocess.run(
            ["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "update:workflow", "--active=true", f"--id={wf_id}"],
            capture_output=True
        )

print("\n=== DONE ===")
print("Dashboard API - Final is now active and supports server-side date filtering.")
