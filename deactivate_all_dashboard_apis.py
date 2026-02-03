import subprocess

# List of all Dashboard API workflow IDs
workflow_ids = [
    "PBs0v51qh8jmPUc9",
    "GejI3ayL6w75FN3B", 
    "9ATSElEKi3qBoRP8",
    "hmf0KIyekCGZv97T",
    "YrUAaOPths7JqZIq",
    "M4qSG1pf2Vw8CxzU",
    "AQxAZx8meCDXGPvZ",
    "7tI4yLdWms5ec2nY",
    "saQEBxsUpxqliboQ",
    "NBZ0dQSzea4BdZS9",
    "8TRsLG74Jwcaa4oL",
    "DyhApbxMfQ5LJrLz",
    "L11tUuiNkgXbL1qa",
    "QqtO26TyHHDJt4RN"
]

print("Deactivating all Dashboard API workflows...")
for wf_id in workflow_ids:
    print(f"  Deactivating {wf_id}...")
    subprocess.run(
        ["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "update:workflow", f"--id={wf_id}", "--active=false"],
        capture_output=True
    )

print("\nRestarting n8n...")
subprocess.run(["docker", "restart", "ai-assist-n8n"], capture_output=True)

print("\nDone! Now you can activate the workflow with ID: 7tI4yLdWms5ec2nY")
print("(This is the one you have open in the UI)")
