"""System tools for process execution, monitoring, and system information."""

from __future__ import annotations

import asyncio
import os
import platform
import subprocess
import time
from typing import Any

import psutil
from pydantic import Field

from ..flow_agent import FlowIOSchema, FlowTool


# Process Execute Tool
class ProcessExecuteInput(FlowIOSchema):
    """Input schema for process execution tool."""

    command: str = Field(..., description="Command to execute")
    args: list[str] = Field(default_factory=list, description="Command arguments")
    working_directory: str | None = Field(
        default=None, description="Working directory"
    )
    environment: dict[str, str] | None = Field(
        default=None, description="Environment variables"
    )
    timeout: float = Field(default=30.0, description="Execution timeout in seconds")
    capture_output: bool = Field(default=True, description="Capture stdout and stderr")
    shell: bool = Field(default=False, description="Execute in shell")
    input_data: str | None = Field(default=None, description="Data to send to stdin")


class ProcessExecuteOutput(FlowIOSchema):
    """Output schema for process execution tool."""

    command: str = Field(..., description="Executed command")
    return_code: int = Field(..., description="Process return code")
    stdout: str = Field(..., description="Standard output")
    stderr: str = Field(..., description="Standard error")
    execution_time: float = Field(..., description="Execution time in seconds")
    working_directory: str = Field(..., description="Working directory used")
    timed_out: bool = Field(..., description="Whether process timed out")
    success: bool = Field(..., description="Whether execution was successful")
    error: str | None = Field(default=None, description="Error message if failed")


async def process_execute_implementation(
    input_data: ProcessExecuteInput,
) -> ProcessExecuteOutput:
    """Execute system processes with comprehensive monitoring."""
    start_time = time.time()

    try:
        # Prepare command
        if input_data.shell:
            cmd = input_data.command
            if input_data.args:
                cmd += " " + " ".join(input_data.args)
        else:
            cmd = [input_data.command] + input_data.args

        # Prepare environment
        env = os.environ.copy()
        if input_data.environment:
            env.update(input_data.environment)

        # Working directory
        cwd = input_data.working_directory or os.getcwd()
        if not os.path.exists(cwd):
            return ProcessExecuteOutput(
                command=str(cmd),
                return_code=-1,
                stdout="",
                stderr="",
                execution_time=time.time() - start_time,
                working_directory=cwd,
                timed_out=False,
                success=False,
                error=f"Working directory does not exist: {cwd}",
            )

        # Execute process
        try:
            process = (
                await asyncio.create_subprocess_exec(
                    *cmd if not input_data.shell else [],
                    shell=input_data.shell,
                    stdout=subprocess.PIPE if input_data.capture_output else None,
                    stderr=subprocess.PIPE if input_data.capture_output else None,
                    stdin=subprocess.PIPE if input_data.input_data else None,
                    cwd=cwd,
                    env=env,
                )
                if not input_data.shell
                else await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=subprocess.PIPE if input_data.capture_output else None,
                    stderr=subprocess.PIPE if input_data.capture_output else None,
                    stdin=subprocess.PIPE if input_data.input_data else None,
                    cwd=cwd,
                    env=env,
                )
            )

            # Communicate with process
            try:
                stdout_data, stderr_data = await asyncio.wait_for(
                    process.communicate(
                        input=(
                            input_data.input_data.encode()
                            if input_data.input_data
                            else None
                        )
                    ),
                    timeout=input_data.timeout,
                )
                timed_out = False
            except TimeoutError:
                # Kill the process on timeout
                process.kill()
                await process.wait()
                timed_out = True
                stdout_data = stderr_data = b""

            execution_time = time.time() - start_time

            return ProcessExecuteOutput(
                command=str(cmd),
                return_code=process.returncode or 0,
                stdout=(
                    stdout_data.decode("utf-8", errors="replace") if stdout_data else ""
                ),
                stderr=(
                    stderr_data.decode("utf-8", errors="replace") if stderr_data else ""
                ),
                execution_time=execution_time,
                working_directory=cwd,
                timed_out=timed_out,
                success=not timed_out and (process.returncode == 0),
                error="Process timed out" if timed_out else None,
            )

        except FileNotFoundError:
            return ProcessExecuteOutput(
                command=str(cmd),
                return_code=-1,
                stdout="",
                stderr="",
                execution_time=time.time() - start_time,
                working_directory=cwd,
                timed_out=False,
                success=False,
                error=f"Command not found: {input_data.command}",
            )

    except Exception as e:
        return ProcessExecuteOutput(
            command=str(input_data.command),
            return_code=-1,
            stdout="",
            stderr="",
            execution_time=time.time() - start_time,
            working_directory=input_data.working_directory or os.getcwd(),
            timed_out=False,
            success=False,
            error=str(e),
        )


# System Information Tool
class SystemInfoInput(FlowIOSchema):
    """Input schema for system information tool."""

    include_cpu: bool = Field(default=True, description="Include CPU information")
    include_memory: bool = Field(default=True, description="Include memory information")
    include_disk: bool = Field(default=True, description="Include disk information")
    include_network: bool = Field(
        default=True, description="Include network information"
    )
    include_processes: bool = Field(
        default=False, description="Include running processes"
    )
    process_limit: int = Field(
        default=10, description="Maximum number of processes to include"
    )


