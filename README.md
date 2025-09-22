# Agentic AI Nanodegree

**Advanced AI Agent Development & Protocol Integration** - A comprehensive 6-week self-paced program covering modern AI agent development, from foundational patterns through cutting-edge protocols and production deployment.

> **🔒 Corporate Content Security Notice**: This repository contains only public course materials. BMW-specific corporate content is delivered securely through automatic network detection and encryption - no sensitive corporate information is stored in this public repository or exposed outside BMW corporate networks.

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
- **Week 2**: Security, ACP fundamentals, A2A communication, advanced workflows, enterprise integration

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

## Corporate Content Availability

This nanodegree features **automatic corporate network (CN) detection** that securely unlocks additional BMW-specific content when accessed from BMW corporate networks. **Important**: Sensitive corporate content is never stored in this public repository or exposed outside the BMW corporate network.

### How Secure Content Access Works

**🌐 Public Network Access:**
- Generic course materials suitable for all audiences
- Local development environment setup guides
- Public LLM API configuration (OpenAI, Anthropic, etc.)
- Standard 9-session course structure per module

**🏢 BMW Corporate Network Access (Secure):**
- **Automatic Detection**: System detects corporate network via IP ranges and internal service accessibility
- **Encrypted Content Delivery**: Corporate content is encrypted and only decryptable from BMW networks
- **Enhanced Content**: BMW-specific examples, configurations, and deployment guides
- **Additional Sessions**: Access to Session 10 "Enterprise Integration & Production Deployment"
- **Cloud Development Environment**: Pre-configured BMW Coder workspace access
- **BMW Gaia LLM API**: Internal LLM service integration
- **Corporate Infrastructure**: BMW-specific architecture diagrams and integration patterns

### Security & Content Protection

**🔒 Content Security Model:**
- **No Sensitive Data in Repository**: Corporate content is never stored in plaintext in this public repository
- **Encrypted Distribution**: Corporate content is AES-256-GCM encrypted before inclusion in public deployments
- **Network-Based Decryption**: Content can only be decrypted and viewed from BMW corporate networks
- **Automatic Fallback**: Public users always see appropriate generic content without corporate details

### Network Detection Indicators

When you access the course, you'll see visual indicators of your network status:

- **🏢 BMW Corporate Network**: Blue indicator shows cloud development environment is available
- **🌐 Public Network**: Green indicator shows local setup is required
- **🔍 Detecting Network...**: Orange indicator during network detection process

### Repository Access Models

**Public Users (Standard Access):**
```bash
git clone https://github.com/fwornle/agentic-ai-nano.git
# No additional setup needed - corporate content loads automatically if on BMW network
```

**Corporate Users (Local Development):**
```bash
# Option 1: Clone with corporate submodule for local development
git clone --recurse-submodules https://github.com/fwornle/agentic-ai-nano.git

# Option 2: Add corporate submodule to existing clone
git clone https://github.com/fwornle/agentic-ai-nano.git
cd agentic-ai-nano
git submodule init && git submodule update
```

### Corporate Content Detection Details

**Network Detection Process:**
1. **Hostname Detection**: Checks for `*.bmw.com`, `*.bmwgroup.com`, and internal IP ranges
2. **External IP Verification**: Validates against BMW IP ranges (160.46.*, 194.114.*, etc.)
3. **Internal Service Test**: Tests accessibility to `contenthub.bmwgroup.net`
4. **Automatic Fallback**: Gracefully falls back to public content if detection fails

**What Corporate Users Get:**

**Enhanced Module Content:**
- **Module 01**: BMW Coder cloud environment setup and integration
- **Module 02**: Corporate-specific RAG examples with internal data sources
- **Module 03**: Session 10 "Enterprise Integration & Production Deployment"
  - BMW-specific infrastructure patterns
  - Corporate deployment strategies
  - Enterprise security considerations
  - Production monitoring and scaling

