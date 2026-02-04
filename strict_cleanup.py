import subprocess

def strict_cleanup():
    # Only these should exist
    TO_KEEP_IDS = [
        "QmjwdS3YsOWhiGPJBpwdV", # 01 - Intake
        "QsnWb0D0m97fu9Ia",      # 08 - Dashboard API - Final
        "YFyshOcBBxynR1D5",      # 09 - Calendar Sync Service - FIXED
        "3",                     # 03 - Routing
        "4",                     # 04 - Task
        "RdvxoVYLHVNNGfLP",      # 03 - Reminders
        "X3m2Nf8iZL2LeX8L"       # 04 - Conflict
    ]
    
    res = subprocess.run(["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "list:workflow"], capture_output=True, text=True)
    lines = res.stdout.strip().split('\n')
    
    for line in lines:
        if '|' in line:
            wf_id = line.split('|')[0].strip()
            wf_name = line.split('|')[1].strip()
            
            if wf_id not in TO_KEEP_IDS:
                print(f"DELETING: {wf_name} ({wf_id})")
                subprocess.run(["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "remove:workflow", f"--id={wf_id}"], capture_output=True)
            else:
                print(f"KEEPING: {wf_name} ({wf_id})")
                # Also make sure it's ACTIVE
                subprocess.run(["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "update:workflow", f"--id={wf_id}", "--active=true"], capture_output=True)

    print("\nRestarting n8n...")
    subprocess.run(["docker", "restart", "ai-assist-n8n"], capture_output=True)

if __name__ == "__main__":
    strict_cleanup()
