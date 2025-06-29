from typing import Callable
from concurrent.futures import ProcessPoolExecutor


def process_pool(processes: dict[Callable:dict] = None, num_workers: int = None):
    """Run multiple processes in parallel using a ProcessPoolExecutor. Each bot should be a callable that accepts
    keyword arguments only.

    Args:
        processes (dict): A dictionary of processes to run with their respective keyword arguments as a dictionary
        num_workers (int): Number of workers to run the processes
    """
    num_workers = num_workers or len(processes) + 1
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        for bot, kwargs in processes.items():
            executor.submit(bot, **kwargs)
