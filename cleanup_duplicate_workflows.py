import subprocess

# Get list of all workflows
result = subprocess.run(
    ["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "list:workflow"],
    capture_output=True,
    text=True
)

lines = result.stdout.strip().split('\n')

# Find all Dashboard API workflows
dashboard_apis = []
for line in lines:
    if '08 - Dashboard API' in line:
        wf_id = line.split('|')[0]
        dashboard_apis.append(wf_id)

print(f"Found {len(dashboard_apis)} Dashboard API workflows:")
for wf_id in dashboard_apis:
    print(f"  - {wf_id}")

# Keep only the last one, delete the rest
if len(dashboard_apis) > 1:
    to_delete = dashboard_apis[:-1]  # All except the last one
    keep = dashboard_apis[-1]
    
    print(f"\nKeeping: {keep}")
    print(f"Deleting: {', '.join(to_delete)}")
    
    for wf_id in to_delete:
        print(f"  Deleting {wf_id}...")
        subprocess.run(
            ["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "remove:workflow", f"--id={wf_id}"],
            capture_output=True
        )
    
    print("\nDone! Now activating the remaining workflow...")
    subprocess.run(
        ["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "update:workflow", f"--id={keep}", "--active=true"],
        capture_output=True
    )
    
    print(f"Workflow {keep} activated!")
else:
    print("\nOnly one Dashboard API workflow found. Activating it...")
    subprocess.run(
        ["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "update:workflow", f"--id={dashboard_apis[0]}", "--active=true"],
        capture_output=True
    )
