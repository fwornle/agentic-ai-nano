# Getting Started

Welcome to the Agentic AI Nano-Degree! This guide will help you set up your environment and begin your learning journey.

## Quick Start

1. **Set Up Environment**: Configure your development environment - see [Setup & Environment](00_intro/coder.md)
2. **Choose Your Module**: Start with [Agent Frameworks](01_frameworks/index.md), [RAG Architecture](02_rag/index.md), or [MCP & Agent Protocols](03_mcp-acp-a2a/index.md)
3. **Select Learning Path**: Observer, Participant, or Implementer based on your time and depth needs
4. **Begin Learning**: Start with Session 0 of your chosen module

## Prerequisites

### Required Knowledge
- **Python Programming**: Intermediate level (functions, classes, modules)
- **Command Line**: Basic terminal/command prompt usage
- **Git**: Basic version control operations
- **APIs**: Understanding of REST APIs and HTTP

### Recommended Background
- **Machine Learning**: Basic understanding of ML concepts
- **Databases**: Familiarity with SQL and NoSQL databases
- **Cloud Platforms**: Exposure to AWS, GCP, or Azure
- **Docker**: Basic containerization concepts

### Hardware Requirements
- **RAM**: Minimum 8GB, recommended 16GB+
- **Storage**: 10GB free space for code examples and models
- **Internet**: Stable connection for API calls and model downloads
- **OS**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)

## Course Overview

This nano-degree consists of three comprehensive modules:

### Module 1: Agent Frameworks (10 Sessions)
Master the art of building intelligent agents using cutting-edge frameworks like LangChain, CrewAI, PydanticAI, and more.

### Module 2: RAG Architecture (10 Sessions)
Build sophisticated Retrieval-Augmented Generation systems for enterprise applications with advanced chunking, vector databases, and evaluation techniques.

### Module 3: MCP, ACP & Agent-to-Agent Communication (10 Sessions)
Master the Model Context Protocol, Agent Communication Protocol, and sophisticated multi-agent coordination patterns.

## Learning Paths Guide

### 👀 Observer Path (30-80 min/session)
**Best for**: Quick understanding, decision makers, busy schedules

### Activities
- Read core concepts and architectural overviews
- Examine code examples and patterns
- Understand design decisions and trade-offs
- Review use cases and applications

**Setup**: Minimal - just read the materials

### 🙋‍♂️ Participant Path (50-110 min/session)
**Best for**: Hands-on learners, developers, practical understanding

### Activities
- Follow guided implementations step-by-step
- Run provided code examples
- Complete exercises and mini-projects
- Analyze and modify existing implementations

**Setup**: Full environment with API keys

### 🛠️ Implementer Path (120-260 min/session)
**Best for**: Deep expertise, architects, production focus

### Activities
- Build complete systems from scratch
- Implement custom components and optimizations
- Explore advanced patterns and architectures
- Create production-ready solutions

**Setup**: Full environment plus additional tools (Docker, cloud access)

## Project Structure

```
nano-degree/
├── 01_frameworks/          # Agent Frameworks Module
│   ├── Session0_Introduction/
│   ├── Session1_Bare_Metal/
│   ├── ...
│   └── src/                # Source code examples
├── 02_rag/                 # RAG Architecture Module  
│   ├── Session0_Introduction/
│   ├── Session1_Basic_RAG/
│   ├── ...
│   └── src/                # RAG implementations
├── 03_mcp-acp-a2a/         # MCP, ACP & A2A Module
│   ├── Session0_Introduction/
│   ├── Session1_Basic_MCP/
│   ├── ...
│   └── src/                # Protocol implementations
├── docs/                   # Documentation and guides
├── tests/                  # Test suites
├── requirements.txt        # Core dependencies
└── README.md              # Project overview
```

## Study Recommendations

### Time Management
- **Consistent Schedule**: Set aside dedicated learning time
- **Session Completion**: Finish sessions completely before moving on
- **Practice Time**: Allow extra time for hands-on practice
- **Review Period**: Revisit complex concepts after a few days

### Learning Strategies
1. **Start with Foundations**: Don't skip early sessions
2. **Practice Immediately**: Run code examples as you learn
3. **Take Notes**: Document insights and modifications
4. **Join Community**: Engage with other learners
5. **Apply Practically**: Use concepts in real projects

### Common Schedules

### Intensive (2-3 weeks)
- 2 sessions per day (Observer path)
- 1 session per day (Participant path)  
- 1 session every 2 days (Implementer path)

### Regular (4-6 weeks)
- 1 session per day (Observer path)
- 1 session every 2 days (Participant path)
- 2-3 sessions per week (Implementer path)

### Extended (8-12 weeks)
- 3-4 sessions per week (any path)
- More time for practice and projects
- Deep exploration of optional modules

## Development Tools

### Recommended IDEs
- **VS Code**: Excellent Python support, extensions
- **PyCharm**: Professional Python IDE
- **Jupyter**: Great for experimentation and learning

### Useful Extensions/Plugins
- Python syntax highlighting and linting
- Git integration
- Docker support
- Markdown preview
- Code formatting (Black, autopep8)

### Command Line Tools
```bash
# Code formatting
pip install black isort

# Linting
pip install flake8 pylint

# Testing
pip install pytest pytest-cov

# Documentation
pip install mkdocs mkdocs-material
```

## 🆘 Support & Community

### Getting Help

1. **Documentation**: Check session materials and API docs first
2. **GitHub Issues**: Report bugs or unclear instructions
3. **Discussions**: Join community discussions for questions
4. **Stack Overflow**: Use tags `agentic-ai`, `langchain`, `rag`

### Community Resources

- **GitHub Discussions**: Course-specific questions and sharing
- **Discord/Slack**: Real-time chat with other learners
- **Office Hours**: Weekly community calls (check schedule)
- **Study Groups**: Form groups with other learners

### Troubleshooting

### Common Issues

- **API Rate Limits**: Use smaller examples, implement delays
- **Memory Issues**: Close other applications, use smaller models
- **Import Errors**: Check virtual environment activation
- **Network Issues**: Verify API keys and internet connection

### Debug Steps
1. Check error messages carefully
2. Verify environment variables
3. Test with minimal examples
4. Check API status pages
5. Ask for help with specific error details

## Progress Tracking

### Session Completion
- [ ] Read all core content
- [ ] Run code examples successfully  
- [ ] Complete exercises/assignments
- [ ] Pass assessment quizzes
- [ ] Understand key concepts

### Module Milestones
- [ ] **Session 0-2**: Foundations established
- [ ] **Session 3-5**: Intermediate concepts mastered  
- [ ] **Session 6-8**: Advanced patterns implemented
- [ ] **Session 9**: Production deployment ready

### Portfolio Projects
Consider building these throughout your learning:

1. **Personal Assistant Agent** (Sessions 1-4)
2. **Document Q&A System** (Sessions 1-3 RAG)
3. **Multi-Agent Collaboration** (Sessions 7-9)
4. **Enterprise RAG System** (Sessions 6-9 RAG)

## Certification

Upon completion, you can:
- **Document Progress**: Keep a portfolio of implementations
- **Share Projects**: Publish code examples and write-ups
- **Join Alumni**: Access to ongoing community and updates
- **Contribute**: Help improve course materials

---

**Ready to start learning?** Choose your path and dive into the world of Agentic AI!

[Start with Agent Frameworks →](01_frameworks/index.md){ .md-button .md-button--primary }
[Begin with RAG Architecture →](02_rag/index.md){ .md-button }
[Master Agent Communication →](03_mcp-acp-a2a/index.md){ .md-button }