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
from typing import Any, override

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import AgentCard, AgentExtension, Task
from a2ui.a2a import try_activate_a2ui_extension
from a2ui.core.schema.constants import VERSION_0_9
from agent import RizzchartsAgentFactory
from a2ui.adk.a2a_extension.send_a2ui_to_client_toolset import (
    A2uiEventConverter,
)
from a2ui.core.schema.constants import A2UI_CLIENT_CAPABILITIES_KEY
from google.adk.a2a.executor.a2a_agent_executor import (
    A2aAgentExecutor,
    A2aAgentExecutorConfig,
)
from google.adk.agents.invocation_context import new_invocation_context_id
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.events.event import Event
from google.adk.events.event_actions import EventActions
from google.adk.runners import Runner

logger = logging.getLogger(__name__)

_A2UI_ENABLED_KEY = "system:a2ui_enabled"
_A2UI_CATALOG_KEY = "system:a2ui_catalog"
_A2UI_EXAMPLES_KEY = "system:a2ui_examples"


def get_a2ui_catalog(ctx: ReadonlyContext):
  """Retrieves the A2UI catalog from the session state.

  Args:
      ctx: The ReadonlyContext for resolving the catalog.

  Returns:
      The A2UI catalog or None if not found.
  """
  return ctx.state.get(_A2UI_CATALOG_KEY)


def get_a2ui_examples(ctx: ReadonlyContext):
  """Retrieves the A2UI examples from the session state.

  Args:
      ctx: The ReadonlyContext for resolving the examples.

  Returns:
      The A2UI examples or None if not found.
  """
  return ctx.state.get(_A2UI_EXAMPLES_KEY)


def get_a2ui_enabled(ctx: ReadonlyContext):
  """Checks if A2UI is enabled in the current session.

  Args:
      ctx: The ReadonlyContext for resolving enablement.

  Returns:
      True if A2UI is enabled, False otherwise.
  """
  return ctx.state.get(_A2UI_ENABLED_KEY, False)


class RizzchartsAgentExecutor(AgentExecutor):
  """Executor for the Rizzcharts agent that handles A2UI session setup."""

  def __init__(
      self,
      base_url: str,
      model: Any,
  ):
    self._base_url = base_url
    self._model = model
    self._executors = {}  # version -> A2aAgentExecutor

  async def execute(
      self,
      context: RequestContext,
      event_queue: EventQueue,
  ) -> None:
    version = try_activate_a2ui_extension(context)
    if not version:
      # If no version negotiated, default to 0.9 (or error if appropriate)
      version = VERSION_0_9

    if version not in self._executors:
      # pylint: disable=import-outside-toplevel
      from google.adk.artifacts import InMemoryArtifactService
      from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
      from google.adk.sessions.in_memory_session_service import InMemorySessionService
      from google.adk.runners import Runner
      from google.adk.a2a.executor.a2a_agent_executor import (
          A2aAgentExecutor,
          A2aAgentExecutorConfig,
      )

      # Create agent, runner, and executor for the negotiated version
      agent = RizzchartsAgentFactory.get_agent(
          base_url=self._base_url,
          version=version,
          model=self._model,
          a2ui_enabled_provider=get_a2ui_enabled,
          a2ui_catalog_provider=get_a2ui_catalog,
          a2ui_examples_provider=get_a2ui_examples,
      )
      runner = Runner(
          app_name=agent.name,
          agent=agent,
          artifact_service=InMemoryArtifactService(),
          session_service=InMemorySessionService(),
          memory_service=InMemoryMemoryService(),
      )

      # Create specialized executor that overrides _prepare_session
      class VersionedRizzchartsExecutor(A2aAgentExecutor):
        def __init__(self, runner, base_url, schema_manager):
          config = A2aAgentExecutorConfig(event_converter=A2uiEventConverter())
          super().__init__(runner=runner, config=config)
          self._base_url = base_url
          self.schema_manager = schema_manager

        @override
        async def _prepare_session(self, context, run_request, runner):
          session = await super()._prepare_session(context, run_request, runner)
          if "base_url" not in session.state:
            session.state["base_url"] = self._base_url

          capabilities = (
              context.message.metadata.get(A2UI_CLIENT_CAPABILITIES_KEY)
              if context.message and context.message.metadata
              else None
          )
          a2ui_catalog = self.schema_manager.get_selected_catalog(
              client_ui_capabilities=capabilities
          )
          examples = self.schema_manager.load_examples(a2ui_catalog, validate=True)

          await runner.session_service.append_event(
              session,
              Event(
                  invocation_id=new_invocation_context_id(),
                  author="system",
                  actions=EventActions(
                      state_delta={
                          _A2UI_ENABLED_KEY: True,
                          _A2UI_CATALOG_KEY: a2ui_catalog,
                          _A2UI_EXAMPLES_KEY: examples,
                      }
                  ),
              ),
          )
          return session

      self._executors[version] = VersionedRizzchartsExecutor(
          runner=runner,
          base_url=self._base_url,
          schema_manager=agent.schema_manager,
      )

    await self._executors[version].execute(context, event_queue)

  async def cancel(
      self, context: RequestContext, event_queue: EventQueue
  ) -> Task | None:
    # No-op for now as individual executors might have state.
    # We could delegate to all if needed, but usually cancel is specific to a session.
    return None