**Corporate-Specific Features:**
- **Pre-configured Development Environment**: `http://10.21.202.14/workspaces`
- **BMW Gaia LLM API Access**: Internal model endpoints and authentication
- **Corporate Architecture Diagrams**: BMW-specific system integration patterns
- **Enterprise Security Examples**: Corporate authentication and authorization patterns

### Architecture Overview

**Intelligent Content System:**
- **Automatic Detection**: No manual switches or configuration required
- **Secure Content Delivery**: Corporate content encrypted and decrypted client-side
- **Seamless Experience**: Users see appropriate content based on their network automatically
- **Graceful Degradation**: Always falls back to public content to ensure accessibility

**Technical Components:**
- **Network Detection Engine**: Multi-layer corporate network detection
- **Content Encryption System**: AES-GCM encrypted corporate content for secure public deployment
- **Dynamic Content Loader**: Client-side decryption and content injection
- **Navigation Intelligence**: Automatic addition/removal of corporate navigation items

### Content Structure

```
nano-degree/ (Public Repository)
├── docs-content/
│   ├── 00_intro/coder.md            # Generic setup guide (corporate content injected dynamically)
│   ├── 01_frameworks/               # Public course content
│   ├── 02_rag/                      # Public course content  
│   ├── 03_mcp-acp-a2a/             # Public course content (Session 10 added dynamically)
│   └── javascripts/
│       ├── network-detection-unified.js  # Network detection & content injection
│       └── corporate-content-loader.js   # Legacy loader (deprecated)
├── scripts/
│   ├── encrypt-corporate-content.js      # Content encryption utility
│   └── inject-corporate-content.js       # Build-time content injection
└── site/                            # Built site (contains encrypted corporate content in HTML comments)
    └── **/*.html                    # Pages with encrypted content embedded for CN decryption

corporate-only/ (Private Repository - Referenced as Submodule)
├── content.encrypted.json           # AES-256-GCM encrypted content bundle
├── 00_intro/
│   ├── coder-concise.md             # Compact BMW Coder setup guide  
│   ├── coder-detailed.md            # Detailed BMW environment setup
│   └── llmapi-detailed.md           # BMW Gaia LLM API documentation
├── 03_mcp-acp-a2a/
│   └── Session10_Enterprise_Integration_Production_Deployment.md
└── images/                          # BMW-specific diagrams (encrypted)
    ├── bmw-*.png                    # Corporate architecture diagrams
    ├── coder-*.png                  # Development environment screenshots
    └── cn-*.png                     # Corporate network diagrams
```

**Security Note**: The `corporate-only/` directory is a private Git submodule. Corporate content is encrypted before being embedded in the public deployment and can only be decrypted from BMW corporate networks.

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

**For Corporate Content Maintainers (BMW Internal Only):**
```bash
# Note: This workflow requires access to the private corporate-only repository

# 1. Update corporate content (private repository)
cd docs-content/corporate-only
# Make changes to corporate files
git add . && git commit -m "Update corporate content"
git push origin main

# 2. Encrypt for public deployment (main repository)
cd ../../
node scripts/encrypt-corporate-content.js

# 3. Deploy encrypted content
git add docs-content/corporate-only
git commit -m "Update encrypted corporate content"
git push origin main

# 4. Test from corporate network
# Access deployed site - decryption tested automatically
```

**For Public Contributors:**
```bash
# Standard contribution workflow - no access to corporate content required
git clone https://github.com/fwornle/agentic-ai-nano.git
cd agentic-ai-nano
# Make changes to public content only
git add . && git commit -m "Update public content"
git push origin main
```

**Content Security Guidelines:**
- **Corporate Content**: Never include BMW-specific details in public content files
- **Generic Alternatives**: Always provide generic alternatives for corporate-specific instructions
- **Conditional Content**: Use automatic network detection rather than manual switches
- **Images**: Corporate images are encrypted and stored separately from public repository

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