class SystemInfoOutput(FlowIOSchema):
    """Output schema for system information tool."""

    platform_info: dict[str, str] = Field(..., description="Platform information")
    cpu_info: dict[str, Any] = Field(
        default_factory=dict, description="CPU information"
    )
    memory_info: dict[str, Any] = Field(
        default_factory=dict, description="Memory information"
    )
    disk_info: list[dict[str, Any]] = Field(
        default_factory=list, description="Disk information"
    )
    network_info: dict[str, Any] = Field(
        default_factory=dict, description="Network information"
    )
    processes: list[dict[str, Any]] = Field(
        default_factory=list, description="Running processes"
    )
    timestamp: float = Field(..., description="Information collection timestamp")
    success: bool = Field(..., description="Whether collection was successful")
    error: str | None = Field(default=None, description="Error message if failed")


async def system_info_implementation(input_data: SystemInfoInput) -> SystemInfoOutput:
    """Collect comprehensive system information."""
    try:
        timestamp = time.time()

        # Platform information (always included)
        platform_info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
        }

        # CPU information
        cpu_info = {}
        if input_data.include_cpu:
            cpu_info = {
                "physical_cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "current_frequency": (
                    psutil.cpu_freq().current if psutil.cpu_freq() else None
                ),
                "min_frequency": psutil.cpu_freq().min if psutil.cpu_freq() else None,
                "max_frequency": psutil.cpu_freq().max if psutil.cpu_freq() else None,
                "cpu_usage_percent": psutil.cpu_percent(interval=1),
                "cpu_usage_per_core": psutil.cpu_percent(interval=1, percpu=True),
                "load_average": os.getloadavg() if hasattr(os, "getloadavg") else None,
            }

        # Memory information
        memory_info = {}
        if input_data.include_memory:
            virtual_memory = psutil.virtual_memory()
            swap_memory = psutil.swap_memory()

            memory_info = {
                "total_bytes": virtual_memory.total,
                "available_bytes": virtual_memory.available,
                "used_bytes": virtual_memory.used,
                "free_bytes": virtual_memory.free,
                "usage_percent": virtual_memory.percent,
                "swap_total_bytes": swap_memory.total,
                "swap_used_bytes": swap_memory.used,
                "swap_free_bytes": swap_memory.free,
                "swap_usage_percent": swap_memory.percent,
            }

        # Disk information
        disk_info = []
        if input_data.include_disk:
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info.append(
                        {
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "filesystem": partition.fstype,
                            "total_bytes": usage.total,
                            "used_bytes": usage.used,
                            "free_bytes": usage.free,
                            "usage_percent": (
                                (usage.used / usage.total) * 100
                                if usage.total > 0
                                else 0
                            ),
                        }
                    )
                except PermissionError:
                    # Skip drives we can't access
                    continue

        # Network information
        network_info = {}
        if input_data.include_network:
            network_stats = psutil.net_io_counters()
            network_connections = len(psutil.net_connections())

            network_info = {
                "bytes_sent": network_stats.bytes_sent,
                "bytes_received": network_stats.bytes_recv,
                "packets_sent": network_stats.packets_sent,
                "packets_received": network_stats.packets_recv,
                "errors_in": network_stats.errin,
                "errors_out": network_stats.errout,
                "drops_in": network_stats.dropin,
                "drops_out": network_stats.dropout,
                "active_connections": network_connections,
            }

            # Network interfaces
            interfaces = psutil.net_if_addrs()
            network_info["interfaces"] = {}
            for interface, addresses in interfaces.items():
                network_info["interfaces"][interface] = [
                    {
                        "family": addr.family.name,
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast,
                    }
                    for addr in addresses
                ]

        # Process information
        processes = []
        if input_data.include_processes:
            try:
                running_processes = []
                for proc in psutil.process_iter(
                    ["pid", "name", "cpu_percent", "memory_percent", "status"]
                ):
                    try:
                        proc_info = proc.info
                        proc_info["cpu_percent"] = proc.cpu_percent()
                        running_processes.append(proc_info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                # Sort by CPU usage and take top processes
                running_processes.sort(
                    key=lambda x: x.get("cpu_percent", 0), reverse=True
                )
                processes = running_processes[: input_data.process_limit]

            except Exception:
                # If process enumeration fails, continue without process info
                processes = []

        return SystemInfoOutput(
            platform_info=platform_info,
            cpu_info=cpu_info,
            memory_info=memory_info,
            disk_info=disk_info,
            network_info=network_info,
            processes=processes,
            timestamp=timestamp,
            success=True,
            error=None,
        )

    except Exception as e:
        return SystemInfoOutput(
            platform_info={}, timestamp=time.time(), success=False, error=str(e)
        )


# Tool instances
ProcessExecuteTool = FlowTool(
    name="process_execute",
    input_schema=ProcessExecuteInput,
    output_schema=ProcessExecuteOutput,
    implementation=process_execute_implementation,
    description="Execute system processes with timeout control, environment setup, and output capture",
)

SystemInfoTool = FlowTool(
    name="system_info",
    input_schema=SystemInfoInput,
    output_schema=SystemInfoOutput,
    implementation=system_info_implementation,
    description="Collect comprehensive system information including CPU, memory, disk, and network stats",
)
