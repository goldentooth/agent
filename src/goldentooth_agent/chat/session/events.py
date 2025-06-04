from enum import Enum

class ChatSessionEvents(str, Enum):
  will_start_session = "chat_session_events.will_start_session"
  did_start_session = "chat_session_events.did_start_session"

  will_end_session = "chat_session_events.will_end_session"
  did_end_session = "chat_session_events.did_end_session"

  will_prompt_user = "chat_session_events.will_prompt_user"
  did_prompt_user = "chat_session_events.did_prompt_user"

  will_handle_user_input = "chat_session_events.will_handle_user_input"
  did_handle_user_input = "chat_session_events.did_handle_user_input"

  will_prompt_agent = "chat_session_events.will_prompt_agent"
  did_prompt_agent = "chat_session_events.did_prompt_agent"

  will_handle_agent_output = "chat_session_events.will_handle_agent_output"
  did_handle_agent_output = "chat_session_events.did_handle_agent_output"
