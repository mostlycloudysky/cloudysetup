# CloudySetup

CloudySetup is a command-line interface (CLI) tool designed to streamline the process of managing AWS resources using AWS Cloud Control API. It leverages the power of generative AI to generate initial resource configurations, suggestions and intent on the cloud resources and supports CRUDL (Create, Read, Update, Delete, List) operations on AWS resources.

## Features

- **Generate Resource Configurations**: Uses generative AI to create initial JSON configurations compatible with AWS Cloud Control API.
- **CRUDL Operations**: Supports creating, reading, updating, deleting, and listing AWS resources.
- **Interactive Prompts**: Guide users through the process of configuring resources interactively.
- **Monitoring**: Provides real-time monitoring of resource creation status with detailed progress updates.
- **Error Handling**: Offers detailed error messages and suggestions for resolving issues.

## Installation

### Prerequisites

- Python 3.8+
- Virtual Environment (optional but recommended)

### Steps

1. **Clone the Repository**
   ```sh
   git clone https://github.com/yourusername/cloudysetup.git
   cd cloudysetup
   ```

2. **Create a Virtual Environment**
   ```sh
   python -m venv myenv
   source myenv/bin/activate  # On Windows use `myenv\Scripts\activate`
   ```
3. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```
4. **Install the CLI Tool**
5. ```sh
   Install the CLI Tool
   ```

## InstallationUsage

### Generating Resource Configurations
To generate a resource configuration, use the `generate` command:

```sh
cloudysetup-cli generate "create sns topic resource"
```

### Applying Configurations
To apply a generated configuration, use the `apply` command:

```sh
cloudysetup-cli apply /path/to/generated_config.json --monitor
```

### Example

Here's an example of generating and applying an SNS topic resource configuration:

```sh
# Generate a configuration
cloudysetup-cli generate "create sns topic resource"

# Apply the generated configuration
cloudysetup-cli apply /path/to/generated_config.json --monitor
```

### Project Structure

cloudysetup/
├── .github/
│   └── workflows/
├── cloudysetup/
│   ├── __init__.py
│   ├── cli_tool/
│   │   ├── __init__.py
│   │   └── cli.py
│   └── envapi_app/
├── resources/
├── myenv/
├── setup.py
├── requirements.txt
├── README.md
└── .env
