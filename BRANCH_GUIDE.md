# Branch Guide - Automation Hub

## Branch Strategy Overview

This project uses a dual-development approach with two specialized branches for different learning and development styles.

## 🤖 AI-Assisted Branch (`ai-assisted`)

**Purpose**: Rapid development with AI assistance

**When to use**:
- Need quick solutions to complex problems
- Want to see best practices and patterns
- Learning new technologies or concepts
- Prototyping and experimentation
- Time-sensitive bug fixes

**Development Style**:
- GitHub Copilot provides code suggestions
- AI helps with architecture decisions
- Focus on understanding AI-generated solutions
- Rapid iteration and testing

**Current Status**: 
- Full project documentation
- Comprehensive branching strategy
- Ready for AI-assisted development

## 🎯 Self-Driven Branch (`self-driven`)

**Purpose**: Manual development for deep learning

**When to use**:
- Want to build coding skills independently
- Need to understand implementation details
- Practicing problem-solving techniques
- Building confidence in your abilities
- Preparing for interviews or assessments

**Development Style**:
- Write all code manually
- Research solutions independently
- Use documentation and learning resources
- Focus on understanding concepts deeply
- Step-by-step debugging and testing

**Current Status**:
- Focused documentation with learning resources
- Identified development tasks from daily notes
- Ready for hands-on development

## 🚀 Main Branch (`main`)

**Purpose**: Stable production code

**Merge Strategy**:
- Merge stable features from either development branch
- Requires full testing before merge
- Maintains production-ready state

## How to Switch Between Branches

```bash
# Check current branch
git branch

# Switch to AI-assisted development
git checkout ai-assisted

# Switch to self-driven development  
git checkout self-driven

# Switch to stable main branch
git checkout main
```

## Current Development Tasks

Based on your daily notes, here are the identified issues to work on:

### 1. SOD Form Data Issues
- **Problem**: Success criteria not populating from SOD form correctly
- **Impact**: Templates showing wrong or missing data
- **Files**: `app.py`, `database.py`, `markdown_generator.py`

### 2. EOD Processing Problems
- **Problem**: Daily Capture content not populated correctly during EOD
- **Impact**: Notes from day not appearing in final template
- **Files**: `app.py`, `notion_manager.py`, `markdown_generator.py`

### 3. Template Generation Issues
- **Problem**: Big 3 and success being copied from yesterday
- **Impact**: Stale data in new daily notes
- **Files**: `markdown_generator.py`, database queries

### 4. Quick Capture Processing
- **Problem**: Quick capture section preserved day-to-day
- **Impact**: Notes not being processed and cleared
- **Files**: `notion_manager.py`, template processing logic

### 5. Infrastructure Migration
- **Problem**: Currently using Cloudflare tunneling
- **Goal**: Move to Raspberry Pi with your own domain
- **Tasks**: Setup nginx, SSL, port forwarding, DNS

## Recommended Development Approach

### For Learning (Use `self-driven`):
1. Pick one issue from the list above
2. Read the relevant code files
3. Write tests to reproduce the problem
4. Research the solution approach
5. Implement fix manually
6. Test thoroughly before committing

### For Speed (Use `ai-assisted`):
1. Describe the problem to AI
2. Review AI-generated solutions
3. Test and adapt as needed
4. Learn from the implementation
5. Document the solution

## Getting Started

1. **Choose your development style**
2. **Switch to the appropriate branch**
3. **Pick a specific issue to work on**
4. **Set up your development environment**
5. **Start coding!**

Remember: Both branches will eventually merge back to `main`, so you can switch between approaches as needed for different tasks.
