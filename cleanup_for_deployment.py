#!/usr/bin/env python3
"""
Pre-Deployment Cleanup Script
Removes unnecessary debug, test, and temporary files before production deployment
"""

import os
import shutil
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}[OK] {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}[CLEANUP] {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}[INFO] {text}{Colors.END}")

# Files to remove (debug, test, and temporary files)
FILES_TO_REMOVE = [
    # Debug scripts
    'debug_missing_message.py',
    'debug_appointments.py',
    'debug_calendar.py',
    'debug_calendar_dates.py',
    'debug_mongo.py',
    'debug_msg_schema.py',
    'debug_raw_msg.py',
    'debug_sync_response.py',
    'debug_telugu.py',
    'debug_timezone_direct.py',
    
    # Test scripts
    'test_ambulance_fix.py',
    'test_ai.py',
    'test_api.py',
    'test_api_v2.py',
    'test_approved_appointments.py',
    'test_intake.py',
    'test_intake_multi.py',
    'test_n8n_local.py',
    'test_n8n_response.py',
    
    # Check scripts (keep validate_system.py)
    'check_all_calendar_fields.py',
    'check_appt_type.py',
    'check_db_past.py',
    'check_db_past_v2.py',
    'check_districts_deep.py',
    'check_full_doc.py',
    'check_id.py',
    'check_intents.py',
    'check_keys.py',
    'check_messages.py',
    'check_mongo.py',
    'check_mongo_state.py',
    'check_recent_depts.py',
    'check_tasks.py',
    'check_type.py',
    'check_webhook.py',
    
    # Inspect scripts
    'inspect_ambulance_msg.py',
    'inspect_api_messages.py',
    'inspect_api_v2.py',
    'inspect_empty.py',
    'inspect_meeting_msg.py',
    'inspect_meetings.py',
    'inspect_messages.py',
    'inspect_mongo_calendar.py',
    'inspect_mongo_full.py',
    'inspect_processed.py',
    'inspect_wrong_messages.py',
    'inspect_svg_labels.py',
    
    # Search scripts
    'search_all_telugu.py',
    'search_message.py',
    'search_message_detailed.py',
    'search_telugu.py',
    'find_schedule_msg.py',
    
    # List scripts
    'list_all_wfs.py',
    'list_atlas.py',
    'list_calendar_summaries.py',
    
    # Cleanup scripts (keep final_cleanup_dashboard.py)
    'cleanup_duplicate_workflows.py',
    'cleanup_junk.py',
    'cleanup_meetings.py',
    'cleanup_messages.py',
    'cleanup_mock_data.py',
    'nuclear_cleanup.py',
    'strict_cleanup.py',
    'super_cleanup.py',
    'verified_cleanup.py',
    
    # Deactivate scripts
    'deactivate_all.py',
    'deactivate_all_dashboard_apis.py',
    'deactivate_all_v2.py',
    'deactivate_redundant.py',
    'delete_old_dashboard_apis.py',
    
    # Fix scripts (temporary)
    'absolute_precision_fix.py',
    'citizen_robustness_fix.py',
    'clean_reason_logic.py',
    'enhanced_appointment_logic.py',
    'filter_completed.py',
    'final_n8n_pairing_fix.py',
    'final_precision_fix.py',
    'final_robustness_fix.py',
    'final_unification_fix.py',
    'fix_appointment_final.py',
    'fix_appointments_dates.py',
    'fix_calendar_districts.py',
    'fix_calendar_final.py',
    'fix_calendar_precision_v3.py',
    'fix_calendar_v2.py',
    'fix_dashboard_filter.py',
    'fix_iso_logic.py',
    'fix_logic_v5.py',
    'fix_loop_and_routing.py',
    'fix_no_reply_memory.py',
    'fix_owners.py',
    'fix_telegram_workflow.py',
    'fix_timestamps_2026.py',
    'fix_webhook_conflicts.py',
    'fix_workflow.py',
    'harden_workflow.py',
    'master_unified_fix.py',
    'next_day_suggestion_fix.py',
    'simplify_prompt.py',
    'surgical_fix.py',
    'unified_robustness_fix.py',
    'update_logic_final.py',
    
    # Deployment scripts (old versions)
    'deploy_debug.py',
    'deploy_final_api_v2.py',
    'deploy_sync_update.py',
    'deploy_telegram_fix.py',
    'deploy_telegram_workflow.py',
    'deploy_unified_api.py',
    
    # Backfill and migration scripts
    'backfill_depts.py',
    'backfill_depts_v2.py',
    'global_sync_depts.py',
    'migrate_existing_appointment.py',
    
    # Insert/seed scripts (keep seed_dashboard_mock.py for reference)
    'insert_backdated.py',
    'insert_dummy.py',
    'insert_today_meeting.py',
    
    # Verify scripts (keep validate_system.py and pre_deployment_check.py)
    'verify_active_workflow.py',
    'verify_api_date.py',
    'verify_calendar_api.py',
    'verify_calendar_range.py',
    'verify_connections.py',
    'verify_dashboard_flow.py',
    'verify_latest_messages.py',
    'verify_v2.py',
    'verify_workflow.py',
    
    # Other utility scripts
    'force_sync.py',
    'remove_blocking_param.py',
    'reset_webhook.py',
    'trigger_sync.py',
    'update_wf_db.py',
    'update_workflow.py',
    'find_and_activate_v2.py',
    
    # JSON files (temporary data)
    'dashboard_data.json',
    'dashboard_data_v2.json',
    'dashboard_messages.json',
    'dashboard_output.json',
    'dashboard_output_v3.json',
    'dashboard_response.json',
    'debug_response.json',
    'debug-activation.json',
    'final_verification.json',
    'multi_msg_response.json',
    'n8n_messages.json',
    'response_v3.txt',
    'workflow_status.json',
    
    # Workflow JSON files (old/backup)
    '01_intake.json',
    'intake_clean.json',
    'intake_connections.json',
    'intake_nodes.json',
    'intake_nodes_utf8.json',
    'workflow_3_connections.json',
    'workflow_3_connections_utf8.json',
    'workflow_3_nodes.json',
    'workflow_3_nodes_utf8.json',
    'workflow_4_nodes.json',
    'workflow_4_nodes_utf8.json',
    'workflow_check.txt',
    
    # Dashboard analysis scripts
    'dashboard/analyze_svg.py',
    'dashboard/analyze_svg_simple.py',
    'dashboard/clean_map_script.py',
    'dashboard/download_convert_geojson.py',
    'dashboard/generate_map_data.py',
]

