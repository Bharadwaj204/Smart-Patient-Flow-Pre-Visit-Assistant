# Contributing to Smart Patient Flow & Pre-Visit Assistant (SPFPA)

Thank you for your interest in contributing to SPFPA! This guide will help you get started with contributing to this healthcare AI project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Code Standards](#code-standards)
- [Healthcare Compliance](#healthcare-compliance)

## 📜 Code of Conduct

This project adheres to a code of conduct that promotes a welcoming and inclusive environment:

- **Be respectful**: Treat all contributors with respect and professionalism
- **Be constructive**: Provide helpful feedback and suggestions
- **Be collaborative**: Work together towards improving healthcare technology
- **Be ethical**: Prioritize patient safety and privacy in all contributions
- **Be inclusive**: Welcome contributors from all backgrounds and experience levels

## 🚀 Getting Started

### Before You Start

1. **Read the README.md** to understand the project
2. **Check existing issues** to see what needs work
3. **Join our community** discussions for questions
4. **Understand healthcare context** - this is a medical technology project

### Types of Contributions

We welcome various types of contributions:

- 🐛 **Bug fixes**
- ✨ **New features**
- 📖 **Documentation improvements**
- 🧪 **Test coverage enhancements**
- 🎨 **UI/UX improvements**
- 🔧 **Performance optimizations**
- 🌐 **Accessibility improvements**
- 🏥 **Healthcare domain expertise**

## 💻 Development Setup

### Prerequisites

- Python 3.11+
- Git
- Basic understanding of healthcare terminology (helpful)
- Familiarity with AI/ML concepts (for advanced contributions)

### Local Setup

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/yourusername/smart-patient-flow-assistant.git
   cd smart-patient-flow-assistant
   ```

2. **Set up development environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Set up pre-commit hooks** (optional but recommended)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

4. **Run tests to ensure everything works**
   ```bash
   python test_system.py
   ```

### Development Dependencies

For advanced development, install additional tools:

```bash
pip install black flake8 mypy pytest pytest-cov
```

## 📝 Contributing Guidelines

### Branch Naming Convention

Use descriptive branch names:

- `feature/symptom-checker-enhancement`
- `bugfix/triage-accuracy-issue`
- `docs/api-documentation-update`
- `ui/accessibility-improvements`

### Commit Message Format

Follow conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

Examples:
```
feat(triage): add cardiovascular risk assessment
fix(ui): resolve text visibility issues in dark mode
docs(readme): update installation instructions
test(intake): add edge case testing for patient data
```

### Development Workflow

1. **Create an issue** (if one doesn't exist)
2. **Create a branch** from `main`
3. **Make your changes**
4. **Write/update tests**
5. **Update documentation**
6. **Test your changes**
7. **Submit a pull request**

## 🔄 Pull Request Process

### Before Submitting

Ensure your PR meets these criteria:

- ✅ **Code runs successfully**
- ✅ **Tests pass** (`python test_system.py`)
- ✅ **Code follows style guidelines**
- ✅ **Documentation is updated**
- ✅ **No sensitive data included**
- ✅ **Healthcare compliance considered**

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] UI/UX enhancement

## Testing
- [ ] System tests pass
- [ ] New tests added (if applicable)
- [ ] Manual testing completed

## Healthcare Considerations
- [ ] Patient safety implications reviewed
- [ ] Privacy considerations addressed
- [ ] Medical accuracy verified (if applicable)

## Screenshots (if applicable)
Add screenshots for UI changes

## Additional Notes
Any additional context or considerations
```

### Review Process

1. **Automated checks** run on all PRs
2. **Code review** by maintainers
3. **Healthcare expert review** (for medical content)
4. **Testing verification**
5. **Merge approval**

## 🐛 Issue Guidelines

### Bug Reports

Use this template for bug reports:

```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g. Windows 10, macOS Big Sur]
- Python version: [e.g. 3.11.0]
- Browser: [e.g. Chrome 91.0]

**Healthcare Context**
If this affects patient care or safety

**Screenshots**
If applicable
```

### Feature Requests

Use this template for feature requests:

```markdown
**Feature Description**
Clear description of the proposed feature

**Healthcare Value**
How this improves patient care or experience

**Use Case**
Specific scenarios where this would be helpful

**Implementation Ideas**
Technical suggestions (optional)

**Priority**
Low/Medium/High with justification
```

## 📏 Code Standards

### Python Code Style

- **Follow PEP 8** style guidelines
- **Use Black** for code formatting
- **Use descriptive variable names**
- **Include type hints** where appropriate
- **Write docstrings** for all functions and classes

Example:
```python
def calculate_risk_score(
    age: int, 
    symptoms: List[str], 
    medical_history: List[str]
) -> float:
    """
    Calculate patient risk score based on demographics and symptoms.
    
    Args:
        age: Patient age in years
        symptoms: List of reported symptoms
        medical_history: List of existing medical conditions
        
    Returns:
        Risk score between 0.0 and 1.0
        
    Raises:
        ValueError: If age is negative or symptoms list is empty
    """
    # Implementation here
    pass
```

### Documentation Standards

- **Clear and concise** explanations
- **Code examples** for complex features
- **Healthcare context** where relevant
- **Updated README.md** for significant changes
- **Inline comments** for complex logic

### Testing Standards

- **Unit tests** for all new functions
- **Integration tests** for user workflows
- **Edge case testing** for healthcare scenarios
- **Performance tests** for AI components
- **Accessibility testing** for UI changes

## 🏥 Healthcare Compliance

### Important Considerations

When contributing to healthcare technology:

1. **Patient Safety First**
   - Never compromise on medical accuracy
   - Include appropriate disclaimers
   - Validate medical information with experts

2. **Privacy Protection**
   - No real patient data in code
   - Secure handling of test data
   - Follow HIPAA guidelines

3. **Accessibility**
   - WCAG 2.1 AA compliance
   - Screen reader compatibility
   - Keyboard navigation support

4. **Medical Accuracy**
   - Verify medical information with sources
   - Include citations for medical claims
   - Get expert review for clinical features

### Sensitive Areas

Be extra careful when working on:

- **Emergency detection algorithms**
- **Triage logic and scoring**
- **Medical advice generation**
- **Drug interaction checking**
- **Age-specific recommendations**

## 🏆 Recognition

Contributors will be recognized in:

- **CONTRIBUTORS.md** file
- **Release notes** for significant contributions
- **Project documentation**
- **Community acknowledgments**

## 📞 Getting Help

### Contact Methods

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and ideas
- **Email**: healthcare-ai@example.com
- **Discord**: [Join our community](https://discord.gg/healthcare-ai)

### Development Questions

For development-specific questions:

- **Code architecture**: Check existing patterns in `src/`
- **AI/ML components**: Review `rag_pipeline.py` and `vector_db.py`
- **UI components**: Look at Streamlit documentation
- **Healthcare domain**: Consult medical professionals

## 🎉 First-Time Contributors

Welcome! We're excited to have you contribute to healthcare technology:

1. **Start small**: Look for "good first issue" labels
2. **Ask questions**: Don't hesitate to ask for help
3. **Learn the domain**: Familiarize yourself with healthcare terminology
4. **Join the community**: Participate in discussions
5. **Share ideas**: Your fresh perspective is valuable

### Easy Starting Points

- **Documentation improvements**
- **UI text and accessibility**
- **Test case additions**
- **Code comments and docstrings**
- **Example scenarios and demos**

Thank you for contributing to better healthcare technology! 🏥✨