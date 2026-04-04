from domain.logger import Logger
import psutil
import asyncio
from api.routers.metrics import active_workers, cpu_usage, mem_usage

async def log_system_metrics(logger:Logger, logger_interval_sec:float):
    while True:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()

        # Structlog Logging
        logger.info("System Metrics",
            cpu_percent=cpu,
            memtory_percent=mem.percent,
            memory_used_gb=round(mem.used / (1024**3), 2),
            memory_total_gb=round(mem.total / (1024**3), 2)
        )

        # Prometheus
        cpu_usage.set(cpu)
        mem_usage.set(mem.percent)

        # active_workers.set()

        await asyncio.sleep(logger_interval_sec)