# Directories to remove
DIRS_TO_REMOVE = [
    'synthetic-data',  # Keep only if needed for testing
]

# Files to KEEP (essential for production)
ESSENTIAL_FILES = [
    # Core application
    'docker-compose.yml',
    'quick_start.bat',
    
    # Setup scripts
    'setup_atlas.py',
    'setup_mongodb_atlas.bat',
    'setup_n8n.bat',
    
    # Production deployment
    'deploy_final_api.py',
    'final_cleanup_dashboard.py',
    'deploy_production.sh',
    'pre_deployment_check.py',
    
    # Validation
    'validate_system.py',
    'validate_n8n.py',
    'test_integration.py',
    'test_telegram_integration.py',
    
    # Reference/seed data
    'seed_dashboard_mock.py',
    
    # Documentation
    '*.md',
    
    # Directories
    'ai-service/',
    'dashboard/',
    'database/',
    'n8n-workflows/',
]

def get_file_size(filepath):
    """Get file size in KB"""
    try:
        size = os.path.getsize(filepath)
        return size / 1024  # Convert to KB
    except:
        return 0

def cleanup_files():
    """Remove unnecessary files"""
    print_header("Cleaning Up Unnecessary Files")
    
    removed_count = 0
    total_size = 0
    skipped = []
    
    for filename in FILES_TO_REMOVE:
        filepath = Path(filename)
        if filepath.exists():
            size = get_file_size(filepath)
            try:
                os.remove(filepath)
                print_warning(f"Removed: {filename} ({size:.1f} KB)")
                removed_count += 1
                total_size += size
            except Exception as e:
                print_warning(f"Could not remove {filename}: {e}")
                skipped.append(filename)
        else:
            # File doesn't exist, skip silently
            pass
    
    print_success(f"Removed {removed_count} files ({total_size:.1f} KB total)")
    
    if skipped:
        print_info(f"Skipped {len(skipped)} files (in use or permission denied)")
    
    return removed_count, total_size

