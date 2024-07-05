import subprocess

def run_script(script_name):
    result = subprocess.run(["python3", script_name], capture_output=True, text=True)
    print(f"Results for {script_name}:\n{result.stdout}")

# Run the Spectre tiling script
run_script("spectre_tiling.py")

# Run the Hexagonal tiling script
run_script("hexagonal_tiling.py")
