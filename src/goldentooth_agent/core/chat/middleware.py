from __future__ import annotations
from antidote import inject
from typing import Any
from goldentooth_agent.core.agent import AgentBase
from goldentooth_agent.core.agent.middleware import get_agent_th, print_agent_th, run_agent_th
from goldentooth_agent.core.console import console_print_th
from goldentooth_agent.core.schema import InputSchema, OutputSchema
from goldentooth_agent.core.thunk import Thunk, trampoline, compose_chain, final_thunk
from goldentooth_agent.core.tool.request_user_input import request_user_input_th, read_user_input_th

def chat_loop_th() -> Thunk[AgentBase, None]:
  """Thunk to run a chat loop that continuously prompts the user for input."""
  @inject
  async def _thunk(agent: AgentBase) -> None:
    """Run a chat loop that continuously prompts the user for input."""
    while True:
      user_input = await trampoline(None, compose_chain(
        request_user_input_th(),
        read_user_input_th(),
        final_thunk(),
      ))
      agent_output = await trampoline(user_input, compose_chain(
        run_agent_th(agent, InputSchema, OutputSchema),
        final_thunk(),
      ))
      await trampoline(agent, compose_chain(
        print_agent_th(),
        final_thunk(),
      ))
      await trampoline(agent_output, compose_chain(
        console_print_th(agent_output),
        final_thunk(),
      ))
  return Thunk(_thunk)
