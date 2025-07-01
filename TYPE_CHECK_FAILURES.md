src/goldentooth_agent/core/embeddings/hybrid_search.py:262: error: Unpacked
dict entry 0 has incompatible type "str"; expected
"SupportsKeysAndGetItem[str, object]"  [dict-item]
                            **doc_info,
                              ^~~~~~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:262: note: "str" is missing following "SupportsKeysAndGetItem" protocol member:
src/goldentooth_agent/core/embeddings/hybrid_search.py:262: note:     keys
src/goldentooth_agent/core/embeddings/hybrid_search.py:262: note: Following member(s) of "str" have conflicts:
src/goldentooth_agent/core/embeddings/hybrid_search.py:262: note:     Expected:
src/goldentooth_agent/core/embeddings/hybrid_search.py:262: note:         def __getitem__(self, str, /) -> object
src/goldentooth_agent/core/embeddings/hybrid_search.py:262: note:     Got:
src/goldentooth_agent/core/embeddings/hybrid_search.py:262: note:         def __getitem__(self, SupportsIndex | slice[Any, Any, Any], /) -> str
src/goldentooth_agent/core/embeddings/hybrid_search.py:262: note:     Expected:
src/goldentooth_agent/core/embeddings/hybrid_search.py:262: note:         def __getitem__(self, str, /) -> object
src/goldentooth_agent/core/embeddings/hybrid_search.py:262: note:     Got:
src/goldentooth_agent/core/embeddings/hybrid_search.py:262: note:         def __getitem__(self, SupportsIndex | slice[Any, Any, Any], /) -> str
src/goldentooth_agent/core/embeddings/hybrid_search.py:262: note:     Expected:
src/goldentooth_agent/core/embeddings/hybrid_search.py:262: note:         def __getitem__(self, str, /) -> object
src/goldentooth_agent/core/embeddings/hybrid_search.py:262: note:     Got:
src/goldentooth_agent/core/embeddings/hybrid_search.py:262: note:         def __getitem__(self, SupportsIndex | slice[Any, Any, Any], /) -> str
src/goldentooth_agent/core/embeddings/hybrid_search.py:353: error: Returning
Any from function declared to return "str"  [no-any-return]
                return result["chunk_id"]
                ^~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:430: error: Incompatible
types in assignment (expression has type "dict[str, Any]", target has type
"str")  [assignment]
                    self._document_corpus[doc_id] = doc
                                                    ^~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:459: error: Need type
annotation for "document_frequencies"  [var-annotated]
            document_frequencies = defaultdict(int)
            ^~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:508: error: Argument 1
to "len" has incompatible type "list[dict[str, int]] | None"; expected "Sized" 
[arg-type]
            if doc_index >= len(self._term_frequencies) or doc_index >= le...
                                ^~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:509: error: Argument 1
to "len" has incompatible type "list[int] | None"; expected "Sized"  [arg-type]
                self._document_lengths
                ^~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:513: error: Value of
type "list[dict[str, int]] | None" is not indexable  [index]
            term_freq = self._term_frequencies[doc_index]
                        ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:514: error: Value of
type "list[int] | None" is not indexable  [index]
            doc_length = self._document_lengths[doc_index]
                         ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:515: error: Value of
type "dict[str, Any] | None" is not indexable  [index]
            avg_doc_length = self._corpus_stats["average_document_length"]
                             ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:516: error: Value of
type "dict[str, Any] | None" is not indexable  [index]
            total_docs = self._corpus_stats["total_documents"]
                         ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:517: error: Value of
type "dict[str, Any] | None" is not indexable  [index]
            doc_frequencies = self._corpus_stats["document_frequencies"]
                              ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/agent_codebase/collection.py:329: error: Name
"current_chunk" already defined on line 319  [no-redef]
                        current_chunk: list[str] = []
                        ^~~~~~~~~~~~~
src/goldentooth_agent/core/agent_codebase/collection.py:338: error: Name
"current_chunk" already defined on line 319  [no-redef]
                    current_chunk: list[str] = []
                    ^~~~~~~~~~~~~
src/goldentooth_agent/core/agent_codebase/collection.py:363: error: Name
"current_chunk" already defined on line 350  [no-redef]
                        current_chunk: list[str] = []
                        ^~~~~~~~~~~~~
