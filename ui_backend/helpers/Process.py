import subprocess


class Process:
    @staticmethod
    def execute(invocation: str) -> tuple:
        # Executes process and get its exit code and output.
        # Wraps C/Bash exit status convention to Python True/False for "success".
        success = False
        status = 1
        output = ""

        try:
            p = subprocess.run(
                invocation.split(" "),
                check=True,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            output = p.stdout # std. output.
            status = int(p.returncode) # exit code.

            if status == 0:
                success = True
        except Exception as e:
            raise e

        return success, status, output
