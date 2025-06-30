# GitHub Integration Workflow

This document demonstrates the complete workflow for retrieving GitHub data and integrating it with the Goldentooth Agent RAG system.

## 🚀 **Complete Workflow Demonstration**

### **Prerequisites**

1. **GitHub Token**: Set up a GitHub personal access token
   ```bash
   export GITHUB_TOKEN="your_github_token_here"
   ```

2. **Anthropic API Key**: For RAG question answering (optional for basic operations)
   ```bash
   export ANTHROPIC_API_KEY="your_anthropic_key_here"
   ```

3. **Install the Package**:
   ```bash
   poetry install
   ```

### **Step 1: Initialize the System**

Start with sample data to see the system in action:

```bash
# Initialize with sample GitHub data and embeddings
poetry run goldentooth-agent setup init

# Check system status
poetry run goldentooth-agent setup status
```

**Result**: System is initialized with 5 sample documents (1 org, 3 repos, 1 note) and 5 embeddings.

### **Step 2: Explore Sample Data**

```bash
# View document statistics
poetry run goldentooth-agent docs stats

# List all documents
poetry run goldentooth-agent docs list

# List specific document types
poetry run goldentooth-agent docs list --type github.repos

# Show specific document details
poetry run goldentooth-agent docs show github.repos goldentooth_agent
```

### **Step 3: Test Semantic Search**

```bash
# Search for documents related to repositories
poetry run goldentooth-agent docs search "repositories"

# Search for monitoring systems
poetry run goldentooth-agent docs search "monitoring alerting"

# Search for Python projects
poetry run goldentooth-agent docs search "Python machine learning"
```

### **Step 4: RAG Question Answering** (Requires ANTHROPIC_API_KEY)

```bash
# Ask questions about the repositories
poetry run goldentooth-agent docs ask "What repositories are available?"

# Get insights about specific documents
poetry run goldentooth-agent docs insights github.repos goldentooth_pulse

# Generate knowledge base summary
poetry run goldentooth-agent docs summarize
```

## 🔄 **Syncing Real GitHub Data**

### **Sync Your Organizations**

```bash
# List your GitHub organizations
poetry run goldentooth-agent github list-orgs

# Sync a specific organization (with repositories)
poetry run goldentooth-agent github sync-org your-org-name

# Sync without embedding (faster)
poetry run goldentooth-agent github sync-org your-org-name --no-embed

# Check GitHub API rate limits
poetry run goldentooth-agent github rate-limit
```

### **Sync User Repositories**

```bash
# Sync your own repositories
poetry run goldentooth-agent github sync-user

# Sync another user's public repositories
poetry run goldentooth-agent github sync-user --user username

# Limit the number of repositories
poetry run goldentooth-agent github sync-user --max 10
```

### **Check Sync Status**

```bash
# View GitHub data status
poetry run goldentooth-agent github status

# View overall system status
poetry run goldentooth-agent setup status
```

## 📊 **Data Organization**

The system organizes data in the following structure:

```
~/Library/Application Support/goldentooth-agent/
├── github/
│   ├── orgs/
│   │   └── goldentooth.yaml
│   └── repos/
│       ├── goldentooth_agent.yaml
│       ├── goldentooth_whispers.yaml
│       └── goldentooth_pulse.yaml
├── goldentooth/
│   ├── nodes/
│   └── services/
├── notes/
│   └── github_integration.yaml
└── embeddings.db
```

## 🔍 **Advanced RAG Queries**

With the ANTHROPIC_API_KEY set, you can perform sophisticated queries:

```bash
# Ask about specific technologies
poetry run goldentooth-agent docs ask "What Rust projects do we have?"

# Get deployment guidance
poetry run goldentooth-agent docs ask "How should I deploy the monitoring system?"

# Compare repositories
poetry run goldentooth-agent docs ask "What's the difference between whispers and pulse?"

# Get setup instructions
poetry run goldentooth-agent docs ask "How do I set up GitHub integration?"
```

## 🛠 **Manual Document Management**

```bash
# Embed all documents (useful after adding new ones)
poetry run goldentooth-agent docs embed

# Embed only specific document types
poetry run goldentooth-agent docs embed --type github.repos

# Force re-embedding of existing documents
poetry run goldentooth-agent docs embed --force

# Show file system paths
poetry run goldentooth-agent docs paths
```

## 🎯 **Use Cases**

### **1. Repository Discovery**
```bash
# Find all Python repositories
poetry run goldentooth-agent docs search "Python" --type github.repos

# Ask about AI/ML projects
poetry run goldentooth-agent docs ask "What AI or machine learning projects do we have?"
```

### **2. Infrastructure Documentation**
```bash
# Search for monitoring tools
poetry run goldentooth-agent docs search "monitoring infrastructure"

# Get deployment insights
poetry run goldentooth-agent docs insights github.repos goldentooth_pulse
```

### **3. Team Onboarding**
```bash
# Generate overview for new team members
poetry run goldentooth-agent docs summarize

# Answer common questions
poetry run goldentooth-agent docs ask "What repositories should I know about?"
```

## 🔧 **Customization**

### **Adding Custom Document Types**

1. Create schema adapters in `src/goldentooth_agent/core/schemas/`
2. Update the `DocumentStore` to include the new type
3. Add CLI commands in `src/goldentooth_agent/cli/commands/`

### **Extending GitHub Integration**

The `GitHubClient` can be extended to:
- Sync specific repository metadata (issues, PRs, releases)
- Include private repositories with appropriate permissions
- Add organization member information
- Sync repository file contents for deeper analysis

## 📈 **Performance Considerations**

- **Rate Limits**: GitHub API has rate limits (5000/hour for authenticated users)
- **Embedding Costs**: Each document embedding uses Anthropic API credits
- **Storage**: Vector embeddings are stored in SQLite database
- **Memory**: Large document sets may require more memory for embedding generation

## 🔐 **Security**

- GitHub tokens should have minimal required permissions
- Store API keys in environment variables, never in code
- Consider using GitHub Apps for organization-wide access
- Regular token rotation is recommended

## 🐛 **Troubleshooting**

### **Common Issues**

1. **"GitHub token is required"**: Set the `GITHUB_TOKEN` environment variable
2. **"Anthropic API key is required"**: Set `ANTHROPIC_API_KEY` for RAG features
3. **Rate limit exceeded**: Wait for reset or use `--no-embed` flag
4. **Empty search results**: Check if documents are embedded with `docs stats`

### **Debug Commands**

```bash
# Check system status
poetry run goldentooth-agent setup status

# View detailed document information
poetry run goldentooth-agent docs show <store_type> <doc_id> --raw

# Check GitHub API status
poetry run goldentooth-agent github rate-limit
```

This integration provides a powerful foundation for building a living, searchable knowledge base of your GitHub ecosystem!
