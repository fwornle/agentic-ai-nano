# Agentic AI Nanodegree

**Advanced AI Agent Development & Protocol Integration** - A comprehensive 6-week self-paced program covering modern AI agent development, from foundational patterns through cutting-edge protocols and production deployment.

## 🚀 Quick Start

**[Start Here: Cloud Development Environment](docs-content/00_intro/coder.md)** - Access your pre-configured workspace at `http://10.21.202.14/workspaces`

**Essential Setup:**
1. **[Cloud Environment Setup](docs-content/00_intro/coder.md)** - Pre-configured workspace with all dependencies
2. **[LLM API Configuration](docs-content/00_intro/llmapi.md)** - Gaia API access for AI models
3. **[🎧 Podcast Mode](docs/podcast-feature.md)** - Learn hands-free while commuting

## Course Structure

**3 Modules × 2 Weeks Each = 6 Weeks Total**

### Module 01: Agent Frameworks & Patterns
**Focus**: Core agent development with modern frameworks  
**[Start Module 01 →](docs-content/01_frameworks/Session0_Introduction_to_Agent_Frameworks_Patterns.md)**

- **Week 1**: Bare metal agents, LangChain, LangGraph, CrewAI, PydanticAI
- **Week 2**: Atomic Agents, ADK, Agno, Multi-agent patterns, Production deployment

### Module 02: Retrieval-Augmented Generation (RAG)
**Focus**: Advanced RAG systems and cognitive architectures  
**[Start Module 02 →](docs-content/02_rag/Session0_Introduction_to_RAG_Architecture.md)**

- **Week 1**: Basic RAG, chunking, vector databases, query enhancement, evaluation
- **Week 2**: Graph-based RAG, agentic RAG, multimodal RAG, production integration

### Module 03: MCP, ACP & A2A Communication
**Focus**: Agent communication protocols and distributed systems  
**[Start Module 03 →](docs-content/03_mcp-acp-a2a/Session0_Introduction_to_MCP_ACP_A2A.md)**

- **Week 1**: MCP server basics, filesystem integration, LangChain integration, production deployment
- **Week 2**: Security, ACP fundamentals, A2A communication, advanced workflows

## Learning Paths

Each session offers **3 learning paths** to match your time and depth preferences:

- **Observer Path** (30-50 min): Conceptual understanding and overview
- **Participant Path** (60-90 min): Guided implementation with examples  
- **Implementer Path** (120-180 min): Complete hands-on development

## Learning Outcomes

By completion, you will:

- **Master** the five core agentic patterns: Reflection, Tool Use, ReAct, Planning, Multi-Agent Collaboration
- **Build** production-ready agents using cutting-edge frameworks (LangChain, CrewAI, PydanticAI, Atomic Agents, Agno)
- **Implement** sophisticated RAG systems with NodeRAG, reasoning-augmented retrieval, and multimodal capabilities
- **Design** distributed agent architectures using MCP, ACP, and A2A protocols
- **Deploy** enterprise-grade agent systems with monitoring, security, and scalability

## Prerequisites

**Required:**
- Python programming (intermediate level)
- API integration experience (REST APIs, JSON)
- Software design understanding (OOP, design patterns)
- Development environment familiarity (virtual environments, package management)

**Recommended:**
- Basic LLM understanding
- HTTP protocols and web services experience
- Database and data processing knowledge
- Distributed systems concepts

## Getting Started

### Cloud Environment (Recommended)
Access your pre-configured workspace - no local installation needed!

1. **[Access Coder Workspace](docs-content/00_intro/coder.md)** - `http://10.21.202.14/workspaces`
2. **[Configure LLM API](docs-content/00_intro/llmapi.md)** - Gaia API setup
3. **[Enable Podcast Mode](docs/podcast-feature.md)** - Learn while commuting
4. **Choose your learning path** and start with Module 01

### Local Setup (Alternative)

#### Public Users (Standard Clone)
```bash
git clone https://github.com/fwornle/agentic-ai-nano.git
cd agentic-ai-nano
python -m venv venv
source venv/bin/activate
pip install -r docs-content/01_frameworks/src/session1/requirements.txt
mkdocs serve  # View documentation locally
```

#### Corporate Users (With Corporate Content)
```bash
# Clone with corporate content submodule
git clone --recurse-submodules https://github.com/fwornle/agentic-ai-nano.git
cd agentic-ai-nano
python -m venv venv
source venv/bin/activate
pip install -r docs-content/01_frameworks/src/session1/requirements.txt
mkdocs serve  # View documentation with corporate content
```

