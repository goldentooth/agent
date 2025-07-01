src/goldentooth_agent/core/flow_agent/instructor_integration.py:64: error:
Returning Any from function declared to return "R"  [no-any-return]
                return self.mock_responses[response_model]
                ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/flow_agent/instructor_integration.py:258: error:
Returning Any from function declared to return "FlowIOSchema"  [no-any-return]
                return response
                ^~~~~~~~~~~~~~~
src/goldentooth_agent/core/tools/file_tools.py:185: error: No overload variant
of "open" matches argument types "str", "str"  [call-overload]
                async with aiofiles.open(str(file_path), mode) as f:
                           ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/tools/file_tools.py:185: note: Possible overload variants:
src/goldentooth_agent/core/tools/file_tools.py:185: note:     def open(file: int | str | bytes | PathLike[str] | PathLike[bytes], mode: Literal['r+', '+r', 'rt+', 'r+t', '+rt', 'tr+', 't+r', '+tr', 'w+', '+w', 'wt+', 'w+t', '+wt', 'tw+', 't+w', '+tw', 'a+', '+a', 'at+', 'a+t', '+at', 'ta+', 't+a', '+ta', 'x+', '+x', 'xt+', 'x+t', '+xt', 'tx+', 't+x', '+tx'] | Literal['w', 'wt', 'tw', 'a', 'at', 'ta', 'x', 'xt', 'tx'] | Literal['r', 'rt', 'tr', 'U', 'rU', 'Ur', 'rtU', 'rUt', 'Urt', 'trU', 'tUr', 'Utr'] = ..., buffering: int = ..., encoding: str | None = ..., errors: str | None = ..., newline: str | None = ..., closefd: bool = ..., opener: Callable[[str, int], int] | None = ..., *, loop: AbstractEventLoop | None = ..., executor: Executor | None = ...) -> AiofilesContextManager[AsyncTextIOWrapper]
src/goldentooth_agent/core/tools/file_tools.py:185: note:     def open(file: int | str | bytes | PathLike[str] | PathLike[bytes], mode: Literal['rb+', 'r+b', '+rb', 'br+', 'b+r', '+br', 'wb+', 'w+b', '+wb', 'bw+', 'b+w', '+bw', 'ab+', 'a+b', '+ab', 'ba+', 'b+a', '+ba', 'xb+', 'x+b', '+xb', 'bx+', 'b+x', '+bx'] | Literal['rb', 'br', 'rbU', 'rUb', 'Urb', 'brU', 'bUr', 'Ubr'] | Literal['wb', 'bw', 'ab', 'ba', 'xb', 'bx'], buffering: Literal[0], encoding: None = ..., errors: None = ..., newline: None = ..., closefd: bool = ..., opener: Callable[[str, int], int] | None = ..., *, loop: AbstractEventLoop | None = ..., executor: Executor | None = ...) -> AiofilesContextManager[AsyncFileIO]
src/goldentooth_agent/core/tools/file_tools.py:185: note:     def open(file: int | str | bytes | PathLike[str] | PathLike[bytes], mode: Literal['rb', 'br', 'rbU', 'rUb', 'Urb', 'brU', 'bUr', 'Ubr'] | Literal['rb+', 'r+b', '+rb', 'br+', 'b+r', '+br', 'wb+', 'w+b', '+wb', 'bw+', 'b+w', '+bw', 'ab+', 'a+b', '+ab', 'ba+', 'b+a', '+ba', 'xb+', 'x+b', '+xb', 'bx+', 'b+x', '+bx'], buffering: Literal[-1, 1] = ..., encoding: None = ..., errors: None = ..., newline: None = ..., closefd: bool = ..., opener: Callable[[str, int], int] | None = ..., *, loop: AbstractEventLoop | None = ..., executor: Executor | None = ...) -> AiofilesContextManager[AsyncBufferedReader]
src/goldentooth_agent/core/tools/file_tools.py:185: note:     def open(file: int | str | bytes | PathLike[str] | PathLike[bytes], mode: Literal['wb', 'bw', 'ab', 'ba', 'xb', 'bx'], buffering: Literal[-1, 1] = ..., encoding: None = ..., errors: None = ..., newline: None = ..., closefd: bool = ..., opener: Callable[[str, int], int] | None = ..., *, loop: AbstractEventLoop | None = ..., executor: Executor | None = ...) -> AiofilesContextManager[AsyncBufferedIOBase]
src/goldentooth_agent/core/tools/file_tools.py:185: note:     def open(file: int | str | bytes | PathLike[str] | PathLike[bytes], mode: Literal['rb+', 'r+b', '+rb', 'br+', 'b+r', '+br', 'wb+', 'w+b', '+wb', 'bw+', 'b+w', '+bw', 'ab+', 'a+b', '+ab', 'ba+', 'b+a', '+ba', 'xb+', 'x+b', '+xb', 'bx+', 'b+x', '+bx'] | Literal['rb', 'br', 'rbU', 'rUb', 'Urb', 'brU', 'bUr', 'Ubr'] | Literal['wb', 'bw', 'ab', 'ba', 'xb', 'bx'], buffering: int = ..., encoding: None = ..., errors: None = ..., newline: None = ..., closefd: bool = ..., opener: Callable[[str, int], int] | None = ..., *, loop: AbstractEventLoop | None = ..., executor: Executor | None = ...) -> AiofilesContextManager[_UnknownAsyncBinaryIO]
src/goldentooth_agent/core/tools/file_tools.py:189: error: No overload variant
of "open" matches argument types "str", "str", "str"  [call-overload]
                async with aiofiles.open(
                           ^
src/goldentooth_agent/core/tools/file_tools.py:189: note: Possible overload variants:
src/goldentooth_agent/core/tools/file_tools.py:189: note:     def open(file: int | str | bytes | PathLike[str] | PathLike[bytes], mode: Literal['r+', '+r', 'rt+', 'r+t', '+rt', 'tr+', 't+r', '+tr', 'w+', '+w', 'wt+', 'w+t', '+wt', 'tw+', 't+w', '+tw', 'a+', '+a', 'at+', 'a+t', '+at', 'ta+', 't+a', '+ta', 'x+', '+x', 'xt+', 'x+t', '+xt', 'tx+', 't+x', '+tx'] | Literal['w', 'wt', 'tw', 'a', 'at', 'ta', 'x', 'xt', 'tx'] | Literal['r', 'rt', 'tr', 'U', 'rU', 'Ur', 'rtU', 'rUt', 'Urt', 'trU', 'tUr', 'Utr'] = ..., buffering: int = ..., encoding: str | None = ..., errors: str | None = ..., newline: str | None = ..., closefd: bool = ..., opener: Callable[[str, int], int] | None = ..., *, loop: AbstractEventLoop | None = ..., executor: Executor | None = ...) -> AiofilesContextManager[AsyncTextIOWrapper]
src/goldentooth_agent/core/tools/file_tools.py:189: note:     def open(file: int | str | bytes | PathLike[str] | PathLike[bytes], mode: Literal['rb+', 'r+b', '+rb', 'br+', 'b+r', '+br', 'wb+', 'w+b', '+wb', 'bw+', 'b+w', '+bw', 'ab+', 'a+b', '+ab', 'ba+', 'b+a', '+ba', 'xb+', 'x+b', '+xb', 'bx+', 'b+x', '+bx'] | Literal['rb', 'br', 'rbU', 'rUb', 'Urb', 'brU', 'bUr', 'Ubr'] | Literal['wb', 'bw', 'ab', 'ba', 'xb', 'bx'], buffering: Literal[0], encoding: None = ..., errors: None = ..., newline: None = ..., closefd: bool = ..., opener: Callable[[str, int], int] | None = ..., *, loop: AbstractEventLoop | None = ..., executor: Executor | None = ...) -> AiofilesContextManager[AsyncFileIO]
src/goldentooth_agent/core/tools/file_tools.py:189: note:     def open(file: int | str | bytes | PathLike[str] | PathLike[bytes], mode: Literal['rb', 'br', 'rbU', 'rUb', 'Urb', 'brU', 'bUr', 'Ubr'] | Literal['rb+', 'r+b', '+rb', 'br+', 'b+r', '+br', 'wb+', 'w+b', '+wb', 'bw+', 'b+w', '+bw', 'ab+', 'a+b', '+ab', 'ba+', 'b+a', '+ba', 'xb+', 'x+b', '+xb', 'bx+', 'b+x', '+bx'], buffering: Literal[-1, 1] = ..., encoding: None = ..., errors: None = ..., newline: None = ..., closefd: bool = ..., opener: Callable[[str, int], int] | None = ..., *, loop: AbstractEventLoop | None = ..., executor: Executor | None = ...) -> AiofilesContextManager[AsyncBufferedReader]
src/goldentooth_agent/core/tools/file_tools.py:189: note:     def open(file: int | str | bytes | PathLike[str] | PathLike[bytes], mode: Literal['wb', 'bw', 'ab', 'ba', 'xb', 'bx'], buffering: Literal[-1, 1] = ..., encoding: None = ..., errors: None = ..., newline: None = ..., closefd: bool = ..., opener: Callable[[str, int], int] | None = ..., *, loop: AbstractEventLoop | None = ..., executor: Executor | None = ...) -> AiofilesContextManager[AsyncBufferedIOBase]
src/goldentooth_agent/core/tools/file_tools.py:189: note:     def open(file: int | str | bytes | PathLike[str] | PathLike[bytes], mode: Literal['rb+', 'r+b', '+rb', 'br+', 'b+r', '+br', 'wb+', 'w+b', '+wb', 'bw+', 'b+w', '+bw', 'ab+', 'a+b', '+ab', 'ba+', 'b+a', '+ba', 'xb+', 'x+b', '+xb', 'bx+', 'b+x', '+bx'] | Literal['rb', 'br', 'rbU', 'rUb', 'Urb', 'brU', 'bUr', 'Ubr'] | Literal['wb', 'bw', 'ab', 'ba', 'xb', 'bx'], buffering: int = ..., encoding: None = ..., errors: None = ..., newline: None = ..., closefd: bool = ..., opener: Callable[[str, int], int] | None = ..., *, loop: AbstractEventLoop | None = ..., executor: Executor | None = ...) -> AiofilesContextManager[_UnknownAsyncBinaryIO]
src/goldentooth_agent/core/security/input_validation.py:475: error: Returning
Any from function declared to return "dict[str, Any]"  [no-any-return]
        return validated_data
        ^~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/security/input_validation.py:510: error: Returning
Any from function declared to return "str"  [no-any-return]
        return sanitizer.sanitize_string(value)
        ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/tools/performance.py:144: error: Incompatible types
in assignment (expression has type "float", target has type "int")  [assignment]
                stats["hits"] / stats["requests"] if stats["requests"] > 0...
                ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~...
src/goldentooth_agent/core/tools/web_tools.py:361: error: Argument
"implementation" to "FlowTool" has incompatible type
"Callable[[WebScrapeInput], Coroutine[Any, Any, WebScrapeOutput]]"; expected
"Callable[[WebScrapeInput], WebScrapeOutput] | Callable[[WebScrapeInput], Future[WebScrapeOutput]]"
 [arg-type]
        implementation=web_scrape_implementation,
                       ^~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/tools/web_tools.py:369: error: Argument
"implementation" to "FlowTool" has incompatible type
"Callable[[JsonApiInput], Coroutine[Any, Any, JsonApiOutput]]"; expected
"Callable[[JsonApiInput], JsonApiOutput] | Callable[[JsonApiInput], Future[JsonApiOutput]]"
 [arg-type]
        implementation=json_api_implementation,
                       ^~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/embeddings_service.py:74: error: Item
"ToolUseBlock" of
"TextBlock | ToolUseBlock | ServerToolUseBlock | WebSearchToolResultBlock | ThinkingBlock | RedactedThinkingBlock"
has no attribute "text"  [union-attr]
                semantic_features = semantic_response.content[0].text
                                    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/embeddings_service.py:74: error: Item
"ServerToolUseBlock" of
"TextBlock | ToolUseBlock | ServerToolUseBlock | WebSearchToolResultBlock | ThinkingBlock | RedactedThinkingBlock"
has no attribute "text"  [union-attr]
                semantic_features = semantic_response.content[0].text
                                    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/embeddings_service.py:74: error: Item
"WebSearchToolResultBlock" of
"TextBlock | ToolUseBlock | ServerToolUseBlock | WebSearchToolResultBlock | ThinkingBlock | RedactedThinkingBlock"
has no attribute "text"  [union-attr]
                semantic_features = semantic_response.content[0].text
                                    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/embeddings_service.py:74: error: Item
"ThinkingBlock" of
"TextBlock | ToolUseBlock | ServerToolUseBlock | WebSearchToolResultBlock | ThinkingBlock | RedactedThinkingBlock"
has no attribute "text"  [union-attr]
                semantic_features = semantic_response.content[0].text
                                    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/embeddings_service.py:74: error: Item
"RedactedThinkingBlock" of
"TextBlock | ToolUseBlock | ServerToolUseBlock | WebSearchToolResultBlock | ThinkingBlock | RedactedThinkingBlock"
has no attribute "text"  [union-attr]
                semantic_features = semantic_response.content[0].text
                                    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/embeddings_service.py:80: error:
Returning Any from function declared to return "list[float]"  [no-any-return]
                return feature_vector.tolist()
                ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:131: error: Incompatible
default for argument "store_type" (default has type "None", argument has type
"str")  [assignment]
            store_type: str = None,
                              ^~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:131: note: PEP 484 prohibits implicit Optional. Accordingly, mypy has changed its default to no_implicit_optional=True
src/goldentooth_agent/core/embeddings/hybrid_search.py:131: note: Use https://github.com/hauntsaninja/no_implicit_optional to automatically upgrade your codebase
src/goldentooth_agent/core/embeddings/hybrid_search.py:133: error: Incompatible
default for argument "semantic_weight" (default has type "None", argument has
type "float")  [assignment]
            semantic_weight: float = None,
                                     ^~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:133: note: PEP 484 prohibits implicit Optional. Accordingly, mypy has changed its default to no_implicit_optional=True
src/goldentooth_agent/core/embeddings/hybrid_search.py:133: note: Use https://github.com/hauntsaninja/no_implicit_optional to automatically upgrade your codebase
src/goldentooth_agent/core/embeddings/hybrid_search.py:134: error: Incompatible
default for argument "keyword_weight" (default has type "None", argument has
type "float")  [assignment]
            keyword_weight: float = None,
                                    ^~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:134: note: PEP 484 prohibits implicit Optional. Accordingly, mypy has changed its default to no_implicit_optional=True
src/goldentooth_agent/core/embeddings/hybrid_search.py:134: note: Use https://github.com/hauntsaninja/no_implicit_optional to automatically upgrade your codebase
src/goldentooth_agent/core/embeddings/hybrid_search.py:159: error: Statement is
unreachable  [unreachable]
                semantic_weight = self.semantic_weight
                ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:161: error: Statement is
unreachable  [unreachable]
                keyword_weight = self.keyword_weight
                ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:250: error: Statement is
unreachable  [unreachable]
                bm25_scores = self._calculate_bm25_scores(query)
                ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:353: error: Returning
Any from function declared to return "str"  [no-any-return]
                return result["chunk_id"]
                ^~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:422: error: Incompatible
types in assignment (expression has type "dict[Never, Never]", variable has type
"None")  [assignment]
                self._document_corpus = {}
                                        ^~
src/goldentooth_agent/core/embeddings/hybrid_search.py:430: error: Unsupported
target for indexed assignment ("None")  [index]
                    self._document_corpus[doc_id] = doc
                    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:440: error: Incompatible
types in assignment (expression has type "dict[Never, Never]", variable has type
"None")  [assignment]
                self._document_corpus = {}
                                        ^~
src/goldentooth_agent/core/embeddings/hybrid_search.py:454: error: Incompatible
types in assignment (expression has type "list[int]", variable has type "None") 
[assignment]
            self._document_lengths = [len(tokens) for tokens in tokenized_...
                                     ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~...
src/goldentooth_agent/core/embeddings/hybrid_search.py:455: error: No overload
variant of "sum" matches argument type "None"  [call-overload]
            avg_doc_length = sum(self._document_lengths) / len(self._docum...
                             ^~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:455: note: Possible overload variants:
src/goldentooth_agent/core/embeddings/hybrid_search.py:455: note:     def sum(Iterable[bool], /, start: int = ...) -> int
src/goldentooth_agent/core/embeddings/hybrid_search.py:455: note:     def [_SupportsSumNoDefaultT: _SupportsSumWithNoDefaultGiven] sum(Iterable[_SupportsSumNoDefaultT], /) -> _SupportsSumNoDefaultT | Literal[0]
src/goldentooth_agent/core/embeddings/hybrid_search.py:455: note:     def [_AddableT1: SupportsAdd[Any, Any], _AddableT2: SupportsAdd[Any, Any]] sum(Iterable[_AddableT1], /, start: _AddableT2) -> _AddableT1 | _AddableT2
src/goldentooth_agent/core/embeddings/hybrid_search.py:455: error: Argument 1
to "len" has incompatible type "None"; expected "Sized"  [arg-type]
    ...g_doc_length = sum(self._document_lengths) / len(self._document_length...
                                                        ^~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:458: error: Incompatible
types in assignment (expression has type "list[Never]", variable has type
"None")  [assignment]
            self._term_frequencies = []
                                     ^~
src/goldentooth_agent/core/embeddings/hybrid_search.py:459: error: Need type
annotation for "document_frequencies"  [var-annotated]
            document_frequencies = defaultdict(int)
            ^~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:463: error: "None" has
no attribute "append"  [attr-defined]
                self._term_frequencies.append(term_freq)
                ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:471: error: Incompatible
types in assignment (expression has type "dict[str, Any]", variable has type
"None")  [assignment]
            self._corpus_stats = {
                                 ^
src/goldentooth_agent/core/embeddings/hybrid_search.py:480: error: Right
operand of "or" is never evaluated  [unreachable]
                not self._corpus_stats
                ^
src/goldentooth_agent/core/embeddings/hybrid_search.py:486: error: Statement is
unreachable  [unreachable]
            query_terms = self._tokenize(query.lower())
            ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:508: error: Argument 1
to "len" has incompatible type "None"; expected "Sized"  [arg-type]
            if doc_index >= len(self._term_frequencies) or doc_index >= le...
                                ^~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:509: error: Argument 1
to "len" has incompatible type "None"; expected "Sized"  [arg-type]
                self._document_lengths
                ^~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:513: error: Value of
type "None" is not indexable  [index]
            term_freq = self._term_frequencies[doc_index]
                        ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:514: error: Value of
type "None" is not indexable  [index]
            doc_length = self._document_lengths[doc_index]
                         ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:515: error: Value of
type "None" is not indexable  [index]
            avg_doc_length = self._corpus_stats["average_document_length"]
                             ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:516: error: Value of
type "None" is not indexable  [index]
            total_docs = self._corpus_stats["total_documents"]
                         ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:517: error: Value of
type "None" is not indexable  [index]
            doc_frequencies = self._corpus_stats["document_frequencies"]
                              ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:576: error: Statement is
unreachable  [unreachable]
            return {
            ^
src/goldentooth_agent/core/embeddings/hybrid_search.py:608: error: Incompatible
default for argument "k1" (default has type "None", argument has type "float") 
[assignment]
        def update_bm25_parameters(self, k1: float = None, b: float = None...
                                                     ^~~~
src/goldentooth_agent/core/embeddings/hybrid_search.py:608: note: PEP 484 prohibits implicit Optional. Accordingly, mypy has changed its default to no_implicit_optional=True
src/goldentooth_agent/core/embeddings/hybrid_search.py:608: note: Use https://github.com/hauntsaninja/no_implicit_optional to automatically upgrade your codebase
src/goldentooth_agent/core/embeddings/hybrid_search.py:608: error: Incompatible
default for argument "b" (default has type "None", argument has type "float") 
[assignment]
    ...date_bm25_parameters(self, k1: float = None, b: float = None) -> None:
                                                               ^~~~
src/goldentooth_agent/core/embeddings/chunk_relationships.py:95: error: Missing
type parameters for generic type "ndarray"  [type-arg]
    ...f _calculate_similarity_matrix(self, embeddings: np.ndarray) -> np.nda...
                                                        ^
src/goldentooth_agent/core/embeddings/chunk_relationships.py:104: error:
Returning Any from function declared to return "ndarray[Any, Any]" 
[no-any-return]
            return similarity_matrix
            ^~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/embeddings/chunk_relationships.py:145: error:
Missing type parameters for generic type "ndarray"  [type-arg]
    ...      self, chunks: list[DocumentChunk], similarity_matrix: np.ndarray
                                                                   ^
src/goldentooth_agent/core/embeddings/chunk_relationships.py:232: error:
Missing type parameters for generic type "ndarray"  [type-arg]
    ...      self, chunks: list[DocumentChunk], similarity_matrix: np.ndarray
                                                                   ^
src/goldentooth_agent/core/embeddings/chunk_relationships.py:347: error:
Missing type parameters for generic type "ndarray"  [type-arg]
            similarity_matrix: np.ndarray,
                               ^
src/goldentooth_agent/core/embeddings/chunk_relationships.py:361: error: Need
type annotation for "chunk_connections"  [var-annotated]
            chunk_connections = defaultdict(int)
            ^~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/agent_codebase/collection.py:319: error: Need type
annotation for "current_chunk" (hint: "current_chunk: list[<type>] = ...") 
[var-annotated]
            current_chunk = []
            ^~~~~~~~~~~~~
src/goldentooth_agent/core/agent_codebase/collection.py:350: error: Need type
annotation for "current_chunk" (hint: "current_chunk: list[<type>] = ...") 
[var-annotated]
            current_chunk = []
            ^~~~~~~~~~~~~
src/goldentooth_agent/core/agent_codebase/collection.py:384: error: Need type
annotation for "current_chunk" (hint: "current_chunk: list[<type>] = ...") 
[var-annotated]
            current_chunk = []
            ^~~~~~~~~~~~~
src/goldentooth_agent/core/agent_codebase/collection.py:432: error: Unexpected
keyword argument "query_text" for "search_similar" of "VectorStore"  [call-arg]
            results = self.vector_store.search_similar(
                      ^
src/goldentooth_agent/core/agent_codebase/collection.py:432: error: Unexpected
keyword argument "metadata_filters" for "search_similar" of "VectorStore" 
[call-arg]
            results = self.vector_store.search_similar(
                      ^
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
src/goldentooth_agent/core/rag/rag_service.py:256: error: Need type annotation
for "chunks_by_doc" (hint: "chunks_by_doc: dict[<type>, <type>] = ...") 
[var-annotated]
            chunks_by_doc = {}
            ^~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:465: error: Name "docs" may be
undefined  [possibly-undefined]
                        "documents_analyzed": len(docs) if store_type else...
                                                  ^~~~
src/goldentooth_agent/core/rag/rag_service.py:465: error: Name "total_docs" may
be undefined  [possibly-undefined]
    ...        "documents_analyzed": len(docs) if store_type else total_docs,
                                                                  ^~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:800: error: Incompatible default
for argument "store_type" (default has type "None", argument has type "str") 
[assignment]
            store_type: str = None,
                              ^~~~
src/goldentooth_agent/core/rag/rag_service.py:800: note: PEP 484 prohibits implicit Optional. Accordingly, mypy has changed its default to no_implicit_optional=True
src/goldentooth_agent/core/rag/rag_service.py:800: note: Use https://github.com/hauntsaninja/no_implicit_optional to automatically upgrade your codebase
src/goldentooth_agent/core/rag/rag_service.py:801: error: Incompatible default
for argument "document_id" (default has type "None", argument has type "str") 
[assignment]
            document_id: str = None,
                               ^~~~
src/goldentooth_agent/core/rag/rag_service.py:801: note: PEP 484 prohibits implicit Optional. Accordingly, mypy has changed its default to no_implicit_optional=True
src/goldentooth_agent/core/rag/rag_service.py:801: note: Use https://github.com/hauntsaninja/no_implicit_optional to automatically upgrade your codebase
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
src/goldentooth_agent/core/rag/rag_service.py:1080: error: Incompatible default
for argument "store_type" (default has type "None", argument has type "str") 
[assignment]
        def _get_all_chunks(self, store_type: str = None) -> list[dict[str...
                                                    ^~~~
src/goldentooth_agent/core/rag/rag_service.py:1080: note: PEP 484 prohibits implicit Optional. Accordingly, mypy has changed its default to no_implicit_optional=True
src/goldentooth_agent/core/rag/rag_service.py:1080: note: Use https://github.com/hauntsaninja/no_implicit_optional to automatically upgrade your codebase
src/goldentooth_agent/core/rag/rag_service.py:1097: error: "DocumentStore" has
no attribute "get_store"  [attr-defined]
                documents = self.document_store.get_store(store_type).list...
                            ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:1110: error: "DocumentStore" has
no attribute "get_store"  [attr-defined]
                        store = self.document_store.get_store(store_name)
                                ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:1142: error: Need type annotation
for "relationship_types" (hint:
"relationship_types: dict[<type>, <type>] = ...")  [var-annotated]
                relationship_types = {}
                ^~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:1158: error: Unexpected keyword
argument "chunk_id" for "get_document_chunks" of "VectorStore"  [call-arg]
                chunk_details = self.vector_store.get_document_chunks(
                                ^
src/goldentooth_agent/core/rag/rag_service.py:1223: error: Need type annotation
for "rel_types" (hint: "rel_types: dict[<type>, <type>] = ...")  [var-annotated]
            rel_types = {}
            ^~~~~~~~~
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
src/goldentooth_agent/core/rag/rag_service.py:1689: error: Incompatible default
for argument "semantic_weights" (default has type "None", argument has type
"list[float]")  [assignment]
            semantic_weights: list[float] = None,
                                            ^~~~
src/goldentooth_agent/core/rag/rag_service.py:1689: note: PEP 484 prohibits implicit Optional. Accordingly, mypy has changed its default to no_implicit_optional=True
src/goldentooth_agent/core/rag/rag_service.py:1689: note: Use https://github.com/hauntsaninja/no_implicit_optional to automatically upgrade your codebase
src/goldentooth_agent/core/rag/rag_service.py:1690: error: Incompatible default
for argument "keyword_weights" (default has type "None", argument has type
"list[float]")  [assignment]
            keyword_weights: list[float] = None,
                                           ^~~~
src/goldentooth_agent/core/rag/rag_service.py:1690: note: PEP 484 prohibits implicit Optional. Accordingly, mypy has changed its default to no_implicit_optional=True
src/goldentooth_agent/core/rag/rag_service.py:1690: note: Use https://github.com/hauntsaninja/no_implicit_optional to automatically upgrade your codebase
src/goldentooth_agent/core/rag/rag_service.py:1703: error: Statement is
unreachable  [unreachable]
                semantic_weights = [0.5, 0.6, 0.7, 0.8, 0.9]
                ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
src/goldentooth_agent/core/rag/rag_service.py:1705: error: Statement is
unreachable  [unreachable]
                keyword_weights = [0.1, 0.2, 0.3, 0.4, 0.5]
                ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
