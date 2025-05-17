# Modern Git Assistant

A modern, user-friendly GUI application for Git operations built with Python and CustomTkinter. This tool simplifies common Git workflows with an intuitive interface and elegant design.

## Features

- **Intuitive Interface**: Clean and modern UI with dark/light theme support
- **Core Git Operations**:
  - Commit changes with custom messages
  - Push/Pull/Fetch operations
  - Stash management (stash, apply, pop)
- **Repository Management**:
  - Open existing repositories
  - Initialize new repositories
  - Auto-load last session
- **Visual Feedback**:
  - Real-time repository status
  - Commit history log
  - Branch information
- **Quality of Life**:
  - Keyboard shortcuts
  - Error handling with user-friendly messages
  - Session persistence
  - Configurable settings

## Installation

1. Clone the repository
2. Install required dependencies
3. Run the application

## Requirements

- Python 3.x
- CustomTkinter
- GitPython
- Git (installed on your system)

## Usage

1. Launch the application
2. Open an existing repository or initialize a new one
3. Use the intuitive interface to perform Git operations
4. Toggle between dark/light themes as needed

## Keyboard Shortcuts

- `Ctrl + R`: Refresh repository
- `Ctrl + L`: Update log
- `Ctrl + O`: Open repository

## Configuration

The application automatically saves your preferences in:
- `~/.modern_git_assistant/config.json`: Application settings
- `~/.modern_git_assistant/session.json`: Session information

## Credits

- Created by [robbiee09](https://github.com/robbiee09)
- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- Git integration using [GitPython](https://github.com/gitpython-developers/GitPython)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

For bug reports and feature requests, please open an issue on the GitHub repository.