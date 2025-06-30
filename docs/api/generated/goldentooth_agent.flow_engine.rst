goldentooth\_agent.flow\_engine
===============================

.. automodule:: goldentooth_agent.flow_engine

   
   
   

   
   
   .. rubric:: Functions

   .. autosummary::
   
      add_flow_breakpoint
      analyze_flow
      analyze_flow_composition
      batch_stream
      benchmark_stream
      branch_flows
      buffer_stream
      catch_and_continue_stream
      chain_flows
      chain_stream
      check_system_health
      chunk_stream
      circuit_breaker_stream
      collect_stream
      combine_latest_stream
      compose
      debounce_stream
      debug_session
      debug_stream
      delay_stream
      detect_flow_patterns
      disable_flow_debugging
      distinct_stream
      empty_flow
      enable_flow_debugging
      enable_memory_tracking
      expand_stream
      export_execution_trace
      export_flow_analysis
      export_health_report
      export_performance_metrics
      extend_flow_with_trampoline
      filter_stream
      finalize_stream
      flat_map_ctx_stream
      flat_map_stream
      flatten_stream
      generate_flow_optimizations
      get_config_validator
      get_execution_trace
      get_flow
      get_flow_analyzer
      get_flow_debugger
      get_health_monitor
      get_performance_monitor
      get_performance_summary
      group_by_stream
      guard_stream
      health_check_stream
      identity_stream
      if_then_stream
      initialize_context_integration
      inspect_flow
      inspect_stream
      list_flows
      log_stream
      map_stream
      materialize_stream
      memoize_stream
      merge_flows
      merge_stream
      metrics_stream
      monitored_stream
      pairwise_stream
      parallel_stream
      parallel_stream_successful
      performance_stream
      race_stream
      range_flow
      recover_stream
      register_flow
      register_health_check
      registered_flow
      remove_flow_breakpoint
      repeat_flow
      retry_stream
      run_fold
      sample_stream
      scan_stream
      search_flows
      share_stream
      skip_stream
      start_with_stream
      switch_stream
      take_stream
      tap_stream
      then_stream
      throttle_stream
      timeout_stream
      trace_stream
      traced_flow
      until_stream
      validate_flow_configuration
      while_condition_stream
      window_stream
      zip_stream
   
   

   
   
   .. rubric:: Classes

   .. autosummary::
   
      Flow
      FlowAnalyzer
      FlowConfigValidator
      FlowDebugger
      FlowEdge
      FlowExecutionContext
      FlowGraph
      FlowHealthMonitor
      FlowMetrics
      FlowNode
      FlowRegistry
      HealthCheck
      HealthCheckResult
      HealthStatus
      OnComplete
      OnError
      OnNext
      PerformanceMonitor
      StreamNotification
      SystemHealth
      TrampolineFlowCombinators
   
   

   
   
   .. rubric:: Exceptions

   .. autosummary::
   
      FlowConfigurationError
      FlowError
      FlowExecutionError
      FlowTimeoutError
      FlowValidationError
   
   



.. rubric:: Modules

.. autosummary::
   :toctree:
   :recursive:

   goldentooth_agent.flow_engine.combinators
   goldentooth_agent.flow_engine.core
   goldentooth_agent.flow_engine.extensions
   goldentooth_agent.flow_engine.integrations
   goldentooth_agent.flow_engine.lazy_imports
   goldentooth_agent.flow_engine.observability
   goldentooth_agent.flow_engine.protocols
   goldentooth_agent.flow_engine.registry
   goldentooth_agent.flow_engine.trampoline

