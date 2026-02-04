import subprocess
import time

print("=== Deploying Telegram Intake Workflow ===\n")

# Step 1: Delete OLD Telegram Intake workflow
print("Step 1: Deleting old Telegram Intake workflow...")
result = subprocess.run(
    ["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "list:workflow"],
    capture_output=True,
    text=True
)

lines = result.stdout.strip().split('\n')
for line in lines:
    if '01 - Telegram Message Intake' in line:
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

# Step 3: Import the new workflow
print("\nStep 3: Importing updated Telegram Intake...")
subprocess.run(
    ["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "import:workflow", "--input=/workflows/telegram/01-telegram-intake.json"],
    capture_output=True
)

print("\n=== DONE ===")
print("\nIMPORTANT: Go to n8n UI and manually ACTIVATE '01 - Telegram Message Intake' workflow.")
