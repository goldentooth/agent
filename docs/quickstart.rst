Quick Start Guide
=================

This guide will help you get started with Goldentooth Agent in 5 minutes.

Prerequisites
-------------

* Python 3.13 or higher
* Poetry (for dependency management)
* Git

Installation
------------

1. Clone the Repository
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git clone https://github.com/yourusername/goldentooth-agent.git
   cd goldentooth-agent

2. Install Dependencies
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install all dependencies
   poetry install
   
   # Activate the virtual environment
   poetry shell

3. Verify Installation
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run tests to verify everything works
   poetry run pytest
   
   # Check type safety
   poetry run mypy src/

Basic Usage
-----------

Using the Flow Engine
~~~~~~~~~~~~~~~~~~~~~

The Flow Engine is the core of Goldentooth Agent. Here's a simple example:

.. code-block:: python

   import asyncio
   from flowengine import Flow
   from flowengine.combinators import map_stream, filter_stream, batch_stream
   
   async def main():
       # Create a flow from data
       numbers = Flow.from_iterable(range(1, 11))
       
       # Transform the data
       result = await numbers.pipe(
           map_stream(lambda x: x * 2),      # Double each number
           filter_stream(lambda x: x > 10),   # Keep only > 10
           batch_stream(size=3)               # Group into batches of 3
       ).to_list()
       
       print(result)  # [[12, 14, 16], [18, 20]]
   
   asyncio.run(main())

Error Handling Example
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flowengine import Flow
   from flowengine.combinators import (
       map_stream, recover_stream, catch_and_continue_stream
   )
   
   async def process_with_errors():
       data = Flow.from_iterable([1, 2, 0, 4, 5])
       
       # Handle division by zero gracefully
       result = await data.pipe(
           map_stream(lambda x: 10 / x),  # This will fail on 0
           catch_and_continue_stream(
               error_handler=lambda e: print(f"Skipping error: {e}")
           )
       ).to_list()
       
       print(result)  # [10.0, 5.0, 2.5, 2.0] (skips the error)

Parallel Processing
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flowengine import Flow
   from flowengine.combinators import parallel_stream
   import aiohttp
   
   async def fetch_data(url: str) -> dict:
       async with aiohttp.ClientSession() as session:
           async with session.get(url) as response:
               return await response.json()
   
   async def process_urls():
       urls = [
           "https://api.example.com/data/1",
           "https://api.example.com/data/2",
           "https://api.example.com/data/3",
       ]
       
       # Fetch all URLs in parallel
       results = await Flow.from_iterable(urls).pipe(
           parallel_stream(
               max_concurrency=3,
               ordered=True  # Maintain order
           )
       ).map(fetch_data).to_list()
       
       return results

Development Workflow
--------------------

Running Tests
~~~~~~~~~~~~~

.. code-block:: bash

   # Run all tests
   poetry run pytest
   
   # Run with coverage
   poetry run pytest --cov
   
   # Run specific test file
   poetry run pytest tests/flowengine/test_flow.py
   
   # Run tests in parallel
   poetry run pytest -n auto

Code Quality Checks
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Type checking
   poetry run mypy src/
   
   # Linting
   poetry run ruff check src/
   
   # Format code
   poetry run black src/ tests/
   poetry run isort src/ tests/
   
   # Run all pre-commit hooks
   poetry run pre-commit run --all-files

Common Patterns
---------------

Stream Processing Pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flowengine import Flow
   from flowengine.combinators import *
   
   async def data_pipeline(input_file: str):
       """Common data processing pipeline pattern."""
       
       return await (
           Flow.from_iterable(read_file_lines(input_file))
           .pipe(
               # Parse and validate
               map_stream(parse_json_line),
               filter_stream(is_valid_record),
               
               # Enrich data
               map_stream(enrich_with_metadata),
               
               # Process in batches
               batch_stream(size=100),
               map_stream(process_batch),
               
               # Flatten results
               flat_map_stream(lambda batch: batch),
               
               # Collect results
               collect_stream()
           )
       )

Time-Based Processing
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flowengine import Flow
   from flowengine.combinators import (
       throttle_stream, debounce_stream, timeout_stream
   )
   
   async def handle_events(event_source):
       """Handle events with time-based controls."""
       
       return await (
           Flow.from_emitter(event_source)
           .pipe(
               # Debounce rapid events
               debounce_stream(seconds=0.5),
               
               # Rate limit processing
               throttle_stream(rate_per_second=10),
               
               # Add timeout protection
               timeout_stream(seconds=30),
               
               # Process events
               map_stream(process_event)
           )
           .for_each(handle_result)
       )

Monitoring and Debugging
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flowengine import Flow
   from flowengine.combinators import (
       log_stream, inspect_stream, metrics_stream
   )
   
   async def monitored_pipeline(data):
       """Pipeline with comprehensive monitoring."""
       
       return await (
           Flow.from_iterable(data)
           .pipe(
               # Log input data
               log_stream(
                   logger=app_logger,
                   message_fn=lambda x: f"Processing: {x}"
               ),
               
               # Transform data
               map_stream(transform_data),
               
               # Inspect intermediate state
               inspect_stream(
                   on_next=lambda x: debug_logger.info(f"Transformed: {x}"),
                   on_error=lambda e: error_logger.error(f"Failed: {e}")
               ),
               
               # Track metrics
               metrics_stream(
                   counter=metrics.increment_counter
               ),
               
               # Final processing
               filter_stream(is_valid_output)
           )
           .to_list()
       )

Next Steps
----------

1. **Explore the Flow Engine Guide**: :doc:`flowengine-guide`
2. **Read the Development Guide**: :doc:`development`
3. **Check Migration Status**: :doc:`migration-status`
4. **Browse API Documentation**: :doc:`api/modules`

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Import Errors**

If you get import errors, ensure you're in the poetry shell:

.. code-block:: bash

   poetry shell

**Type Checking Errors**

The project uses strict type checking. Fix any type errors before committing:

.. code-block:: bash

   poetry run mypy src/ --strict

**Test Failures**

Run tests with verbose output to debug:

.. code-block:: bash

   poetry run pytest -vv

Getting Help
~~~~~~~~~~~~

* Check the :doc:`overview` for architecture details
* Review the :doc:`flowengine-guide` for detailed examples
* See the :doc:`development` guide for contribution guidelines