def cleanup_directories():
    """Remove unnecessary directories"""
    print_header("Cleaning Up Unnecessary Directories")
    
    removed_count = 0
    
    for dirname in DIRS_TO_REMOVE:
        dirpath = Path(dirname)
        if dirpath.exists() and dirpath.is_dir():
            try:
                # Ask for confirmation for directories
                print_info(f"Found directory: {dirname}")
                response = input(f"  Remove {dirname}? (y/N): ").strip().lower()
                if response == 'y':
                    shutil.rmtree(dirpath)
                    print_warning(f"Removed directory: {dirname}")
                    removed_count += 1
                else:
                    print_info(f"Kept: {dirname}")
            except Exception as e:
                print_warning(f"Could not remove {dirname}: {e}")
    
    if removed_count > 0:
        print_success(f"Removed {removed_count} directories")
    else:
        print_info("No directories removed")
    
    return removed_count

def cleanup_empty_files():
    """Remove empty JSON files"""
    print_header("Cleaning Up Empty Files")
    
    removed_count = 0
    
    # Find all JSON files
    for filepath in Path('.').glob('*.json'):
        if filepath.stat().st_size == 0:
            try:
                os.remove(filepath)
                print_warning(f"Removed empty file: {filepath.name}")
                removed_count += 1
            except Exception as e:
                print_warning(f"Could not remove {filepath.name}: {e}")
    
    if removed_count > 0:
        print_success(f"Removed {removed_count} empty files")
    else:
        print_info("No empty files found")
    
    return removed_count

def create_cleanup_summary():
    """Create a summary of what was kept"""
    print_header("Production Files Summary")
    
    print_info("Essential files kept:")
    print("  • docker-compose.yml")
    print("  • deploy_final_api.py")
    print("  • final_cleanup_dashboard.py")
    print("  • pre_deployment_check.py")
    print("  • validate_system.py")
    print("  • All documentation (*.md)")
    print("  • ai-service/ directory")
    print("  • dashboard/ directory")
    print("  • database/ directory")
    print("  • n8n-workflows/ directory")
    print()

def main():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{'Pre-Deployment Cleanup'.center(60)}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    print_info("This script will remove:")
    print("  • Debug scripts")
    print("  • Test scripts")
    print("  • Temporary fix scripts")
    print("  • Old deployment scripts")
    print("  • Temporary JSON files")
    print()
    
    response = input(f"{Colors.YELLOW}Continue with cleanup? (y/N): {Colors.END}").strip().lower()
    if response != 'y':
        print_info("Cleanup cancelled")
        return
    
    # Perform cleanup
    files_removed, size_freed = cleanup_files()
    empty_removed = cleanup_empty_files()
    dirs_removed = cleanup_directories()
    
    # Summary
    print_header("Cleanup Complete")
    print_success(f"Files removed: {files_removed}")
    print_success(f"Empty files removed: {empty_removed}")
    print_success(f"Directories removed: {dirs_removed}")
    print_success(f"Disk space freed: {size_freed:.1f} KB")
    print()
    
    create_cleanup_summary()
    
    print(f"{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}[OK] Cleanup completed successfully!{Colors.END}".center(70))
    print(f"{Colors.GREEN}System is ready for deployment{Colors.END}".center(70))
    print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")

if __name__ == "__main__":
    main()