src/goldentooth_agent/core/agent_codebase/collection.py:372: error: Name
"current_chunk" already defined on line 350  [no-redef]
                    current_chunk: list[str] = []
                    ^~~~~~~~~~~~~
src/goldentooth_agent/core/agent_codebase/collection.py:392: error: Name
"current_chunk" already defined on line 384  [no-redef]
                    current_chunk: list[str] = []
                    ^~~~~~~~~~~~~
src/goldentooth_agent/core/agent_codebase/collection.py:436: error: Statement
is unreachable  [unreachable]
            formatted_results = []
            ^~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/agent_codebase/collection.py:437: error: Name
"results" is not defined  [name-defined]
            for result in results:
                          ^~~~~~~
src/goldentooth_agent/core/agent_codebase/introspection.py:186: error:
"dict[str, Any]" has no attribute "content"  [attr-defined]
                    "content": result.content,
                               ^~~~~~~~~~~~~~
src/goldentooth_agent/core/agent_codebase/introspection.py:187: error:
"dict[str, Any]" has no attribute "score"  [attr-defined]
                    "score": result.score,
                             ^~~~~~~~~~~~
src/goldentooth_agent/core/agent_codebase/introspection.py:188: error:
"dict[str, Any]" has no attribute "metadata"  [attr-defined]
                    "metadata": result.metadata,
                                ^~~~~~~~~~~~~~~
src/goldentooth_agent/core/agent_codebase/introspection.py:190: error:
"dict[str, Any]" has no attribute "metadata"  [attr-defined]
                        "file_path": result.metadata.get("file_path", ""),
                                     ^~~~~~~~~~~~~~~
