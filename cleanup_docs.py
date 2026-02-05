#!/usr/bin/env python3
"""
Cleanup Unnecessary Documentation Files
Removes development/internal documentation, keeping only production-essential docs
"""

import os
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_warning(text):
    print(f"{Colors.YELLOW}[CLEANUP] {text}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}[OK] {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}[INFO] {text}{Colors.END}")

# Documentation files to REMOVE (development/internal docs)
DOCS_TO_REMOVE = [
    # Development process docs
    'CURSOR_AI_PROMPT.md',
    'QUICK_CURSOR_PROMPT.md',
    
    # Status/progress docs (replaced by FINAL_DEPLOYMENT_STATUS.md)
    'FINAL_PROJECT_STATUS.md',
    'SUCCESS_APPOINTMENTS_WORKING.md',
    'VALIDATION_REPORT.md',
    
    # Feature-specific implementation docs (too detailed for production)
    'ACTIVATE_APPOINTMENTS_ENDPOINT.md',
    'APPOINTMENTS_DATABASE_SUMMARY.md',
    'CLEAN_OPERATIONAL_COMMS.md',
    'DASHBOARD_ORGANIZATION.md',
    'DASHBOARD_IMPLEMENTATION.md',
    'DASHBOARD_FEATURES.md',
    'UNIFIED_DASHBOARD_API.md',
    'DEPARTMENT_ROUTING_SETUP.md',
    
    # Voice/UI enhancement docs (development notes)
    'VOICE_AND_ICON_IMPROVEMENTS.md',
    'FEMALE_VOICE_ENHANCEMENT.md',
    
    # Quick reference (redundant with main docs)
    'QUICK_REFERENCE.md',
    'TELEGRAM_QUICK_START.md',
    
    # Duplicate/redundant summaries
    'PROJECT_SUMMARY.md',  # Covered in COMPLETE_PROJECT_SUMMARY.md
    'DEPLOYMENT_READY.md',  # Covered in FINAL_DEPLOYMENT_STATUS.md
    
    # Dashboard-specific docs (keep only essential ones)
    'dashboard/QUICKSTART.md',  # Redundant with dashboard/README.md
    'dashboard/MAP_GUIDE.md',  # Development detail
]

# Documentation files to KEEP (production-essential)
ESSENTIAL_DOCS = [
    # Main documentation
    'README.md',
    'DEPLOYMENT_GUIDE.md',
    'FINAL_DEPLOYMENT_STATUS.md',
    'COMPLETE_PROJECT_SUMMARY.md',
    
    # Technical documentation
    'TECHNICAL_DOCUMENTATION.md',
    'SYSTEM_FLOW.md',
    'TECH_STACK_REFERENCE.md',
    
    # Setup guides
    'SETUP_GUIDE.md',
    'N8N_SETUP_GUIDE.md',
    'MONGODB_ATLAS_CONFIG.md',
    'DOCKER_TROUBLESHOOTING.md',
    
    # User guides
    'TELEGRAM_BOT_SETUP.md',
    'TELEGRAM_DEMO_GUIDE.md',
    'CREATE_TELEGRAM_BOT_GUIDE.md',
    'CHATBOT_DOCUMENTATION.md',
    'VOICE_ASSISTANT_GUIDE.md',
    
    # Component documentation
    'n8n-workflows/README.md',
    'dashboard/README.md',
    'dashboard/SETUP.md',
]

def cleanup_docs():
    """Remove unnecessary documentation files"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{'Cleaning Up Documentation Files'.center(60)}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    removed_count = 0
    total_size = 0
    
    for doc_file in DOCS_TO_REMOVE:
        filepath = Path(doc_file)
        if filepath.exists():
            size = filepath.stat().st_size / 1024  # KB
            try:
                os.remove(filepath)
                print_warning(f"Removed: {doc_file} ({size:.1f} KB)")
                removed_count += 1
                total_size += size
            except Exception as e:
                print_warning(f"Could not remove {doc_file}: {e}")
    
    print()
    print_success(f"Removed {removed_count} documentation files ({total_size:.1f} KB total)")
    
    return removed_count, total_size

def show_kept_docs():
    """Show which documentation files are being kept"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{'Essential Documentation Kept'.center(60)}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    print_info("Production-essential documentation:")
    print("\n📘 Main Documentation:")
    print("  • README.md - Project overview")
    print("  • DEPLOYMENT_GUIDE.md - Complete deployment instructions")
    print("  • FINAL_DEPLOYMENT_STATUS.md - Current deployment status")
    print("  • COMPLETE_PROJECT_SUMMARY.md - Comprehensive project summary")
    
    print("\n📗 Technical Documentation:")
    print("  • TECHNICAL_DOCUMENTATION.md - Technical architecture")
    print("  • SYSTEM_FLOW.md - System workflow details")
    print("  • TECH_STACK_REFERENCE.md - Technology stack")
    
    print("\n📙 Setup & Configuration:")
    print("  • SETUP_GUIDE.md - General setup instructions")
    print("  • N8N_SETUP_GUIDE.md - n8n workflow setup")
    print("  • MONGODB_ATLAS_CONFIG.md - Database configuration")
    print("  • DOCKER_TROUBLESHOOTING.md - Docker troubleshooting")
    
    print("\n📕 User Guides:")
    print("  • TELEGRAM_BOT_SETUP.md - Telegram bot setup")
    print("  • TELEGRAM_DEMO_GUIDE.md - User demo guide")
    print("  • CREATE_TELEGRAM_BOT_GUIDE.md - Bot creation guide")
    print("  • CHATBOT_DOCUMENTATION.md - Chatbot features")
    print("  • VOICE_ASSISTANT_GUIDE.md - Voice assistant guide")
    
    print("\n📂 Component Documentation:")
    print("  • n8n-workflows/README.md - Workflow documentation")
    print("  • dashboard/README.md - Dashboard documentation")
    print("  • dashboard/SETUP.md - Dashboard setup")
    print()

def main():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{'Documentation Cleanup'.center(60)}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    print_info("This will remove development/internal documentation files")
    print_info("Essential production documentation will be kept")
    print()
    
    response = input(f"{Colors.YELLOW}Continue with documentation cleanup? (y/N): {Colors.END}").strip().lower()
    if response != 'y':
        print_info("Cleanup cancelled")
        return
    
    # Perform cleanup
    removed, size_freed = cleanup_docs()
    
    # Show what was kept
    show_kept_docs()
    
    # Summary
    print(f"{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}[OK] Documentation cleanup completed!{Colors.END}".center(70))
    print(f"{Colors.GREEN}Removed {removed} files ({size_freed:.1f} KB){Colors.END}".center(70))
    print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")

if __name__ == "__main__":
    main()
