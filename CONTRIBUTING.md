# Contributing to PyPM2

Thank you for your interest in contributing to PyPM2! We welcome contributions from the community.

## 🚀 Quick Start

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `./run_all_tests.sh`
6. Commit your changes: `git commit -m "Add amazing feature"`
7. Push to your branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## 🧪 Testing

Before submitting a pull request, please ensure:

```bash
# Run all tests
./run_all_tests.sh

# Run unit tests only
python3 -m pytest tests/ -v

# Test installation
./install.sh
```

## 📝 Code Style

- Follow PEP 8 guidelines
- Add docstrings to all functions and classes
- Use type hints where appropriate
- Keep functions focused and small
- Write descriptive commit messages

## 🐛 Bug Reports

When reporting bugs, please include:

- Python version
- Operating system
- PyPM2 version
- Steps to reproduce
- Expected vs actual behavior
- Error messages or logs

## 💡 Feature Requests

For feature requests:

- Describe the use case
- Explain why it would be useful
- Consider providing a basic implementation idea
- Check existing issues to avoid duplicates

## 📚 Documentation

Help improve our documentation:

- Fix typos or unclear explanations
- Add examples and use cases
- Improve API documentation
- Update installation instructions

## 🏗️ Development Setup

```bash
# Clone the repository
git clone https://github.com/pypm2/pypm2.git
cd pypm2

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-cov

# Run tests
python3 -m pytest tests/ -v
```

## 📋 Pull Request Guidelines

- Keep PRs focused on a single feature or fix
- Include tests for new functionality
- Update documentation if needed
- Ensure all tests pass
- Add a clear description of changes

## 🎯 Areas for Contribution

We especially welcome contributions in:

- Performance optimizations
- Cross-platform compatibility
- Additional monitoring features
- Integration with other tools
- Documentation improvements
- Example applications

## 📞 Getting Help

- Open an issue for questions
- Check existing documentation
- Look at example applications
- Review the test suite for usage patterns

## 🙏 Recognition

Contributors will be recognized in:

- Release notes
- Contributors file
- GitHub contributor graph

Thank you for helping make PyPM2 better!