src/goldentooth_agent/core/agent_codebase/introspection.py:191: error:
"dict[str, Any]" has no attribute "metadata"  [attr-defined]
                        "module_path": result.metadata.get("module_path", ...
                                       ^~~~~~~~~~~~~~~
src/goldentooth_agent/core/agent_codebase/introspection.py:192: error:
"dict[str, Any]" has no attribute "metadata"  [attr-defined]
                        "line_start": result.metadata.get("line_start", 0)...
                                      ^~~~~~~~~~~~~~~
src/goldentooth_agent/core/agent_codebase/introspection.py:193: error:
"dict[str, Any]" has no attribute "metadata"  [attr-defined]
                        "line_end": result.metadata.get("line_end", 0),
                                    ^~~~~~~~~~~~~~~
src/goldentooth_agent/core/agent_codebase/introspection.py:198: error:
"dict[str, Any]" has no attribute "metadata"  [attr-defined]
                if query.include_source and result.metadata.get("document_...
                                            ^~~~~~~~~~~~~~~
src/goldentooth_agent/core/agent_codebase/introspection.py:204: error:
"dict[str, Any]" has no attribute "metadata"  [attr-defined]
    ...     source_content = await self._find_related_source(result.metadata)
                                                             ^~~~~~~~~~~~~~~
src/goldentooth_agent/core/agent_codebase/introspection.py:361: error:
Returning Any from function declared to return "str | None"  [no-any-return]
                    return (
                    ^
src/goldentooth_agent/core/llm/claude_client.py:76: error: Argument 1 to
"AsyncAnthropic" has incompatible type "**dict[str, str]"; expected
"float | Timeout | NotGiven | None"  [arg-type]
            self._client = AsyncAnthropic(**client_kwargs)
                                            ^~~~~~~~~~~~~
src/goldentooth_agent/core/llm/claude_client.py:76: error: Argument 1 to
"AsyncAnthropic" has incompatible type "**dict[str, str]"; expected "int" 
[arg-type]
            self._client = AsyncAnthropic(**client_kwargs)
                                            ^~~~~~~~~~~~~
src/goldentooth_agent/core/llm/claude_client.py:76: error: Argument 1 to
"AsyncAnthropic" has incompatible type "**dict[str, str]"; expected
"Mapping[str, str] | None"  [arg-type]
            self._client = AsyncAnthropic(**client_kwargs)
                                            ^~~~~~~~~~~~~
src/goldentooth_agent/core/llm/claude_client.py:76: error: Argument 1 to
"AsyncAnthropic" has incompatible type "**dict[str, str]"; expected
"Mapping[str, object] | None"  [arg-type]
            self._client = AsyncAnthropic(**client_kwargs)
                                            ^~~~~~~~~~~~~
src/goldentooth_agent/core/llm/claude_client.py:76: error: Argument 1 to
"AsyncAnthropic" has incompatible type "**dict[str, str]"; expected
"AsyncClient | None"  [arg-type]
            self._client = AsyncAnthropic(**client_kwargs)
                                            ^~~~~~~~~~~~~
src/goldentooth_agent/core/llm/claude_client.py:76: error: Argument 1 to
"AsyncAnthropic" has incompatible type "**dict[str, str]"; expected "bool" 
[arg-type]
            self._client = AsyncAnthropic(**client_kwargs)
                                            ^~~~~~~~~~~~~
src/goldentooth_agent/core/llm/claude_client.py:121: error: Argument "messages"
to "create" of "AsyncInstructor" has incompatible type "list[dict[str, Any]]";
expected
"list[ChatCompletionDeveloperMessageParam | ChatCompletionSystemMessageParam | ChatCompletionUserMessageParam | ChatCompletionAssistantMessageParam | ChatCompletionToolMessageParam | ChatCompletionFunctionMessageParam]"
 [arg-type]
                    messages=messages,
                             ^~~~~~~~
src/goldentooth_agent/core/llm/claude_client.py:175: error: Incompatible return
value type (got "ClaudeStreamingResponse", expected "str | StreamingResponse") 
[return-value]
                    return ClaudeStreamingResponse(response_stream)
                           ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/cli/commands/git_sync.py:199: error: Item "None" of
"GitHubClient | None" has no attribute "sync_organization"  [union-attr]
                    github_result = github_client.sync_organization(
                                    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:465: error: Name "docs" may be
undefined  [possibly-undefined]
                        "documents_analyzed": len(docs) if store_type else...
                                                  ^~~~
src/goldentooth_agent/core/rag/rag_service.py:465: error: Name "total_docs" may
be undefined  [possibly-undefined]
    ...        "documents_analyzed": len(docs) if store_type else total_docs,
                                                                  ^~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:862: error: Argument 1 to
"ChunkRelationshipAnalyzer" has incompatible type
"OpenAIEmbeddingsService | EmbeddingsService"; expected "EmbeddingsService" 
[arg-type]
                analyzer = ChunkRelationshipAnalyzer(self.embeddings_servi...
                                                     ^~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:890: error: Function is missing a
type annotation for one or more arguments  [no-untyped-def]
        async def query_with_relationships(
        ^
src/goldentooth_agent/core/rag/rag_service.py:950: error: Argument 1 to
"ChunkRelationshipAnalyzer" has incompatible type
"OpenAIEmbeddingsService | EmbeddingsService"; expected "EmbeddingsService" 
[arg-type]
                analyzer = ChunkRelationshipAnalyzer(self.embeddings_servi...
                                                     ^~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:959: error: Unexpected keyword
argument "chunk_id" for "get_document_chunks" of "VectorStore"  [call-arg]
                        chunk_details = self.vector_store.get_document_chu...
                                        ^
src/goldentooth_agent/core/rag/rag_service.py:1097: error: "DocumentStore" has
no attribute "get_store"  [attr-defined]
                documents = self.document_store.get_store(store_type).list...
                            ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:1110: error: "DocumentStore" has
no attribute "get_store"  [attr-defined]
                        store = self.document_store.get_store(store_name)
                                ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:1158: error: Unexpected keyword
argument "chunk_id" for "get_document_chunks" of "VectorStore"  [call-arg]
                chunk_details = self.vector_store.get_document_chunks(
                                ^
src/goldentooth_agent/core/rag/rag_service.py:1255: note: "hybrid_query" of "RAGService" defined here
src/goldentooth_agent/core/rag/rag_service.py:1259: error: Incompatible default
for argument "store_type" (default has type "None", argument has type "str") 
[assignment]
            store_type: str = None,
                              ^~~~
src/goldentooth_agent/core/rag/rag_service.py:1259: note: PEP 484 prohibits implicit Optional. Accordingly, mypy has changed its default to no_implicit_optional=True
src/goldentooth_agent/core/rag/rag_service.py:1259: note: Use https://github.com/hauntsaninja/no_implicit_optional to automatically upgrade your codebase
src/goldentooth_agent/core/rag/rag_service.py:1507: error: Incompatible default
for argument "store_type" (default has type "None", argument has type "str") 
[assignment]
            store_type: str = None,
                              ^~~~
src/goldentooth_agent/core/rag/rag_service.py:1507: note: PEP 484 prohibits implicit Optional. Accordingly, mypy has changed its default to no_implicit_optional=True
src/goldentooth_agent/core/rag/rag_service.py:1507: note: Use https://github.com/hauntsaninja/no_implicit_optional to automatically upgrade your codebase
src/goldentooth_agent/core/rag/rag_service.py:1622: error: Returning Any from
function declared to return "str"  [no-any-return]
                return result["chunk_id"]
                ^~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:1633: error: Returning Any from
function declared to return "float"  [no-any-return]
            return sum(scores) / len(scores)
            ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:1815: error: Unexpected keyword
argument "include_metadata" for "hybrid_query" of "RAGService"  [call-arg]
                hybrid_result = await self.hybrid_query(
                                      ^
src/goldentooth_agent/core/rag/rag_service.py:1815: error: Unexpected keyword
argument "include_explanations" for "hybrid_query" of "RAGService"  [call-arg]
                hybrid_result = await self.hybrid_query(
                                      ^
src/goldentooth_agent/core/rag/rag_service.py:1818: error: Argument
"store_type" to "hybrid_query" of "RAGService" has incompatible type
"str | None"; expected "str"  [arg-type]
                    store_type=store_type,
                               ^~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:2039: error: Argument
"max_clusters" to "query_with_fusion" of "RAGService" has incompatible type
"float"; expected "int"  [arg-type]
                    max_clusters=config.get("max_clusters", 3),
                                 ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:2250: error: Argument
"store_type" to "hybrid_query" of "RAGService" has incompatible type
"str | None"; expected "str"  [arg-type]
                            store_type=store_type,
                                       ^~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:2289: error: Argument
"store_type" to "hybrid_query" of "RAGService" has incompatible type
"str | None"; expected "str"  [arg-type]
                            store_type=store_type,
                                       ^~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:2325: error: Incompatible types
in assignment (expression has type "SearchResult", variable has type
"dict[str, Any]")  [assignment]
                            search_result = SearchResult(
                                            ^
src/goldentooth_agent/core/rag/rag_service.py:2339: error: Argument
"search_results" to "fuse_chunks" of "ChunkFusion" has incompatible type
"list[dict[str, Any]]"; expected "list[SearchResult]"  [arg-type]
                            search_results=search_results,
                                           ^~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:2368: error: "expansion_result"
has type "QueryExpansion" which does not implement __bool__ or __len__ so it
could always be true in boolean context  [truthy-bool]
                                if expansion_result
                                   ^~~~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:2373: error: "expansion_result"
has type "QueryExpansion" which does not implement __bool__ or __len__ so it
could always be true in boolean context  [truthy-bool]
                                if expansion_result
                                   ^~~~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:2377: error: "expansion_result"
has type "QueryExpansion" which does not implement __bool__ or __len__ so it
could always be true in boolean context  [truthy-bool]
    ...                   expansion_result.key_terms if expansion_result else...
                                                        ^~~~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:2380: error: "expansion_result"
has type "QueryExpansion" which does not implement __bool__ or __len__ so it
could always be true in boolean context  [truthy-bool]
    ...                    expansion_result.synonyms if expansion_result else...
                                                        ^~~~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:2383: error: "expansion_result"
has type "QueryExpansion" which does not implement __bool__ or __len__ so it
could always be true in boolean context  [truthy-bool]
    ...               expansion_result.related_terms if expansion_result else...
                                                        ^~~~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:2386: error: "expansion_result"
has type "QueryExpansion" which does not implement __bool__ or __len__ so it
could always be true in boolean context  [truthy-bool]
    ...                  expansion_result.confidence if expansion_result else...
                                                        ^~~~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:2389: error: "expansion_result"
has type "QueryExpansion" which does not implement __bool__ or __len__ so it
could always be true in boolean context  [truthy-bool]
    ...                 expansion_result.suggestions if expansion_result else...
                                                        ^~~~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:2658: error: Missing type
parameters for generic type "list"  [type-arg]
            fused_answers: list,
                           ^
src/goldentooth_agent/examples/instructor/agents.py:80: error: Missing named
argument "age" for "PersonData"  [call-arg]
                    error_result = PersonData(
                                   ^
src/goldentooth_agent/examples/instructor/agents.py:80: error: Missing named
argument "occupation" for "PersonData"  [call-arg]
                    error_result = PersonData(
                                   ^
src/goldentooth_agent/examples/instructor/agents.py:80: error: Missing named
argument "location" for "PersonData"  [call-arg]
                    error_result = PersonData(
                                   ^
src/goldentooth_agent/examples/instructor/agents.py:152: error: Name
"input_data" may be undefined  [possibly-undefined]
                        text=input_data.message if "input_data" in locals(...
                             ^~~~~~~~~~
src/goldentooth_agent/core/rag/simple_rag_agent.py:64: error: Returning Any
from function declared to return "dict[str, Any]"  [no-any-return]
            return response_obj
            ^~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/simple_rag_agent.py:83: error: Returning Any
from function declared to return "float"  [no-any-return]
            return round(confidence, 2)
            ^~~~~~~~~~~~~~~~~~~~~~~~~~~
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
src/goldentooth_agent/core/rag/rag_agent.py:416: error: Function is missing a
return type annotation  [no-untyped-def]
            async def input_stream():
            ^
src/goldentooth_agent/core/rag/rag_agent.py:421: error: Call to untyped
function "input_stream" in typed context  [no-untyped-call]
            async for result in flow(input_stream()):
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
src/goldentooth_agent/cli/commands/codebase.py:57: error: Item "None" of
"CodebaseIntrospectionService | None" has no attribute "collection" 
[union-attr]
                result = await introspection_service.collection.index_code...
                               ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/cli/commands/codebase.py:63: error: Item "None" of
"CodebaseIntrospectionService | None" has no attribute "collection" 
[union-attr]
                    result = await introspection_service.collection.index_...
                                   ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/cli/commands/codebase.py:67: error: Item "None" of
"CodebaseIntrospectionService | None" has no attribute "index_current_codebase" 
[union-attr]
                    result = await introspection_service.index_current_cod...
                                   ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~...
src/goldentooth_agent/cli/commands/codebase.py:165: error: Item "None" of
"CodebaseIntrospectionService | None" has no attribute "query"  [union-attr]
                result = await introspection_service.query(introspection_q...
                               ^~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/cli/commands/codebase.py:215: error: Item "None" of
"CodebaseRAGIntegration | None" has no attribute "query"  [union-attr]
                result = await rag_integration.query(rag_query_obj)
                               ^~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/cli/commands/codebase.py:235: error: Item "None" of
"CodebaseIntrospectionService | None" has no attribute "get_codebase_overview" 
[union-attr]
                overview = await introspection_service.get_codebase_overvi...
                                 ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/cli/commands/codebase.py:257: error: Item "None" of
"CodebaseIntrospectionService | None" has no attribute "compare_codebases" 
[union-attr]
                comparison = await introspection_service.compare_codebases...
                                   ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/cli/commands/codebase.py:289: error: Item "None" of
"CodebaseIntrospectionService | None" has no attribute "add_external_codebase" 
[union-attr]
                result = await introspection_service.add_external_codebase...
                               ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/cli/commands/codebase.py:316: error: Item "None" of
"CodebaseIntrospectionService | None" has no attribute "initialize" 
[union-attr]
            await introspection_service.initialize()
                  ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/cli/commands/codebase.py:318: error: Item "None" of
"CodebaseIntrospectionService | None" has no attribute
"list_available_codebases"  [union-attr]
            codebases = introspection_service.list_available_codebases()
                        ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/cli/commands/codebase.py:361: error: Item "None" of
"CodebaseIntrospectionService | None" has no attribute "initialize" 
[union-attr]
            await introspection_service.initialize()
                  ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/cli/commands/codebase.py:363: error: Item "None" of
"CodebaseIntrospectionService | None" has no attribute "collection" 
[union-attr]
            token_tracker = introspection_service.collection.token_tracker
                            ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/cli/commands/codebase.py:456: error: Item "None" of
"CodebaseIntrospectionService | None" has no attribute "initialize" 
[union-attr]
            await introspection_service.initialize()
                  ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/cli/commands/codebase.py:458: error: Item "None" of
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
