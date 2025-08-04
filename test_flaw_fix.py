import os

# Check if there are any recent log entries about flaw still capture
log_file = 'basketball_analysis_production_20250728.log'
if os.path.exists(log_file):
    with open(log_file, 'r') as f:
        lines = f.readlines()
        flaw_lines = [line for line in lines[-100:] if 'FLAW STILL CAPTURE' in line or 'flaw frames' in line.lower()]
        if flaw_lines:
            print('Recent flaw capture log entries:')
            for line in flaw_lines[-10:]:
                print(line.strip())
        else:
            print('No recent flaw capture entries found in log')
else:
    print('Log file not found')

# Also check for any existing flaw still images
import glob
flaw_stills = glob.glob('temp_*_flaw_*.png')
if flaw_stills:
    print(f"\nFound {len(flaw_stills)} existing flaw still images:")
    for still in flaw_stills[-5:]:  # Show last 5
        print(f"  {still}")
else:
    print("\nNo flaw still images found")
