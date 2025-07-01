src/goldentooth_agent/core/llm/claude_client.py:131: error: Signature of
"create_chat_completion" incompatible with supertype "LLMClient"  [override]
        async def create_chat_completion(
        ^
src/goldentooth_agent/core/llm/claude_client.py:131: note:      Superclass:
src/goldentooth_agent/core/llm/claude_client.py:131: note:          def create_chat_completion(self, messages: list[dict[str, Any]], model: str = ..., temperature: float = ..., max_tokens: int = ..., stream: bool = ..., **kwargs: Any) -> Coroutine[Any, Any, str | StreamingResponse]
src/goldentooth_agent/core/llm/claude_client.py:131: note:      Subclass:
src/goldentooth_agent/core/llm/claude_client.py:131: note:          def create_chat_completion(self, messages: list[dict[str, Any]], model: str | None = ..., temperature: float = ..., max_tokens: int | None = ..., stream: bool = ..., system: str | None = ..., **kwargs: Any) -> Coroutine[Any, Any, str | ClaudeStreamingResponse]
src/goldentooth_agent/core/rag/rag_service.py:952: error: Name "cast" is not
defined  [name-defined]
                analyzer = ChunkRelationshipAnalyzer(cast(EmbeddingsServic...
                                                     ^~~~
src/goldentooth_agent/core/rag/rag_service.py:952: note: Did you forget to import it from "typing"? (Suggestion: "from typing import cast")
src/goldentooth_agent/core/rag/rag_service.py:1256: note: "hybrid_query" of "RAGService" defined here
src/goldentooth_agent/core/rag/rag_service.py:1817: error: Unexpected keyword
argument "include_metadata" for "hybrid_query" of "RAGService"  [call-arg]
                hybrid_result = await self.hybrid_query(
                                      ^
src/goldentooth_agent/core/rag/rag_service.py:1817: error: Unexpected keyword
argument "include_explanations" for "hybrid_query" of "RAGService"  [call-arg]
                hybrid_result = await self.hybrid_query(
                                      ^
src/goldentooth_agent/core/rag/rag_service.py:2327: error: Incompatible types
in assignment (expression has type "SearchResult", variable has type
"dict[str, Any]")  [assignment]
                            search_result = SearchResult(
                                            ^
src/goldentooth_agent/core/rag/rag_service.py:2337: error: Argument 1 to
"append" of "list" has incompatible type "dict[str, Any]"; expected
"SearchResult"  [arg-type]
                            search_results.append(search_result)
                                                  ^~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:2370: error: If condition is
always true  [redundant-expr]
                                if expansion_result is not None
                                   ^~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:2375: error: If condition is
always true  [redundant-expr]
                                if expansion_result is not None
                                   ^~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:2379: error: If condition is
always true  [redundant-expr]
    ...                   expansion_result.key_terms if expansion_result is n...
                                                        ^~~~~~~~~~~~~~~~~~~~~...
src/goldentooth_agent/core/rag/rag_service.py:2382: error: If condition is
always true  [redundant-expr]
    ...                    expansion_result.synonyms if expansion_result is n...
                                                        ^~~~~~~~~~~~~~~~~~~~~...
src/goldentooth_agent/core/rag/rag_service.py:2385: error: If condition is
always true  [redundant-expr]
    ...               expansion_result.related_terms if expansion_result is n...
                                                        ^~~~~~~~~~~~~~~~~~~~~...
src/goldentooth_agent/core/rag/rag_service.py:2388: error: If condition is
always true  [redundant-expr]
    ...                  expansion_result.confidence if expansion_result is n...
                                                        ^~~~~~~~~~~~~~~~~~~~~...
src/goldentooth_agent/core/rag/rag_service.py:2391: error: If condition is
always true  [redundant-expr]
    ...                 expansion_result.suggestions if expansion_result is n...
                                                        ^~~~~~~~~~~~~~~~~~~~~...
src/goldentooth_agent/core/rag/rag_agent.py:102: error: Need type annotation
for "conversation_history"  [var-annotated]
                    conversation_history = context.get(
                                           ^
src/goldentooth_agent/core/rag/rag_agent.py:122: error: "set" of "Context" does
not return a value (it only ever returns None)  [func-returns-value]
                    context = context.fork().set(analysis_key.path, query_...
                              ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~...
src/goldentooth_agent/core/rag/rag_agent.py:136: error: "set" of "Context" does
not return a value (it only ever returns None)  [func-returns-value]
                    context = context.fork().set(conv_key.path, conversati...
                              ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~...
src/goldentooth_agent/core/rag/rag_agent.py:159: error: Statement is
unreachable  [unreachable]
                        enhanced_question = (
                        ^
src/goldentooth_agent/core/rag/rag_agent.py:166: error: Argument "max_results"
to "enhanced_query" of "RAGService" has incompatible type "int | None"; expected
"int"  [arg-type]
                        max_results=max_results,
                                    ^~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_agent.py:167: error: Argument
"enable_expansion" to "enhanced_query" of "RAGService" has incompatible type
"bool | None"; expected "bool"  [arg-type]
                        enable_expansion=enable_expansion,
                                         ^~~~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_agent.py:168: error: Argument
"enable_fusion" to "enhanced_query" of "RAGService" has incompatible type
"bool | None"; expected "bool"  [arg-type]
                        enable_fusion=enable_fusion,
                                      ^~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_agent.py:181: error: Need type annotation
for "query_analysis"  [var-annotated]
                    query_analysis = context.get("rag.query_analysis", {})
                                     ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_agent.py:186: error: Argument 2 to
"_generate_suggestions" of "RAGAgent" has incompatible type
"dict[Any, Any] | None"; expected "dict[str, Any]"  [arg-type]
    ...  suggestions = self._generate_suggestions(rag_result, query_analysis)
                                                              ^~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_agent.py:194: error: Argument 5 to
"_store_results_in_context" of "RAGAgent" has incompatible type
"dict[Any, Any] | None"; expected "dict[str, Any]"  [arg-type]
                        query_analysis,
                        ^~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_agent.py:426: error: Incompatible return
value type (got "FlowIOSchema", expected "RAGOutput")  [return-value]
                return results[-1]
                       ^~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_agent.py:440: error: Incompatible return
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
src/goldentooth_agent/cli/commands/codebase.py:465: error: Item "None" of
"CodebaseIntrospectionService | None" has no attribute "initialize" 
[union-attr]
            await introspection_service.initialize()
                  ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/cli/commands/codebase.py:467: error: Item "None" of
"CodebaseIntrospectionService | None" has no attribute "collection" 
[union-attr]
            token_tracker = introspection_service.collection.token_tracker
                            ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/cli/commands/chat.py:315: error: Argument 1 to
"process_agent_input" has incompatible type "FlowAgent | None"; expected
"FlowAgent"  [arg-type]
    ...                 result = await process_agent_input(agent, input_data)
                                                           ^~~~~
src/goldentooth_agent/cli/commands/chat.py:322: error: Argument 1 to
"process_agent_input" has incompatible type "FlowAgent | None"; expected
"FlowAgent"  [arg-type]
    ...                 result = await process_agent_input(agent, input_data)
                                                           ^~~~~
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
