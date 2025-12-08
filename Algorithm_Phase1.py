"""
CPU Scheduling Algorithms - All 6 Implementations
Each function returns structured output with table, gantt chart, and metrics
"""
import copy


def FCFS(processes):
    """
    First Come First Serve Algorithm (Non-Preemptive)

    How it works:
    - Processes are executed in order of arrival
    - Once a process starts, it runs until completion
    - No interruption allowed

    Returns:
        dict: {
            'table': List of dicts with process details,
            'gantt_chart': List of tuples (PID, start, finish),
            'metrics': Dict with average waiting and turnaround times
        }
    """
    # Phase 1: Prepare and sort processes
    process = copy.deepcopy(processes)  # Make a copy to avoid modifying original
    process.sort(key=lambda x: x["arrival"])  # Sort by arrival time

    # Phase 2: Initialize tracking variables
    time = 0  # Current CPU time
    gantt = []  # Store gantt chart entries
    table = []  # Store final results table

    # Phase 3: Process each job in order
    for i in process:
        # Step 1: Calculate start time (CPU might be idle waiting for process)
        start = max(time, i["arrival"])

        # Step 2: Calculate finish time
        finish = start + i["burst"]

        # Step 3: Calculate Turnaround Time (Total time in system)
        TAT = finish - i["arrival"]

        # Step 4: Calculate Waiting Time (Time spent waiting in ready queue)
        waiting = TAT - i["burst"]

        # Step 5: Store results
        table.append({
            'name': i["PID"],
            'arrival_time': i["arrival"],
            'burst_time': i["burst"],
            'completion_time': finish,
            'turnaround_time': TAT,
            'waiting_time': waiting
        })

        gantt.append((i["PID"], start, finish))

        # Step 6: Move time forward
        time = finish

    # Phase 4: Calculate average metrics
    avg_waiting = sum(p['waiting_time'] for p in table) / len(table)
    avg_turnaround = sum(p['turnaround_time'] for p in table) / len(table)

    return {
        'table': table,
        'gantt_chart': gantt,
        'metrics': {
            'average_waiting_time': avg_waiting,
            'average_turnaround_time': avg_turnaround
        }
    }


def SJF(processes):
    """
    Shortest Job First Algorithm (Non-Preemptive)

    How it works:
    - Always select the process with shortest burst time from ready queue
    - Once started, runs until completion
    - Minimizes average waiting time

    Returns:
        dict: Same structure as FCFS
    """
    # Phase 1: Prepare data structures
    process = copy.deepcopy(processes)
    time = 0  # Current CPU time
    completed = []  # List of completed process IDs
    no_of_jobs = len(process)
    gantt = []
    table = []

    # Phase 2: Keep scheduling until all jobs complete
    while len(completed) < no_of_jobs:
        # Step 1: Find all processes that have arrived and not completed
        available = [i for i in process if i["arrival"] <= time and i["PID"] not in completed]

        # Step 2: If no process is ready, advance time
        if not available:
            time += 1
            continue

        # Step 3: Select job with shortest burst time
        job = min(available, key=lambda x: x["burst"])

        # Step 4: Execute the selected job
        start = time
        finish = start + job["burst"]

        # Step 5: Calculate times
        TAT = finish - job["arrival"]
        waiting = TAT - job["burst"]

        # Step 6: Update time and mark as completed
        time = finish
        completed.append(job["PID"])

        # Step 7: Store results
        table.append({
            'name': job["PID"],
            'arrival_time': job["arrival"],
            'burst_time': job["burst"],
            'completion_time': finish,
            'turnaround_time': TAT,
            'waiting_time': waiting
        })

        gantt.append((job["PID"], start, finish))

    # Phase 3: Calculate metrics
    avg_waiting = sum(p['waiting_time'] for p in table) / len(table)
    avg_turnaround = sum(p['turnaround_time'] for p in table) / len(table)

    return {
        'table': table,
        'gantt_chart': gantt,
        'metrics': {
            'average_waiting_time': avg_waiting,
            'average_turnaround_time': avg_turnaround
        }
    }


