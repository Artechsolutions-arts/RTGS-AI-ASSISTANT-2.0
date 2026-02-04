import subprocess
import json

def get_workflows():
    res = subprocess.run(["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "list:workflow"], capture_output=True, text=True)
    lines = res.stdout.strip().split('\n')
    workflows = []
    for line in lines:
        if '|' in line:
            parts = line.split('|')
            workflows.append({"id": parts[0].strip(), "name": parts[1].strip()})
    return workflows

def nuclear_cleanup():
    # Keep list (IDs)
    KEEP_NAMES = [
        "01 - Telegram Message Intake",
        "Dashboard API-FINAL",
        "09 - Calendar Sync Service - FIXED",
        "03 - Rule-Based Routing",
        "04 - Task Creation and Follow-up",
        "03-task-reminders",
        "04-meeting-conflict-detector"
    ]
    
    workflows = get_workflows()
    print(f"Found {len(workflows)} workflows.")
    
    for wf in workflows:
        if wf['name'] not in KEEP_NAMES:
            print(f"Deleting duplicate/old workflow: {wf['name']} ({wf['id']})")
            subprocess.run(["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "remove:workflow", f"--id={wf['id']}"], capture_output=True)
        else:
            # Check if there are multiple with the same name, keep only one
            same_name = [w for w in workflows if w['name'] == wf['name']]
            if len(same_name) > 1:
                # Keep the one with the highest ID or longest ID (rough heuristic)
                to_keep = sorted(same_name, key=lambda x: len(x['id']), reverse=True)[0]
                if wf['id'] != to_keep['id']:
                    print(f"Deleting duplicate name workflow: {wf['name']} ({wf['id']})")
                    subprocess.run(["docker", "exec", "-u", "node", "ai-assist-n8n", "n8n", "remove:workflow", f"--id={wf['id']}"], capture_output=True)

    print("Cleanup complete. Restarting n8n...")
    subprocess.run(["docker", "restart", "ai-assist-n8n"], capture_output=True)

if __name__ == "__main__":
    nuclear_cleanup()
