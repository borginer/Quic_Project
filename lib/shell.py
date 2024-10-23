import subprocess
from typing import Tuple


def execute_command(command: str) -> Tuple[str, str]:
    try:
        result = subprocess.run(command, shell=True,
                                capture_output=True, text=True)

        # Return the output and error (if any)
        return result.stdout, result.stderr

    except Exception as e:
        return None, str(e)


if __name__ == "__main__":
    command = input("Enter the command you want to execute: ")

    stdout, stderr = execute_command(command)

    if stdout:
        print("Output:\n", stdout)

    if stderr:
        print("Error:\n", stderr)