def SRT(processes):
    """
    Shortest Remaining Time (Preemptive SJF)

    How it works:
    - Always execute process with shortest remaining time
    - Can preempt currently running process if shorter job arrives
    - Executes in 1 time unit increments to check for preemption

    Returns:
        dict: Same structure as FCFS
    """
    # Phase 1: Setup and initialization
    process = copy.deepcopy(processes)
    process = sorted(process, key=lambda x: x["arrival"])
    no_of_jobs = len(process)
    time = 0
    gantt = []
    table = []
    completed = []

    # Track current execution block for gantt chart
    last_PID = None
    start = 0

    # Track remaining burst time for each process
    remaining = {p["PID"]: p["burst"] for p in process}

    # Phase 2: Execute processes one time unit at a time
    while len(completed) < no_of_jobs:
        # Step 1: Find all available processes (arrived and not finished)
        available = [p for p in process if p["arrival"] <= time and remaining[p["PID"]] > 0]

        # Step 2: If no process available, advance time
        if not available:
            time += 1
            continue

        # Step 3: Select process with shortest remaining time
        job = min(available, key=lambda x: remaining[x["PID"]])
        pid = job["PID"]

        # Step 4: Handle context switch (if switching to different process)
        if pid != last_PID:
            if last_PID is not None:
                # Save previous process's gantt entry
                gantt.append((last_PID, start, time))
            start = time  # Start new gantt block
            last_PID = pid

        # Step 5: Execute for 1 time unit
        remaining[pid] -= 1
        time += 1

        # Step 6: Check if process completed
        if remaining[pid] == 0:
            finish = time
            turnaround = finish - job["arrival"]
            waiting = turnaround - job["burst"]

            # Save gantt entry for completed process
            gantt.append((pid, start, finish))

            # Store in results table
            table.append({
                'name': pid,
                'arrival_time': job["arrival"],
                'burst_time': job["burst"],
                'completion_time': finish,
                'turnaround_time': turnaround,
                'waiting_time': waiting
            })

            completed.append(pid)
            last_PID = None

    # Phase 3: Calculate metrics and sort table by PID
    avg_waiting = sum(p['waiting_time'] for p in table) / len(table)
    avg_turnaround = sum(p['turnaround_time'] for p in table) / len(table)
    table_sorted = sorted(table, key=lambda x: x['name'])

    return {
        'table': table_sorted,
        'gantt_chart': gantt,
        'metrics': {
            'average_waiting_time': avg_waiting,
            'average_turnaround_time': avg_turnaround
        }
    }


def Priority_NP(processes):
    """
    Priority Scheduling (Non-Preemptive)

    How it works:
    - Each process has a priority number (lower = higher priority)
    - Always select highest priority process from ready queue
    - Once started, runs until completion

    Returns:
        dict: Same structure as FCFS
    """
    # Phase 1: Setup
    process = copy.deepcopy(processes)
    process = sorted(process, key=lambda x: x["arrival"])
    no_of_jobs = len(process)
    time = 0
    gantt = []
    table = []
    completed = []

    # Phase 2: Schedule processes based on priority
    while len(completed) < no_of_jobs:
        # Step 1: Find available processes (arrived and not completed)
        available = [p for p in process if p["arrival"] <= time and p not in completed]

        # Step 2: If none available, advance time
        if not available:
            time += 1
            continue

        # Step 3: Select process with highest priority (lowest number)
        job = min(available, key=lambda x: x["priority"])

        # Step 4: Execute the process completely
        start = time
        finish = start + job["burst"]

        # Step 5: Calculate times
        turnaround = finish - job["arrival"]
        waiting = turnaround - job["burst"]

        # Step 6: Update time and mark completed
        time = finish
        completed.append(job)

        # Step 7: Store results
        gantt.append((job["PID"], start, finish))
        table.append({
            'name': job["PID"],
            'arrival_time': job["arrival"],
            'burst_time': job["burst"],
            'completion_time': finish,
            'turnaround_time': turnaround,
            'waiting_time': waiting
        })

    # Phase 3: Calculate metrics and sort table
    table_sorted = sorted(table, key=lambda x: x['name'])
    avg_waiting = sum(p['waiting_time'] for p in table) / no_of_jobs
    avg_turnaround = sum(p['turnaround_time'] for p in table) / no_of_jobs

    return {
        'table': table_sorted,
        'gantt_chart': gantt,
        'metrics': {
            'average_waiting_time': avg_waiting,
            'average_turnaround_time': avg_turnaround
        }
    }


