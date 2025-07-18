# pyddcci

A Python application to control your monitor(s) using DDC/CI.

## Overview

**pyddcci** is a command-line tool and Python library for querying and controlling monitor settings (such as brightness, contrast, and input source) using the DDC/CI protocol. It supports multiple monitors and provides a flexible, extensible architecture for advanced users and developers.

## Features

- Query and set monitor settings via DDC/CI
- Support for multiple monitors
- Extensible command-line interface (CLI)
- Configuration via YAML files
- Logging and debugging support
- Modular codebase for easy extension

## Installation

1. Clone this repository:
   ```sh
   git clone https://github.com/yourusername/pyddcci.git
   cd pyddcci
   ```
2. Install dependencies (Python 3.13+ required):
   ```sh
   pip install -r requirements.txt
   ```
   (You may need additional dependencies depending on your OS and monitor hardware.)

## Usage

Run the main CLI:
```sh
python pyddcci.py [options]
```

For help and available commands:
```sh
python pyddcci.py --help
```

### Global Options

- `-v`, `--verbosity` — Set console log verbosity (e.g., DEBUG, INFO, WARNING)
- `-lv`, `--log-verbosity` — Set logfile verbosity
- `-l`, `--list`, `--list-monitors` — List detected monitors and exit
- `-ie`, `--ignore-errors` — Continue execution even if a command fails

### Commands

#### Get Monitor Setting
Retrieve the value of a monitor setting (e.g., brightness, input source).

```sh
python pyddcci.py -g <filter> <code> [+raw]
```
- `-g`, `--get` — Get a VCP code value
- `<filter>` — Monitor selector (e.g., `primary`, regex, etc.)
- `<code>` — VCP code or alias (e.g., `brightness`, `contrast`, `input`)
- `+raw` — Output raw value (optional)

**Example:**
```sh
python pyddcci.py -g primary brightness
python pyddcci.py -g primary input +raw
```

#### Set Monitor Setting
Set a monitor setting to a specific value.

```sh
python pyddcci.py -s <filter> <code> <value> [+verify|+no_verify]
```
- `-s`, `--set` — Set a VCP code value
- `<filter>` — Monitor selector
- `<code>` — VCP code or alias
- `<value>` — Value to set (integer or alias)
- `+verify` — Verify after setting (default)
- `+no_verify` — Do not verify after setting

**Example:**
```sh
python pyddcci.py -s primary brightness 80
python pyddcci.py -s primary input hdmi1 +no_verify
```

#### Multi-Set
Set a monitor setting to multiple values in sequence (useful for scripting or cycling through values).

```sh
python pyddcci.py -ms <filter> <code> <value1> <value2> ... [+verify|+no_verify]
```
- `-ms`, `--multi-set` — Set a VCP code to multiple values
- `<filter>` — Monitor selector
- `<code>` — VCP code or alias
- `<value1> <value2> ...` — Values to set in order
- `+verify` / `+no_verify` — (see above)

**Example:**
```sh
python pyddcci.py -ms primary contrast 0 100 50
```

#### Toggle
Cycle a monitor setting through a list of values (e.g., toggle input source).

```sh
python pyddcci.py -t <filter> <code> <value1> <value2> ... [+verify|+no_verify]
```
- `-t`, `--toggle` — Toggle a VCP code between values
- `<filter>` — Monitor selector
- `<code>` — VCP code or alias
- `<value1> <value2> ...` — Values to toggle between
- `+verify` / `+no_verify` — (see above)

**Example:**
```sh
python pyddcci.py -t primary input hdmi1 dp1
```

### Filters and Codes
- **Filter**: Selects which monitor(s) to target. Common values: `primary`, regex, or custom YAML filter.
- **Code**: VCP code or alias (e.g., `brightness`, `contrast`, `input`, `power`).
- **Value**: Integer or string alias (e.g., `80`, `hdmi1`, `dp1`).

Default VCP code and value aliases are defined in [`app/ddcci/vcp/vcp_spec.py`](app/ddcci/vcp/vcp_spec.py).

### Configuration

Configuration is managed via YAML files in the `data/` directory. Do not modify `config.default.yaml` directly; instead, copy it to `config.yaml` and edit as needed.

## Project Structure

- `pyddcci.py` — Main entry point
- `app/` — Application modules
  - `cli/` — Command-line interface and commands
  - `ddcci/` — DDC/CI protocol implementation and monitor management
  - `util/` — Utilities, configuration, and logging
- `data/` — Default configuration files
- `test/` — Unit tests

## Running Tests

To run the testcases in the `test` folder, use Python's built-in unittest module. From the project root directory, run:

```sh
python -m unittest discover -b -s test
```

This will automatically discover and run all tests in the `test` directory and its subdirectories.

You can also run a specific test file, for example:

```sh
python -m unittest -b test.ddcci.test_monitor
```

For more verbose output, add the `-v` flag:

```sh
python -m unittest discover -b -s test -v
```

### Test Suite Structure

The `test` folder contains unit tests for the main components of pyddcci:

- `test/ddcci/` — Tests for DDC/CI protocol implementation, monitor management, and configuration (e.g., `test_monitor.py`, `test_monitor_config.py`).
- `test/ddcci/cli/` — Tests for the command-line interface and CLI commands.
- `test/ddcci/os/` — Tests for OS-specific monitor detection and mock monitor info.
- `test/ddcci/vcp/` — Tests for VCP code and value storage.
- `test/util/` — Tests for utility modules, including argument parsing and mixins.

Each test file targets a specific module or feature. For example, `test_monitor_config.py` verifies monitor configuration loading, saving, and filtering logic. Mock objects are used where appropriate to simulate monitor hardware and OS behavior.

To contribute new tests, add them to the appropriate subdirectory and follow the structure of existing test files.

## License

This project is licensed under the GNU General Public License v3.0 or later. See the [LICENSE](LICENSE) file for details.

## Author

Copyright © 2020 Rui Pinheiro