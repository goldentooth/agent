# TODO

1. What sort of features can we add to make the interface really "pop"? What sort of wow factor can we introduce into a CLI? This is not just an agent, it's a flexible programmable conversation system.
2. Add GitHub Actions workflows to run tests in CI/CD.
3. Create appropriate tools and other mechanisms to ease GitHub issue CRUD operations from within the Goldentooth Agent so that e.g. the Agent can create, search, and review existing tickets and act on them as needed.
4. Create appropriate tools and other mechanisms to ease searching the codebase, running tests, and performing other tasks needed to effectively query the current codebase along multiple axes.
5.  Devise a detailed plan to incorporate the successful and effective patterns from the smolcode project geared at giving the Goldentooth Agent the ability to code itself when desirable.
6.  Incorporate some method of checking dependencies automatically and manually for upstream security alerts, e.g. `goldentooth-agent dev audit security` or using Dependabot.
7.  Write a command or GHA workflow to bump the version in the pyproject.toml file, e.g. `goldentooth-agent dev bump-version` or use the bump-version GitHub Action if it supports pyproject.toml (probably does).
8.  Move to recharacterize this project; remember that it's not a general-purpose agent framework, it's a lulzy toy for playing with my cluster.
9.  Create a command to retrieve the content of a given package, grab its README.md file, grab its tests if specified, and use it as contextual information for a question to the agent, e.g. `goldentooth-agent dev chat --path <path>`.
10. Establish reasonable defaults for CLI commands without subcommands so that we don't get unhelpful error messages.
11. Ensure that tracing support is integrated and that we can step through a complicated pipeline to debug it, with the output being both machine-readable and human-readable.
12. Can the Agent interact with Claude Code? It would be useful to be able to run certain queries through the Claude Code API (or using my plan, or whatever) and other queries through the metered API key I have. This doesn't appear to be the case with embeddings, but perhaps elsewhere. I suppose it can do it with `claude -p`...
13. Investigate GitHub MCP and other methods of maintaining a developing and ongoing relationship with GitHub and my repositories.
14. What other public MCPs are there out there?
15. Can I create an MCP for Beets? LOL. Is there one for Plex?
16. Are there MCP interfaces for Loki, Prometheus, etc?
17. Can I easily write and deploy an MCP into Goldentooth? What would that entail? What would be the upfront work, and how much work would each additional endpoint or function involve?
18. I know I can self-host a RAG, e.g. with PostgreSQL or SQLite. I favor the latter for its comparative lack of infrastructure, but I think it will cause issues with performance in the long run, if only because I want to maintain all documentation in a Git repository and rebuild it frequently. Can we have a multi-tiered structure? What can I self-host, and what should I host in the cloud? Should Goldentooth Agent include a sync engine for transferring documents between locations?
19. Add functionality to support querying the various other GitHub organizations and repositories I have available, so I can say to investigate some given GitHub project and devise a plan for updating/expanding/improving it, etc.
20. Start thinking about integrating Goldentooth Agent with the Terraform repository (https://github.com/goldentooth/terraform/, ~/Projects/goldentooth/terraform) specifically. We want to be able to maintain a human-readable and machine-readable graph of the infrastructure in that repository and use that to update the README, etc.
21. Start thinking about integrating Goldentooth Agent with the Ansible repository (https://github.com/goldentooth/ansible/, ~/Projects/goldentooth/ansible) specifically. We can use this to figure out ways of describing the infrastructure, service catalog, inventory, etc and summarize that in READMEs, etc.
22. Start thinking about integrating Goldentooth Agent with the Clog (https://github.com/goldentooth/clog/, https://clog.goldentooth.net/, ~/Projects/goldentooth/clog). We can use that to get a good picture of the journey thusfar, formulate longer-term strategies for the cluster, document things as we go, and so forth, e.g. `goldentooth-agent dev clog...`. Its markdown content should be injected into the RAG.
23. Can we integrate asciinema or something similar to easily create screen recordings of command execution? e.g. `goldentooth-agent <command> --record=ascii` or `goldentooth-agent record <command>`?
24. Write a script to run as part of pre-commit hooks to enforce the README.md file maintenance within modules, e.g. `goldentooth dev module readme update <path>`.
25. Can Sphinx be integrated as a RAG source?
26. Create a command that will retrieve the .py files in the codebase that have been touched least recently within the codebase and perform a deep audit of them, evaluating whether they should be refactored or otherwise improved, etc. After the file has been updated, a comment should be added to the foot of the document mentioning the date and indicating that the file was touched on that date. The command might be `goldentooth-agent dev audit stale-files` or something.
27. Can the Git history be integrated as a RAG source?
28. Ensure we're adding autocomplete for Typer commands.
29. Ensure that CLI commands are simple proxy functions with no meaningful logic, as they are somewhat complex to test. Can we establish a policy of dividing the command implementation (which is mostly e.g. Typer configuration and parameter annotations) from the actual invocation of the commands (which should be just mapping those parameters to existing library code)? We should add this to guidelines too.
30. Add guidelines on how CLI commands should be structured for consistency, e.g. we want commands to be single words whenever possible and kind of reverse-dns-named or something similar.
31. Add a link to the GitHub Pages site (https://goldentooth.github.io/agent/) in the README.
32. Let's replace any use of `inject.me()` with `world[<Type>]`, e.g. `world[SomeServiceClass]`. The former seems to trigger Pylance/Pyright's `reportCallInDefaultInitializer` lint. This should be considered a guideline for future development. Or maybe not. IDK. `inject.me()` is probably the best functionally, but the type implications are not great.
33. Our RAG agent is not a FlowAgent... why not? Let's tackle the issues that cause this discrepancy so we can unify agent capabilities.
34. What do I need to do to install goldentooth-agent globally?
35. What do I need to do to install goldentooth-agent globally and also have the alias command `gta`?
36. RAG agent: Embedding dimension mismatch: Search operations fail with dimension alignment errors
37. RAG agent: Chat mode EOF loop: RAG agent in interactive chat gets stuck in an error loop
38. Let's remove that code that checks if the embedding length is equal to 0 in 'src/goldentooth_agent/core/embeddings/vector_store.py'. Instead, while we're in "development mode", let's just nuke the DB semi-regularly and rebuild it.
39. Why are RAG imports timing out after two minutes? What can we do to address this?
40. Add a `docs types` command to list the types of documents supported in our RAG implementation.
41. What can we do to interestingly and effectively integrate the flow system with Jupyter, etc?
42. We can add a semi-persistent database with SQLite; this can host local RAG, perhaps some other local stuff that's not critical for long-term preservation. How can we make this absolutely bulletproof, highly observable, and maintainable?
43. Revisit `agent-knowledge-base`. Is this still valuable? What if we get into 100,000-1,000,000 files? Does this just become absurd, and should we abandon it now?
44. Probably split out anything correlating Flow and Context into a subclass or smth.
45. Replace placeholder health check implementations in Epic 18 with proper flow execution monitoring, error tracking, and performance metrics collection. Current implementations are basic placeholders that need real system integration for production use.
46. Symbol should probably throw an exception on successive dots.