def Priority_P(processes):
    """
    Priority Scheduling (Preemptive)

    How it works:
    - Each process has a priority number (lower = higher priority)
    - Always execute highest priority process available
    - Can preempt currently running process if higher priority arrives
    - Executes in 1 time unit increments

    Returns:
        dict: Same structure as FCFS
    """
    # Phase 1: Setup and initialization
    process = copy.deepcopy(processes)
    process = sorted(process, key=lambda x: x["arrival"])
    no_of_jobs = len(process)
    time = 0
    gantt = []
    table = []
    completed = []

    # Track current execution for gantt chart
    last_PID = None
    start = 0

    # Track remaining time for each process
    remaining = {p["PID"]: p["burst"] for p in process}

    # Phase 2: Execute processes one time unit at a time
    while len(completed) < no_of_jobs:
        # Step 1: Find available processes
        available = [p for p in process if p["arrival"] <= time and remaining[p["PID"]] > 0]

        # Step 2: If none available, advance time
        if not available:
            time += 1
            continue

        # Step 3: Select highest priority process
        job = min(available, key=lambda x: x["priority"])
        pid = job["PID"]

        # Step 4: Handle context switch
        if pid != last_PID:
            if last_PID is not None:
                gantt.append((last_PID, start, time))
            start = time
            last_PID = pid

        # Step 5: Execute for 1 time unit
        remaining[pid] -= 1
        time += 1

        # Step 6: Check if completed
        if remaining[pid] == 0:
            finish = time
            turnaround = finish - job["arrival"]
            waiting = turnaround - job["burst"]

            gantt.append((pid, start, finish))
            table.append({
                'name': pid,
                'arrival_time': job["arrival"],
                'burst_time': job["burst"],
                'completion_time': finish,
                'turnaround_time': turnaround,
                'waiting_time': waiting
            })

            completed.append(pid)
            last_PID = None

    # Phase 3: Calculate metrics and sort
    table_sorted = sorted(table, key=lambda x: x['name'])
    avg_waiting = sum(p['waiting_time'] for p in table) / len(table)
    avg_turnaround = sum(p['turnaround_time'] for p in table) / len(table)

    return {
        'table': table_sorted,
        'gantt_chart': gantt,
        'metrics': {
            'average_waiting_time': avg_waiting,
            'average_turnaround_time': avg_turnaround
        }
    }


