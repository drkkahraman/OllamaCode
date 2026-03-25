import os
import pty
import sys
import select
import termios
import tty
import subprocess
import signal

def execute_command(cmd, cwd=None):
    if cwd: 
        try: os.chdir(cwd)
        except OSError: pass
            
    if cmd.strip().startswith("cd "):
        try:
            new_dir = cmd.strip().split("cd ", 1)[1].strip()
            path = os.path.expanduser(new_dir)
            os.chdir(path)
            return 0, f"Changed to {os.getcwd()}", os.getcwd()
        except Exception as e:
            return 1, str(e), os.getcwd()

    output_buffer = []
    
    # Save current terminal settings
    try:
        old_tty = termios.tcgetattr(sys.stdin)
    except termios.error:
        old_tty = None

    master_fd = None
    try:
        # Create a pseudo-terminal
        master_fd, slave_fd = pty.openpty()
        
        # Start the process in a new session so it gets its own group
        p = subprocess.Popen(
            ["/bin/bash", "-c", cmd],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            preexec_fn=os.setsid,
            cwd=cwd
        )
        
        os.close(slave_fd)
        
        if old_tty:
            tty.setraw(sys.stdin.fileno())
            
        while p.poll() is None:
            # Use select to wait for data on either master_fd (process output) or sys.stdin (user input)
            r, _, _ = select.select([master_fd, sys.stdin], [], [], 0.05)
            
            if master_fd in r:
                try:
                    data = os.read(master_fd, 1024)
                    if data:
                        decoded = data.decode(errors='ignore')
                        output_buffer.append(decoded); sys.stdout.write(decoded); sys.stdout.flush()
                except OSError: pass
                    
            if sys.stdin in r:
                try:
                    data = os.read(sys.stdin.fileno(), 1024)
                    if data: os.write(master_fd, data)
                except OSError: pass
                    
        # Process finished, capture any remaining output
        while True:
            r, _, _ = select.select([master_fd], [], [], 0)
            if not r: break
            try:
                data = os.read(master_fd, 1024)
                if not data: break
                decoded = data.decode(errors='ignore')
                output_buffer.append(decoded); sys.stdout.write(decoded); sys.stdout.flush()
            except OSError: break
                
        return p.returncode, "".join(output_buffer), os.getcwd()
        
    except Exception as e:
        return 1, f"Execution failed: {str(e)}", os.getcwd()
    finally:
        if old_tty:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)
        if master_fd is not None:
            try: os.close(master_fd)
            except: pass
