"""
Fix for conflicting webhook paths in n8n.

The issue is that multiple workflows are trying to use the same webhook paths.
We need to ensure only one workflow is active with these paths.
"""

import subprocess
import time

print("=== Fixing n8n Webhook Conflicts ===\n")

# Step 1: List all workflows
print("Step 1: Listing all workflows...")
result = subprocess.run(
    ["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "list:workflow"],
    capture_output=True,
    text=True
)
print(result.stdout)

# Step 2: Deactivate all workflows first
print("\nStep 2: Deactivating all workflows to clear conflicts...")
workflows_to_deactivate = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

for wf_id in workflows_to_deactivate:
    subprocess.run(
        ["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "update:workflow", f"--id={wf_id}", "--active=false"],
        capture_output=True
    )

print("All workflows deactivated.")

# Step 3: Restart n8n to clear webhook registrations
print("\nStep 3: Restarting n8n to clear webhook registrations...")
subprocess.run(["docker", "restart", "ai-assist-n8n"], capture_output=True)
print("Waiting for n8n to restart (30 seconds)...")
time.sleep(30)

# Step 4: Activate only the essential workflows
print("\nStep 4: Activating essential workflows...")

essential_workflows = {
    "1": "01 - Telegram Message Intake",
    "5": "08 - Dashboard API",
    "X6QuleMMGA2OSyBY": "09 - Calendar Sync Service"
}

for wf_id, wf_name in essential_workflows.items():
    print(f"  Activating {wf_name}...")
    result = subprocess.run(
        ["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "update:workflow", f"--id={wf_id}", "--active=true"],
        capture_output=True,
        text=True
    )

print("\n=== Done! ===")
print("\nPlease restart n8n one more time:")
print("  docker restart ai-assist-n8n")
print("\nThen test the appointments endpoint:")
print("  Invoke-RestMethod -Method Get -Uri 'http://localhost:5678/webhook/appointments-approved?district=ntr-district'")
