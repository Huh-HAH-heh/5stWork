import sys

import subprocess
import time
def split_command(cmd_str):
    splited = cmd_str.split()
    return splited
def parse_args(argv):
    slow = False
    commands = []
    if len(argv) > 0:
       
        if argv[0] == "--slow":
            slow =True
           
            argv.pop(0)
    if len(argv) == 0:
        argv.append("python --version")
        
    for command in argv:
            commands.append(split_command(command))
    return slow , commands 
def pick_encoding(cmd):
    encoding =None
    program = cmd[0].lower()
    system_tools = [
    "cmd",
    "findstr",
    "ping",
    "where",
    "dir",
    "type"
    ]
    if program in system_tools:
        encoding = "cp866"
    else:
        encoding ="utf-8"
    return encoding
def decode_output(data, encoding):
    if data is None:
        return ""

    return data.decode(encoding, errors="replace")
def run_command(cmd, timeout=10):
    start_time = time.perf_counter()

    encoding = pick_encoding(cmd)

    status = "ошибка"
    returncode = None
    stdout = ""
    stderr = ""

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=timeout,
            check=True
        )

        returncode = result.returncode
        stdout = decode_output(result.stdout, encoding)
        stderr = decode_output(result.stderr, encoding)

        status = "успех"

    except FileNotFoundError:
        status = "не найдена"
        stderr = f"Программа не найдена: {cmd[0]}"

    except subprocess.TimeoutExpired as error:
        status = "timeOut"

        stdout = decode_output(error.stdout, encoding)
        stderr = decode_output(error.stderr, encoding)

        stderr += f"\ntimeOut {timeout} сек"

    except subprocess.CalledProcessError as error:
        status = "err"

        returncode = error.returncode
        stdout = decode_output(error.stdout, encoding)
        stderr = decode_output(error.stderr, encoding)

    duration = time.perf_counter() - start_time

    return {
        "command": cmd,
        "status": status,
        "returncode": returncode,
        "stdout": stdout,
        "stderr": stderr,
        "duration": duration
    }
def run_parallel(commands, timeout=10):
    processes = []
    results = [None] * len(commands)

    # Сначала запускаем все процессы
    for index, cmd in enumerate(commands):
        start_time = time.perf_counter()
        encoding = pick_encoding(cmd)

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            processes.append({
                "index": index,
                "process": process,
                "command": cmd,
                "encoding": encoding,
                "start_time": start_time
            })

        except FileNotFoundError:
            results[index] = {
                "command": cmd,
                "status": "не найдена",
                "returncode": None,
                "stdout": "",
                "stderr": f"Программа не найдена: {cmd[0]}",
                "duration": time.perf_counter() - start_time
            }

    # Теперь собираем результаты
    for item in processes:
        process = item["process"]
        encoding = item["encoding"]
        start_time = item["start_time"]

        elapsed = time.perf_counter() - start_time
        remaining = max(0, timeout - elapsed)

        try:
            stdout_data, stderr_data = process.communicate(
                timeout=remaining
            )

            returncode = process.returncode

            status = "успех" if returncode == 0 else "ошибка"

        except subprocess.TimeoutExpired:
            process.kill()
            stdout_data, stderr_data = process.communicate()

            returncode = process.returncode
            status = "таймаут"

            stderr_data += f"\nТаймаут {timeout} сек".encode(encoding)

        duration = time.perf_counter() - start_time

        results[item["index"]] = {
            "command": item["command"],
            "status": status,
            "returncode": returncode,
            "stdout": decode_output(stdout_data, encoding),
            "stderr": decode_output(stderr_data, encoding),
            "duration": duration
        }

    return results
def run_commands(commands, slow, timeout=10):
    if slow:
        return run_parallel(commands, timeout)

    return run_sequential(commands, timeout)
def format_report(results, total_time, slow, timeout):

    lines = []

    lines.append("=== МЕНЕДЖЕР ЗАПУСКА КОМАНД ===")
    lines.append(f"Режим: {'параллельный' if slow else 'последовательный'}")
    lines.append(f"Таймаут: {timeout} сек")
    lines.append("")

    successful = 0

    for index, result in enumerate(results, 1):

        if result["status"] == "успех":
            successful += 1

        lines.append(f"--- Команда {index} ---")
        lines.append(f"Команда: {' '.join(result['command'])}")
        lines.append(f"Статус: {result['status']}")

        returncode = result["returncode"]
        lines.append(f"Код возврата: {returncode if returncode is not None else '—'}")

        stdout = result["stdout"][:200] or "(пусто)"
        stderr = result["stderr"][:200] or "(пусто)"

        lines.append(f"stdout: {stdout}")
        lines.append(f"stderr: {stderr}")
        lines.append(f"Время: {result['duration']:.2f} сек")
        lines.append("")

    failed = len(results) - successful

    lines.append("============ ИТОГО ============")
    lines.append(f"Всего команд: {len(results)}")
    lines.append(f"Успешных: {successful}")
    lines.append(f"Провалившихся: {failed}")
    lines.append(f"Общее время: {total_time:.2f} сек")

    return "\n".join(lines)
def save_report(text, path="report.txt"):
    with open(path, "w", encoding="utf-8") as file:
        file.write(text)
def run_sequential(commands, timeout=10):
    results = []

    for cmd in commands:
        result = run_command(cmd, timeout)
        results.append(result)

    return results
def main():

    slow, commands = parse_args(sys.argv[1:])

    timeout = 10

    print("Подготовленные команды:")
    for command in commands:
        print(command)

    print("\nЗапуск...")

    start_time = time.perf_counter()

    results = run_commands(commands, slow, timeout)

    total_time = time.perf_counter() - start_time

    report = format_report(
        results,
        total_time,
        slow,
        timeout
    )

    print("\n" + report)

    save_report(report)

    print("\nОтчёт сохранён в report.txt")

    successful = any(
        result["status"] == "успех"
        for result in results
    )

    return 0 if successful else 1


if __name__ == "__main__":
    sys.exit(main())
