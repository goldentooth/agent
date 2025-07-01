# TODO

1. Add GitHub Actions workflows to run tests in CI/CD.
2. Create appropriate tools and other mechanisms to ease GitHub issue CRUD operations from within the Goldentooth Agent so that e.g. the Agent can create, search, and review existing tickets and act on them as needed.
3. Create appropriate tools and other mechanisms to ease searching the codebase, running tests, and performing other tasks needed to effectively query the current codebase along multiple axes.
4. Create appropriate tools and other mechanisms to create and update statics about test coverage, etc in such a way that we're not hardcoding them into the README.md. This should likely be a part of the module-level and repo-level README.meta.yaml files and the `goldentooth-agent dev` command/subcommands.
5. Create a suite of QA tools that can remedy (without consuming LLM tokens) as much as possible of the most common issues we encounter, e.g. determining the number of, severity of, and extent of current type-checking issues, etc.
6. Consider refactoring large files into smaller ones where possible to improve code locality.
7. Create a tool that will review the submodule-level README.meta.yaml and README.md files and combine/re-summarize them after meaningful changes. The README file should be reviewed for potential updates whenever a file in the module is changed.
8.  Create commands to accurately construct directory tree representations in markdown for injection into root- and submodule-level README.md files. Probably just `tree`, maybe something fancier. This should be in the `README.meta.yaml` files too.
9.  Devise a detailed plan to incorporate the successful and effective patterns from the smolcode project geared at giving the Goldentooth Agent the ability to code itself when desirable.
10. Incorporate some method of checking dependencies automatically and manually for upstream security alerts, e.g. `goldentooth-agent dev audit security` or using Dependabot.
11. Write a command or GHA workflow to bump the version in the pyproject.toml file, e.g. `goldentooth-agent dev bump-version` or use the bump-version GitHub Action if it supports pyproject.toml (probably does).
12. Move to recharacterize this project; remember that it's not a general-purpose agent framework, it's a lulzy toy for playing with my cluster.
13. Create a command to retrieve the content of a given core module, grab its README.md file, grab its tests if specified, and use it as contextual information for a question to the agent, e.g. `goldentooth-agent dev chat --path <path>`.
14. Establish reasonable defaults for CLI commands without subcommands so that we don't get unhelpful error messages.
15. Ensure that tracing support is integrated and that we can step through a complicated pipeline to debug it, with the output being both machine-readable and human-readable.
16. Can the Agent interact with Claude Code? It would be useful to be able to run certain queries through the Claude Code API (or using my plan, or whatever) and other queries through the metered API key I have. This doesn't appear to be the case with embeddings, but perhaps elsewhere.
17. Investigate GitHub MCP and other methods of maintaining a developing and ongoing relationship with GitHub and my repositories.
18. Add functionality to support querying the various other GitHub organizations and repositories I have available, so I can say to investigate some given GitHub project and devise a plan for updating/expanding/improving it, etc.
19. Start thinking about integrating Goldentooth Agent with the Terraform repository (https://github.com/goldentooth/terraform/, ~/Projects/goldentooth/terraform) specifically. We want to be able to maintain a human-readable and machine-readable graph of the infrastructure in that repository and use that to update the README, etc.
20. Start thinking about integrating Goldentooth Agent with the Ansible repository (https://github.com/goldentooth/ansible/, ~/Projects/goldentooth/ansible) specifically. We can use this to figure out ways of describing the infrastructure, service catalog, inventory, etc and summarize that in READMEs, etc.
21. Start thinking about integrating Goldentooth Agent with the Clog (https://github.com/goldentooth/clog/, https://clog.goldentooth.net/, ~/Projects/goldentooth/clog). We can use that to get a good picture of the journey thusfar, formulate longer-term strategies for the cluster, document things as we go, and so forth, e.g. `goldentooth-agent dev clog...`. Its markdown content should be injected into the RAG.
22. Can we integrate asciinema or something similar to easily create screen recordings of command execution? e.g. `goldentooth-agent <command> --record=ascii` or `goldentooth-agent record <command>`?
23. Write a script to run as part of pre-commit hooks to enforce the README.md file maintenance within modules, e.g. `goldentooth dev module readme update <path>`.
24. I dislike this error: TypeVar "Input" appears only once in generic function signature; Use "object" insteadPylancereportInvalidTypeVarUse. Can we ignore it permanently?
25. Create a script or command to list functions and classes with missing/low test coverage, e.g. `goldentooth-agent dev module coverage`.
26. Maintain a README.meta.yaml in each and every module/submodule directory that collects useful information about a given module and that can be updated entirely by executing a script (i.e. without consuming unnecessary extra tokens), e.g. `goldentooth-agent dev module meta check <path>`. This should be used to determine that the README.md file in that module is outdated, e.g. `goldentooth-agent dev module readme check <path>`.
27. Create a command that will retrieve the .py files in the codebase that have been touched least recently within the codebase and perform a deep audit of them, evaluating whether they should be refactored or otherwise improved, etc. After the file has been updated, a comment should be added to the foot of the document mentioning the date and indicating that the file was touched on that date. The command might be `goldentooth-agent dev audit stale-files` or something.
28. Can Sphinx be integrated as a RAG source?
29. Can pre-commit pass along an argument to fail on the first error to allow Claude Code to focus a bit more easily on the errors?
30. Refactor `dev module` commands to make them more stylistically consistent with one another. For example, let's try to avoid long hyphenated subcommand names like `check-freshness-for-commit` and instead consider making that an option switch of another command, e.g. `check-freshness`. In general, let's try to avoid having hyphenated subcommands and prefer just having subcommands. We might also consider reverse-DNS-style or namespaced dotted subcommands, e.g. `goldentooth-agent dev module readme.update --all` or `goldentooth-agent dev module.readme.update --all`.
31. Add guidelines on how CLI commands should be structured for consistency.
32. Add module README.md files to RAG knowledge base.
33. Can we establish a policy of dividing the command implementation (which is mostly e.g. Typer configuration and
  parameter annotations) from the actual invocation of the commands (which should be just mapping those parameters to
  existing library code)? We should add this to guidelines too.
34. Add a link to the GitHub Pages site (https://goldentooth.github.io/agent/) in the README.
35. Let's try to prevent functions from exceeding about ten lines (or, more accurately, statements) in length. If a function exceeds that, we should complain about it.
36. Let's replace any use of `inject.me()` with `world[<Type>]`, e.g. `world[SomeServiceClass]`. The former seems to trigger Pylance/Pyright's `reportCallInDefaultInitializer` lint. This should be considered a guideline for future development.
37. Think the BG generation is shitting itself. Or did we disable that?
