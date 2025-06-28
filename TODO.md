# TODO

1. Create a command to enter into each `core/` submodule and write a detailed summary of the code therein, including philosophical background, CS theory, interoperation with other libraries, use cases, notes on test coverage, and anything else needed to fully document the module.
2. Set up Sphinx to generate documentation and integrate it where appropriate into pre-commit hooks, etc.
3. Add GitHub Actions workflows to run tests in CI/CD.
4. Create appropriate tools and other mechanisms to ease issue CRUD operations from within the Goldentooth Agent so that e.g. the Agent can create, search, and review existing tickets and act on them as needed.
5. Create appropriate tools and other mechanisms to ease searching the codebase, running tests, and performing other tasks needed to effectively query the current codebase along multiple axes.
6. Create appropriate tools and other mechanisms to create and update statics about test coverage, etc in such a way that we're not hardcoding them into the README.md.
7. Create a suite of QA tools that can remedy (without consuming LLM tokens) as much as possible of the most common issues we encounter, e.g. determining the number of, severity of, and extent of current type-checking issues, etc.
8. Consider refactoring large files into smaller ones where possible to improve code locality.
9. Create a tool that will review the submodule-level README.md files and combine/re-summarize them after meaningful changes.
10. Create commands to accurately construct directory tree representations in markdown for injection into root- and submodule-level README.md files.
11. Devise a detailed plan to incorporate the successful and effective patterns from the smolcode project.
12. Incorporate some method of checking dependencies automatically for upstream security alerts.
13. Write a command or GHA workflow to bump the version in the pyproject.toml file.
14. Move to recharacterize this project; remember that it's not a general-purpose agent framework, it's a lulzy toy for playing with my cluster.
15. Create a command to retrieve the content of a given core module, grab its README.md file, grab its tests if specified, and use it as contextual information for a question to the agent.
16. Establish reasonable defaults for CLI commands without subcommands.
17. Ensure that tracing support is integrated and that we can step through a complicated pipeline to debug it, with the output being both machine-readable and human-readable.
18. Can the Agent interact with Claude Code? It would be useful to be able to run certain queries through the Claude Code API (or using my plan, or whatever) and other queries through the metered API key I have.
19. Add functionality to support querying the various other GitHub organizations and repositories I have available, so I can say to investigate some given GitHub project and devise a plan for updating/expanding/improving it, etc.
