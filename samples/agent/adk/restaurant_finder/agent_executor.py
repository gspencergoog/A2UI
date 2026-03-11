# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    DataPart,
    Part,
    Task,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import (
    new_agent_parts_message,
    new_agent_text_message,
    new_task,
)
from a2a.utils.errors import ServerError
from a2ui.a2a import A2UI_EXTENSION_URI_V0_8, A2UI_EXTENSION_URI_V0_9
from v0_8.agent import RestaurantAgent as RestaurantAgentV08
from v0_9.agent import RestaurantAgent as RestaurantAgentV09

logger = logging.getLogger(__name__)


class RestaurantAgentExecutor(AgentExecutor):
  """Restaurant AgentExecutor Example."""

  def __init__(self, ui_agent_v0_8: RestaurantAgentV08, ui_agent_v0_9: RestaurantAgentV09, text_agent: RestaurantAgentV09):
    # Instantiate two agents for UI (one per version) and one for text-only.
    # The appropriate one will be chosen at execution time.
    self.ui_agent_v0_8 = ui_agent_v0_8
    self.ui_agent_v0_9 = ui_agent_v0_9
    self.text_agent = text_agent

  async def execute(
      self,
      context: RequestContext,
      event_queue: EventQueue,
  ) -> None:
    query = ""
    ui_event_part = None
    action = None

    logger.info(f"--- Client requested extensions: {context.requested_extensions} ---")

    use_ui = False
    requested_version = None

    if A2UI_EXTENSION_URI_V0_9 in context.requested_extensions or (
        context.message and context.message.extensions and A2UI_EXTENSION_URI_V0_9 in context.message.extensions
    ):
      context.add_activated_extension(A2UI_EXTENSION_URI_V0_9)
      use_ui = True
      requested_version = "v0.9"
    elif A2UI_EXTENSION_URI_V0_8 in context.requested_extensions or (
        context.message and context.message.extensions and A2UI_EXTENSION_URI_V0_8 in context.message.extensions
    ):
      context.add_activated_extension(A2UI_EXTENSION_URI_V0_8)
      use_ui = True
      requested_version = "v0.8"

    # Determine which agent to use based on whether the a2ui extension is active.
    if use_ui:
      if requested_version == "v0.8":
        agent = self.ui_agent_v0_8
        logger.info("--- AGENT_EXECUTOR: A2UI extension v0.8 is active. Using v0.8 UI agent. ---")
      else:
        agent = self.ui_agent_v0_9
        logger.info("--- AGENT_EXECUTOR: A2UI extension v0.9 is active. Using v0.9 UI agent. ---")
    else:
      agent = self.text_agent
      logger.info(
          "--- AGENT_EXECUTOR: A2UI extension is not active. Using text agent. ---"
      )

    if context.message and context.message.parts:
      logger.info(
          f"--- AGENT_EXECUTOR: Processing {len(context.message.parts)} message"
          " parts ---"
      )
      for i, part in enumerate(context.message.parts):
        if isinstance(part.root, DataPart):
          if "userAction" in part.root.data:
            logger.info(f"  Part {i}: Found a2ui UI ClientEvent payload (wrapped userAction).")
            ui_event_part = part.root.data["userAction"]
          elif "action" in part.root.data:
            logger.info(f"  Part {i}: Found a2ui UI ClientEvent payload (wrapped action).")
            ui_event_part = part.root.data["action"]
          elif part.root.data.get("kind") == "clientEvent":
            logger.info(f"  Part {i}: Found a2ui UI ClientEvent payload (unwrapped).")
            ui_event_part = part.root.data
          else:
            logger.info(f"  Part {i}: DataPart (data: {part.root.data})")
        elif isinstance(part.root, TextPart):
          logger.info(f"  Part {i}: TextPart (text: {part.root.text})")
        else:
          logger.info(f"  Part {i}: Unknown part type ({type(part.root)})")

    if ui_event_part:
      logger.info(f"Received a2ui ClientEvent: {ui_event_part}")
      # Support both v0.8 (actionName) and v0.9 (name/event)
      action = ui_event_part.get("name") or ui_event_part.get("event") or ui_event_part.get("actionName")
      ctx = ui_event_part.get("context", {}) or ui_event_part.get("args", {})

      if action == "book_restaurant":
        restaurant_name = ctx.get("restaurantName", "Unknown Restaurant")
        address = ctx.get("address", "Address not provided")
        image_url = ctx.get("imageUrl", "")
        query = (
            f"USER_WANTS_TO_BOOK: {restaurant_name}, Address: {address}, ImageURL:"
            f" {image_url}"
        )

      elif action == "submit_booking":
        restaurant_name = ctx.get("restaurantName", "Unknown Restaurant")
        party_size = ctx.get("partySize", "Unknown Size")
        reservation_time = ctx.get("reservationTime", "Unknown Time")
        dietary_reqs = ctx.get("dietary", "None")
        image_url = ctx.get("imageUrl", "")
        query = (
            f"User submitted a booking for {restaurant_name} for {party_size} people at"
            f" {reservation_time} with dietary requirements: {dietary_reqs}. The image"
            f" URL is {image_url}"
        )

      else:
        query = f"User submitted an event: {action} with data: {ctx}"
    else:
      logger.info("No a2ui UI event part found. Falling back to text input.")
      query = context.get_user_input()

    logger.info(f"--- AGENT_EXECUTOR: Final query for LLM: '{query}' ---")

    task = context.current_task

    if not task:
      task = new_task(context.message)
      await event_queue.enqueue_event(task)
    updater = TaskUpdater(event_queue, task.id, task.context_id)

    async for item in agent.stream(query, task.context_id):
      is_task_complete = item["is_task_complete"]
      if not is_task_complete:
        await updater.update_status(
            TaskState.working,
            new_agent_text_message(item["updates"], task.context_id, task.id),
        )
        continue

      final_state = (
          TaskState.completed
          if action == "submit_booking"
          else TaskState.input_required
      )

      if "parts" in item:
        final_parts = item["parts"]
      else:
        content = item["content"]
        final_parts = [Part(root=TextPart(text=content.strip()))] if content.strip() else []

      logger.info("--- FINAL PARTS TO BE SENT ---")
      for i, part in enumerate(final_parts):
        logger.info(f"  - Part {i}: Type = {type(part.root)}")
        if isinstance(part.root, TextPart):
          logger.info(f"    - Text: {part.root.text[:200]}...")
        elif isinstance(part.root, DataPart):
          logger.info(f"    - Data: {str(part.root.data)[:200]}...")
      logger.info("-----------------------------")

      await updater.update_status(
          final_state,
          new_agent_parts_message(final_parts, task.context_id, task.id),
          final=(final_state == TaskState.completed),
      )
      break

  async def cancel(
      self, request: RequestContext, event_queue: EventQueue
  ) -> Task | None:
    raise ServerError(error=UnsupportedOperationError())
