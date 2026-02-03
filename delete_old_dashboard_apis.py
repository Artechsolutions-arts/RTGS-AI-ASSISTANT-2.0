import subprocess

# List of all Dashboard API workflow IDs EXCEPT the one currently open (7tI4yLdWms5ec2nY)
workflow_ids_to_delete = [
    "PBs0v51qh8jmPUc9",
    "GejI3ayL6w75FN3B", 
    "9ATSElEKi3qBoRP8",
    "hmf0KIyekCGZv97T",
    "YrUAaOPths7JqZIq",
    "M4qSG1pf2Vw8CxzU",
    "AQxAZx8meCDXGPvZ",
    "saQEBxsUpxqliboQ",
    "NBZ0dQSzea4BdZS9",
    "8TRsLG74Jwcaa4oL",
    "DyhApbxMfQ5LJrLz",
    "L11tUuiNkgXbL1qa",
    "QqtO26TyHHDJt4RN"
]

print("Deleting all old Dashboard API workflows...")
for wf_id in workflow_ids_to_delete:
    print(f"  Deleting {wf_id}...")
    result = subprocess.run(
        ["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "remove:workflow", f"--id={wf_id}"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"    Warning: {result.stderr.strip()}")

print("\nRestarting n8n to clear webhook registry...")
subprocess.run(["docker", "restart", "ai-assist-n8n"], capture_output=True)

print("\nDone! Wait 30 seconds, then refresh the page and try to Publish again.")
print("The only remaining Dashboard API workflow is: 7tI4yLdWms5ec2nY")