**Alternative for Corporate Users** (if submodules weren't cloned initially):
```bash
git clone https://github.com/fwornle/agentic-ai-nano.git
cd agentic-ai-nano
git submodule init
git submodule update  # Fetch corporate content
# Continue with setup...
```

## Navigation

### Documentation
- **[Interactive Documentation](http://127.0.0.1:8001)** - Full browsing experience with search
- **[Live Demo Site](https://fwornle.github.io/agentic-ai-nano)** - GitHub Pages deployment

### Module Quick Access
- **[Module 01: Frameworks](docs-content/01_frameworks/)** - Agent patterns and frameworks
- **[Module 02: RAG](docs-content/02_rag/)** - Advanced retrieval and reasoning systems
- **[Module 03: Protocols](docs-content/03_mcp-acp-a2a/)** - Agent communication and integration

### Resources
- **[Source Code Examples](docs-content/01_frameworks/src/)** - Complete implementations
- **[Architecture Diagrams](docs-content/01_frameworks/puml/)** - PlantUML system diagrams
- **[Podcast Feature Guide](docs/podcast-feature.md)** - Hands-free learning setup

## Corporate Content Management

This repository implements a sophisticated content management system that supports both public and corporate-specific content:

### Repository Access Models

**Public Access (Standard Clone):**
- Public users clone the repository without corporate content
- Receives generic course materials suitable for general audiences
- No access to corporate-specific content or proprietary configurations

**Corporate Access (Submodule Clone):**
- Corporate users clone with `--recurse-submodules` to access additional content
- Includes corporate-specific examples, configurations, and deployment guides
- Corporate content stored in a separate private repository as a git submodule

### Architecture Overview

**Dual Content System:**
- **Public Content**: Generic course materials available to all users
- **Corporate Content**: Organization-specific content accessible only to authorized users

**Key Components:**
- **Private Submodule**: Corporate content stored in private repository (`docs-content/corporate-only/`)
- **Network Detection**: Automatic corporate network detection (`docs-content/javascripts/network-detection.js`)
- **Content Encryption**: Corporate content encrypted for secure public deployment (`scripts/encrypt-corporate-content.js`)
- **Dynamic Decryption**: Client-side decryption when accessed from corporate network (`docs-content/javascripts/corporate-content-loader.js`)

### Content Structure

```
nano-degree/
├── docs-content/
│   ├── corporate-only/              # Private submodule (corporate users only)
│   │   ├── 00_intro/coder-detailed.md    # Corporate environment details
│   │   ├── 03_mcp-acp-a2a/Session10*    # Corporate enterprise deployment
│   │   ├── images/corp-*.png            # Corporate-specific diagrams
│   │   ├── puml/corp-*.puml             # Corporate architecture diagrams
│   │   ├── content.encrypted.json       # Encrypted content manifest
│   │   └── test.encrypted.json          # Decryption test file
│   ├── 00_intro/coder.md            # Conditional content (corporate/public)
│   └── javascripts/
│       ├── network-detection.js      # Corporate network detection
│       └── corporate-content-loader.js # Content decryption system
└── scripts/encrypt-corporate-content.js # Encryption utility
```

### Content Publishing Workflow

**For Public Deployment:**
1. Corporate content encrypted using AES-256-GCM
2. Encrypted manifest included in public repository
3. Network detection determines content visibility
4. Corporate content decrypted client-side on corporate network

**For Corporate Environment:**
- Direct access to unencrypted corporate content
- Corporate cloud development environment
- Pre-configured templates and organization-specific integrations

### Development Workflow

**Managing Corporate Content:**
```bash
# Update corporate content
cd docs-content/corporate-only
# Make changes to corporate files
git add . && git commit -m "Update corporate content"
git push origin main

# Encrypt for public deployment
node scripts/encrypt-corporate-content.js

# Test decryption (corporate network only)
# Access from corporate network - decryption tested automatically
```

**Content Guidelines:**
- Use conditional divs: `<div class="corp-corporate-only">` and `<div class="corp-public-alternative">`
- Corporate images: Store in `corporate-only/images/` with relative paths
- Reference corporate content: Use `../corporate-only/` paths from public content

### Security Features

- **Network-based Access Control**: Content visibility based on corporate network detection
- **Encryption at Rest**: Corporate content encrypted when included in public repository
- **Client-side Decryption**: Secure decryption only available from corporate network
- **IP Range Validation**: Multiple corporate IP range patterns for network detection
- **Automatic Content Switching**: Seamless transition between corporate and public content

This system ensures corporate-specific content remains secure while allowing flexible deployment across both internal and public environments.

## Certification

**Module Completion**: Complete all sessions, achieve 80%+ on assessments, implement practical exercises  
**Nanodegree Completion**: Complete all 3 modules + capstone project integrating all concepts

---

**Ready to build the future of AI agents?**

**[🚀 Start Your Journey: Setup Cloud Workspace →](docs-content/00_intro/coder.md)**

Transform your commute into productive learning time with our **[🎧 Podcast Mode](docs/podcast-feature.md)** - perfect for hands-free learning while driving!