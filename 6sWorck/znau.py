
import subprocess
result = subprocess.run(
    ["cmd", "/c", "exit", "7"],
    capture_output=True,
    check=False
)

print("Код завершения:", result.returncode)

