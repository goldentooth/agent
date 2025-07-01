src/goldentooth_agent/core/llm/claude_client.py:131: error: Signature of
"create_chat_completion" incompatible with supertype "LLMClient"  [override]
        async def create_chat_completion(
        ^
src/goldentooth_agent/core/llm/claude_client.py:131: note:      Superclass:
src/goldentooth_agent/core/llm/claude_client.py:131: note:          def create_chat_completion(self, messages: list[dict[str, Any]], model: str = ..., temperature: float = ..., max_tokens: int = ..., stream: bool = ..., **kwargs: Any) -> Coroutine[Any, Any, str | StreamingResponse]
src/goldentooth_agent/core/llm/claude_client.py:131: note:      Subclass:
src/goldentooth_agent/core/llm/claude_client.py:131: note:          def create_chat_completion(self, messages: list[dict[str, Any]], model: str | None = ..., temperature: float = ..., max_tokens: int | None = ..., stream: bool = ..., system: str | None = ..., **kwargs: Any) -> Coroutine[Any, Any, str | ClaudeStreamingResponse]
src/goldentooth_agent/core/rag/rag_service.py:2327: error: Name "search_result"
already defined on line 2250  [no-redef]
                            search_result: SearchResult = SearchResult(
                            ^~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:2337: error: Argument 1 to
"append" of "list" has incompatible type "dict[str, Any]"; expected
"SearchResult"  [arg-type]
                            search_results.append(search_result)
                                                  ^~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_agent.py:102: error: Incompatible types in
assignment (expression has type "list[dict[str, str]] | None", variable has type
"list[dict[str, str]]")  [assignment]
    ...             conversation_history: list[dict[str, str]] = context.get(
                                                                 ^
src/goldentooth_agent/core/rag/rag_agent.py:161: error: Statement is
unreachable  [unreachable]
                        enhanced_question = (
                        ^
src/goldentooth_agent/core/rag/rag_agent.py:183: error: Need type annotation
for "query_analysis"  [var-annotated]
                    query_analysis = context.get("rag.query_analysis", {})
                                     ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_agent.py:188: error: Argument 2 to
"_generate_suggestions" of "RAGAgent" has incompatible type
"dict[Any, Any] | None"; expected "dict[str, Any]"  [arg-type]
    ...  suggestions = self._generate_suggestions(rag_result, query_analysis)
                                                              ^~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_agent.py:196: error: Argument 5 to
"_store_results_in_context" of "RAGAgent" has incompatible type
"dict[Any, Any] | None"; expected "dict[str, Any]"  [arg-type]
                        query_analysis,
                        ^~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_agent.py:428: error: Incompatible return
value type (got "FlowIOSchema", expected "RAGOutput")  [return-value]
                return results[-1]
                       ^~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_agent.py:442: error: Incompatible return
value type (got "Flow[FlowIOSchema, FlowIOSchema]", expected
"Flow[RAGInput, RAGOutput]")  [return-value]
            return self.flow_agent.as_flow()
                   ^~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/agent_codebase/rag_integration.py:150: error:
"RAGService" has no attribute "search"  [attr-defined]
                result = await self.rag_service.search(query, limit=limit)
                               ^~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/agent_codebase/rag_integration.py:249: error: Need
type annotation for "content_pieces" (hint:
"content_pieces: list[<type>] = ...")  [var-annotated]
            content_pieces = []
            ^~~~~~~~~~~~~~
src/goldentooth_agent/core/agent_codebase/rag_integration.py:285: error:
"ClaudeFlowClient" has no attribute "generate_response"  [attr-defined]
                response = await self.rag_service.claude_client.generate_r...
                                 ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~...
src/goldentooth_agent/core/agent_codebase/rag_integration.py:289: error:
Returning Any from function declared to return "str"  [no-any-return]
                return response.get("content", "Unable to generate synthes...
                ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~...
src/goldentooth_agent/cli/commands/codebase.py:244: error: Item "None" of
"CodebaseIntrospectionService | None" has no attribute "get_codebase_overview"
[union-attr]
                overview = await introspection_service.get_codebase_overvi...
                                 ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/cli/commands/codebase.py:266: error: Item "None" of
"CodebaseIntrospectionService | None" has no attribute "compare_codebases"
[union-attr]
                comparison = await introspection_service.compare_codebases...
                                   ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/cli/commands/codebase.py:298: error: Item "None" of
"CodebaseIntrospectionService | None" has no attribute "add_external_codebase"
[union-attr]
                result = await introspection_service.add_external_codebase...
                               ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/cli/commands/codebase.py:325: error: Item "None" of
"CodebaseIntrospectionService | None" has no attribute "initialize"
[union-attr]
            await introspection_service.initialize()
                  ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/cli/commands/codebase.py:327: error: Item "None" of
"CodebaseIntrospectionService | None" has no attribute
"list_available_codebases"  [union-attr]
            codebases = introspection_service.list_available_codebases()
                        ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/cli/commands/codebase.py:370: error: Item "None" of
"CodebaseIntrospectionService | None" has no attribute "initialize"
[union-attr]
            await introspection_service.initialize()
                  ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/cli/commands/codebase.py:372: error: Item "None" of
"CodebaseIntrospectionService | None" has no attribute "collection"
[union-attr]
            token_tracker = introspection_service.collection.token_tracker
                            ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/cli/commands/instructor.py:278: error: Returning Any from
function declared to return "FlowIOSchema"  [no-any-return]
                return results[-1]
                ^~~~~~~~~~~~~~~~~~
src/goldentooth_agent/cli/commands/docs.py:65: error: Name "docs" may be
undefined  [possibly-undefined]
                    for doc_id in docs:
                                  ^~~~
src/goldentooth_agent/cli/commands/agents.py:65: error: If condition is always
true  [redundant-expr]
                agent.system_flow.name if agent.system_flow is not None el...
                                          ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/cli/commands/agents.py:68: error: If condition is always
true  [redundant-expr]
                agent.processing_flow.name if agent.processing_flow is not...
                                              ^~~~~~~~~~~~~~~~~~~~~~~~~~~~...
