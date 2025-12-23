import subprocess
import os
from datetime import datetime

ANALYTICS_SCRIPTS = [
    "generate_reports.py",
    "keyword_trends.py",
    # "domain_activity.py",
    # "sentiment_trends.py",
    # "category_stats.py",
    "repeated_domains.py",
    # "domain_url_activity.py",
    "same_site_evolution.py"  # 👈 add this line
]


def run_script(script_name):
    script_path = os.path.join("analytics", script_name)
    print(f"\n📊 Running {script_name} ...")
    result = subprocess.run(["python", script_path], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ {script_name} completed successfully.")
    else:
        print(f"❌ Error in {script_name}:")
        print(result.stderr or result.stdout)

def main():
    print("=== DARKWEB DAILY ANALYTICS PIPELINE ===")
    print(f"🕒 Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    os.makedirs("reports", exist_ok=True)
    
    for script in ANALYTICS_SCRIPTS:
        run_script(script)
    
    print("\n📁 All reports saved in the 'reports/' folder.")
    print("🎯 Analytics pipeline completed successfully.")

if __name__ == "__main__":
    main()
