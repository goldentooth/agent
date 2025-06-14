from __future__ import annotations
from antidote import inject
from typing import Any
from goldentooth_agent.core.agent import AgentBase
from goldentooth_agent.core.agent.middleware import get_agent_th, print_agent_th, run_agent
from goldentooth_agent.core.console import console_print
from goldentooth_agent.core.schema import InputSchema, OutputSchema
from goldentooth_agent.core.thunk import Thunk, trampoline, compose_chain
from goldentooth_agent.core.console.tool import request_user_input_th, read_user_input_th

def chat_loop_th() -> Thunk[AgentBase, None]:
  """Thunk to run a chat loop that continuously prompts the user for input."""
  @inject
  async def _thunk(agent: AgentBase) -> None:
    """Run a chat loop that continuously prompts the user for input."""
    while True:
      user_input = await trampoline(None, compose_chain(
        request_user_input_th(),
        read_user_input_th(),
      ))
      agent_output = await trampoline(user_input, compose_chain(
        run_agent(agent, InputSchema, OutputSchema),
      ))
      await trampoline(agent, compose_chain(
        print_agent_th(),
      ))
      await trampoline(agent_output, compose_chain(
        console_print(agent_output),
      ))
  return Thunk(_thunk)
