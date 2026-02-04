import subprocess

def deactivate_others():
    TO_KEEP_IDS = [
        "QmjwdS3YsOWhiGPJBpwdV", # 01 - Intake
        "QsnWb0D0m97fu9Ia",      # Dashboard API - Final
        "YFyshOcBBxynR1D5",      # Calendar Sync Service - FIXED
        "3",                     # Routing
        "4",                     # Task
        "RdvxoVYLHVNNGfLP",      # Reminders
        "X3m2Nf8iZL2LeX8L"       # Conflict
    ]
    
    res = subprocess.run(["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "list:workflow"], capture_output=True, text=True)
    lines = res.stdout.strip().split('\n')
    
    for line in lines:
        if '|' in line:
            parts = line.split('|')
            wf_id = parts[0].strip()
            wf_name = parts[1].strip()
            
            if wf_id in TO_KEEP_IDS:
                print(f"ACTIVATING: {wf_name} ({wf_id})")
                subprocess.run(["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "update:workflow", f"--id={wf_id}", "--active=true"], capture_output=True)
            else:
                print(f"DEACTIVATING: {wf_name} ({wf_id})")
                subprocess.run(["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "update:workflow", f"--id={wf_id}", "--active=false"], capture_output=True)

    print("\nRestarting n8n to ensure clean state...")
    subprocess.run(["docker", "restart", "ai-assist-n8n"], capture_output=True)

if __name__ == "__main__":
    deactivate_others()
