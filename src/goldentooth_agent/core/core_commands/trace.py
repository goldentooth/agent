from antidote import inject
import builtins
import goldentooth_agent
from goldentooth_agent.core.command import enroll_command, get_command_typer
from goldentooth_agent.core.context import Context
from goldentooth_agent.core.logging import get_logger
import hunter
import hunter.predicates

import typer
from typer import Typer, Context as TyperContext
from typing import Annotated, List

# Global handle for stopping the trace
_active_tracer = None


@enroll_command
@inject
def enroll_trace_command(
    app: Typer = inject[get_command_typer()], logger=inject[get_logger(__name__)]
) -> None:
    """Enroll the trace command."""
    logger.debug("Enrolling trace command...")

    @app.command("trace", help="Start or stop Hunter tracing.")
    def _command(
        typer_context: TyperContext,
        expr: Annotated[
            List[str],
            typer.Argument(
                help="Query expression to trace, or 'stop' to disable",
            ),
        ],
    ) -> None:
        """Start tracing with Hunter using a Q(...) expression. Use 'stop' to disable."""
        context: Context = typer_context.obj
        global _active_tracer

        # Join the list of strings into a single expression
        query = " ".join(expr).strip()
        if query == "stop":
            if _active_tracer:
                _active_tracer.stop()
                logger.info("Stopped active trace.")
                _active_tracer = None
            else:
                logger.info("No active trace to stop.")
            return

        # Build a safe eval environment
        safe_globals = {
            "Q": hunter.Q,
            "Query": hunter.predicates.Query,
            "When": hunter.predicates.When,
            "And": hunter.predicates.And,
            "Or": hunter.predicates.Or,
            "Not": hunter.predicates.Not,
            "CodePrinter": hunter.CodePrinter,
            "VarsPrinter": hunter.VarsPrinter,
            "builtins": builtins,
            "goldentooth_agent": goldentooth_agent,
        }

        try:
            query = eval(query, safe_globals)
        except Exception as e:
            logger.error(f"Error evaluating trace expression: {e}")
            return

        logger.info(f"Starting trace with: {query}")
        _active_tracer = hunter.trace(query)