def Round_Robin(processes, quantum):
    """
    Round Robin Scheduling (Preemptive)

    How it works:
    - Each process gets a fixed time quantum
    - After quantum expires or process completes, move to next in queue
    - Fair scheduling - prevents starvation

    Args:
        quantum: Time slice each process gets before switching

    Returns:
        dict: Same structure as FCFS
    """
    # Phase 1: Setup
    process = copy.deepcopy(processes)
    process = sorted(process, key=lambda x: x["arrival"])
    no_of_jobs = len(process)
    time = 0
    gantt = []
    table = []
    completed = []

    # Track remaining burst time
    remaining = {p["PID"]: p["burst"] for p in process}

    # Ready queue to track process order
    queue = []

    # Phase 2: Execute in round-robin fashion
    while len(completed) < no_of_jobs:
        # Step 1: Add newly arrived processes to queue
        for p in process:
            if p["arrival"] <= time and remaining[p["PID"]] > 0 and p["PID"] not in queue:
                queue.append(p["PID"])

        # Step 2: If queue empty, advance time
        if not queue:
            time += 1
            continue

        # Step 3: Get next process from queue
        pid = queue.pop(0)

        # Step 4: Calculate execution time (quantum or remaining, whichever is less)
        execution_time = min(quantum, remaining[pid])

        # Step 5: Execute for calculated time
        start = time
        time += execution_time
        remaining[pid] -= execution_time

        # Step 6: Add to gantt chart
        gantt.append((pid, start, time))

        # Step 7: Check if process finished
        if remaining[pid] == 0:
            # Process completed - calculate final times
            job = next(p for p in process if p["PID"] == pid)
            turnaround = time - job["arrival"]
            waiting = turnaround - job["burst"]

            table.append({
                'name': pid,
                'arrival_time': job["arrival"],
                'burst_time': job["burst"],
                'completion_time': time,
                'turnaround_time': turnaround,
                'waiting_time': waiting
            })

            completed.append(pid)
        else:
            # Step 8: Process not finished - add newly arrived processes first
            for p in process:
                if p["arrival"] <= time and remaining[p["PID"]] > 0 and p["PID"] not in queue and p["PID"] != pid:
                    queue.append(p["PID"])

            # Then add current process back to end of queue
            queue.append(pid)

    # Phase 3: Calculate metrics and sort table
    table_sorted = sorted(table, key=lambda x: x['name'])
    avg_waiting = sum(p['waiting_time'] for p in table) / no_of_jobs
    avg_turnaround = sum(p['turnaround_time'] for p in table) / no_of_jobs

    return {
        'table': table_sorted,
        'gantt_chart': gantt,
        'metrics': {
            'average_waiting_time': avg_waiting,
            'average_turnaround_time': avg_turnaround
        }
    }


# Example usage and testing
if __name__ == "__main__":
    # Sample processes
    processes = [
        {"PID": "P1", "arrival": 0, "burst": 5, "priority": 2},
        {"PID": "P2", "arrival": 1, "burst": 3, "priority": 1},
        {"PID": "P3", "arrival": 2, "burst": 2, "priority": 3}
    ]

    print("=" * 80)
    print("FCFS ALGORITHM")
    print("=" * 80)
    result = FCFS(processes)

    print("\nProcess Table:")
    print(f"{'Name':<8} {'Arrival':<10} {'Burst':<10} {'Completion':<12} {'Turnaround':<12} {'Waiting':<10}")
    print("-" * 80)
    for p in result['table']:
        print(f"{p['name']:<8} {p['arrival_time']:<10} {p['burst_time']:<10} "
              f"{p['completion_time']:<12} {p['turnaround_time']:<12} {p['waiting_time']:<10}")

    print("\nGantt Chart:")
    for g in result['gantt_chart']:
        print(f"| {g[0]} ({g[1]}→{g[2]}) ", end="")
    print("|")

    print(f"\nAverage Waiting Time: {result['metrics']['average_waiting_time']:.2f}")
    print(f"Average Turnaround Time: {result['metrics']['average_turnaround_time']:.2f}")

    print("\n" + "=" * 80)
    print("ROUND ROBIN (Quantum = 2)")
    print("=" * 80)
    result = Round_Robin(processes, 2)

    print("\nProcess Table:")
    print(f"{'Name':<8} {'Arrival':<10} {'Burst':<10} {'Completion':<12} {'Turnaround':<12} {'Waiting':<10}")
    print("-" * 80)
    for p in result['table']:
        print(f"{p['name']:<8} {p['arrival_time']:<10} {p['burst_time']:<10} "
              f"{p['completion_time']:<12} {p['turnaround_time']:<12} {p['waiting_time']:<10}")

    print("\nGantt Chart:")
    for g in result['gantt_chart']:
        print(f"| {g[0]} ({g[1]}→{g[2]}) ", end="")
    print("|")

    print(f"\nAverage Waiting Time: {result['metrics']['average_waiting_time']:.2f}")
    print(f"Average Turnaround Time: {result['metrics']['average_turnaround_time']:.2f}")