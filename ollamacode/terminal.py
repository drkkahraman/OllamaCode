import os
import pty
import sys

def execute_command(cmd, cwd=None):
    if cwd: os.chdir(cwd)
    output_buffer = []
    try:
        if cmd.strip().startswith("cd "):
            new_dir = cmd.strip().split("cd ")[1].strip()
            os.chdir(os.path.expanduser(new_dir))
            return 0, f"Changed to {os.getcwd()}", os.getcwd()

        def master_read(master_fd):
            try:
                data = os.read(master_fd, 1024)
                if data:
                    decoded = data.decode(errors='ignore')
                    output_buffer.append(decoded); sys.stdout.write(decoded); sys.stdout.flush()
                return data
            except OSError: return b''

        exit_status = pty.spawn(["/bin/bash", "-c", cmd], master_read)
        return exit_status, "".join(output_buffer), os.getcwd()
    except Exception as e:
        return 1, f"Execution failed: {str(e)}", os.getcwd()
