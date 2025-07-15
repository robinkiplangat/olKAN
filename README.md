# olKAN
**A lightweight, open-source data catalog platform**

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

olKAN is a lightweight data catalog platform inspired by CKAN but optimized for small teams, rapid deployment, and constrained environments. It provides a minimal, composable, and agent-friendly foundation for building data portals with a focus on simplicity and developer experience.

## ✨ Features

- **🗂️ Flat-File First**: Run your entire data portal from YAML files - no database required
- **🚀 API-Driven**: Clean REST API for every feature, perfect for automation and integrations
- **⚡ Simple CLI**: Initialize, serve, and manage your portal with intuitive commands
- **🎨 Beautiful UI**: Modern, responsive interface built with Tailwind CSS and HTMX
- **🔧 Developer-Centric**: Powerful CLI, flexible plugin architecture, and clear documentation
- **📱 Progressive Complexity**: Start simple with flat files, scale to databases when needed
- **🐳 Container-Ready**: Docker support for easy deployment anywhere

## 🚀 Quick Start

### Installation

```bash
pip install olkan
```

### Initialize a New Portal

```bash
olkan init my-data-portal
cd my-data-portal
```

### Start the Server

```bash
olkan serve
```

Open your browser to [http://localhost:8000](http://localhost:8000) to see your data portal!

## 📖 Usage

### Adding Datasets

#### Via YAML Files (Recommended)
Create a file in the `datasets/` directory:

```yaml
# datasets/health-facilities.yaml
id: kenya-health-facilities
title: Kenya Public Health Facilities
description: Comprehensive list of public health facilities in Kenya
owner_org: ministry-of-health
license_id: cc-by-4.0
tags:
  - health
  - kenya
  - facilities
resources:
  - name: Health Facilities CSV
    description: Complete dataset in CSV format
    url: https://data.example.com/health-facilities.csv
    format: csv
    filesize: 2048576
```

#### Via REST API
```bash
curl -X POST http://localhost:8000/api/v1/datasets \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Dataset",
    "description": "Dataset description",
    "owner_org": "my-organization",
    "tags": ["data", "example"]
  }'
```

#### Via Python
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/datasets",
        json={
            "title": "My Dataset",
            "description": "Dataset description", 
            "owner_org": "my-organization",
            "tags": ["data", "example"]
        }
    )
    dataset = response.json()
```

### CLI Commands

```bash
# Initialize new portal
olkan init my-portal --template basic

# Start development server
olkan serve --reload --port 8000

# Validate dataset files
olkan validate --datasets-dir datasets/

# Import dataset from file
olkan import-dataset path/to/dataset.yaml
```

## 🏗️ Project Structure

```
olkan/
├── app/                         # Main application code
│   ├── api/                     # FastAPI REST endpoints
│   │   └── datasets.py          # Dataset CRUD operations
│   ├── core/                    # Business logic and storage
│   │   ├── config.py            # Configuration management
│   │   └── storage.py           # Storage backends (flat-file, database)
│   ├── models/                  # Pydantic data schemas
│   │   └── schemas.py           # Dataset, Resource, Organization models
│   ├── web/                     # Frontend templates and static files
│   │   ├── templates/           # Jinja2 HTML templates
│   │   └── static/              # CSS, JS, images
│   └── main.py                  # FastAPI app factory
├── cli.py                       # CLI tool (Typer-based)
├── data/                        # User file uploads
├── datasets/                    # YAML dataset files (flat-file storage)
├── tests/                       # Test suite
├── docs/                        # Project documentation
│   ├── REF_Guide.md            # Complete implementation guide
│   ├── olKAN_spec.md           # Product requirements
│   └── designGuide.md          # UI/UX guidelines
├── pyproject.toml              # Project configuration and dependencies
├── Dockerfile                  # Container configuration
└── README.md                   # This file
```

## 🛠️ Development Setup

### Prerequisites

- Python 3.10 or higher
- Node.js 16+ (for Tailwind CSS)
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/olkan.git
   cd olkan
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Set up frontend assets**
   ```bash
   npm install
   npm run watch-css  # Start Tailwind CSS compilation
   ```

4. **Start development server**
   ```bash
   olkan serve --reload
   ```

5. **Run tests**
   ```bash
   pytest --cov=app
   ```

### Code Quality

```bash
# Linting and formatting
ruff check app/ tests/
black app/ tests/

# Type checking
mypy app/

# Security scanning
bandit -r app/
```

## 🚢 Deployment

### Docker (Recommended)

```bash
# Build and run with Docker
docker build -t olkan .
docker run -p 8000:8000 -v $(pwd)/datasets:/app/datasets olkan
```

### Docker Compose

```bash
# Start with flat-file storage
docker-compose up

# Start with PostgreSQL database
docker-compose --profile database up
```

### Production Environment

1. Set environment variables:
   ```bash
   export DEBUG=false
   export STORAGE_BACKEND=database
   export DATABASE_URL=postgresql://user:pass@db:5432/olkan
   export SECRET_KEY=your-production-secret-key
   ```

2. Deploy with your preferred method:
   - **Cloud**: AWS ECS, Google Cloud Run, Azure Container Instances
   - **Kubernetes**: Use provided k8s manifests
   - **Traditional**: systemd service with reverse proxy

## 📚 Documentation

- **[Complete Implementation Guide](docs/REF_Guide.md)** - Comprehensive step-by-step development guide
- **[Product Specification](docs/olKAN_spec.md)** - Requirements and architecture overview
- **[Design Guidelines](docs/designGuide.md)** - UI/UX design system and components
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (when server is running)

## 🎯 Core Principles

- **Simplicity First**: Prioritize ease of use, deployment, and maintenance
- **Developer-Centric**: Clean, intuitive experience with powerful tooling
- **Human & Machine Readable**: Simple metadata structure for all users
- **API-First Architecture**: Every function exposed via REST API
- **Progressive Complexity**: Start simple, scale as needed
- **Stateless & Portable**: Works seamlessly in any environment

## 🤝 Contributing

We welcome contributions! Please see our [contributing guidelines](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Run code quality checks: `ruff check && black --check .`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## 📋 Roadmap

### v0.1 (Current)
- [x] Core CRUD operations for datasets
- [x] Flat-file storage with YAML
- [x] REST API with FastAPI
- [x] CLI tool with Typer
- [x] Web interface with Tailwind CSS
- [x] Docker deployment

### v0.2 (Planned)
- [ ] Database backend (PostgreSQL, SQLite)
- [ ] User authentication and authorization
- [ ] File upload and preview functionality
- [ ] Advanced search with faceted filtering
- [ ] Data visualization components

### v0.3 (Future)
- [ ] Plugin system for extensibility
- [ ] API federation capabilities
- [ ] Advanced data validation
- [ ] Workflow automation
- [ ] Analytics and usage tracking

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by [CKAN](https://ckan.org/) - the world's leading open-source data portal platform
- Built with modern Python tools: [FastAPI](https://fastapi.tiangolo.com/), [Pydantic](https://pydantic.dev/), [Typer](https://typer.tiangolo.com/)
- Styled with [Tailwind CSS](https://tailwindcss.com/) for beautiful, responsive design

## 🔗 Links

- **Project Homepage**: [https://olkan.org](https://olkan.org)
- **Documentation**: [https://docs.olkan.org](https://docs.olkan.org)
- **Issue Tracker**: [GitHub Issues](https://github.com/your-org/olkan/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/olkan/discussions)

---

**Made with ❤️ for the open data community**
