# Insurance Quote Service

A REST API for managing insurance customers, quotes, and policies with age-based premium pricing.

## Tech Stack

- **Python 3.14** / **Django 6.1** / **Django REST Framework 3.18+**
- **PostgreSQL 16**
- **Poetry** (dependency management)
- **Docker** (containerized dev environment)

## Project Structure

```
├── app/
│   ├── models.py          # Customer, Policy, PolicyStateHistory
│   ├── pricing.py         # Age-based premium calculation
│   ├── serializers.py     # DRF serializers
│   ├── views.py           # API views
│   └── exceptions.py      # Custom exceptions
├── tests/app/
│   ├── test_pricing.py    # Pricing logic tests
│   └── test_views.py      # API endpoint tests
├── docker-compose.yml     # PostgreSQL + Django services
├── Dockerfile
├── Makefile
└── pyproject.toml
```

## Models

| Model | Description |
|---|---|
| **Customer** | Customer details (name, DOB) |
| **Policy** | Insurance policy linked to a customer, with type, premium, cover, and state |
| **PolicyStateHistory** | Audit trail for policy state transitions |

Policy states: `new` -> `quoted` -> `bound` -> `active` -> `accepted`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/create_customer/` | Create a customer |
| `GET` | `/api/v1/customer/` | Search customers by name |
| `POST` | `/api/v1/quote/` | Create a quote for a customer |
| `PATCH` | `/api/v1/quote/` | Update quote state |
| `GET` | `/api/v1/policies/` | List policies (filter by `customer_id`, `type`) |
| `GET` | `/api/v1/policies/<uuid:pk>/` | Get policy details |
| `GET` | `/api/v1/policies/<uuid:policy_id>/history/` | Get policy state history |

### Sample Requests

**Create a customer:**

```bash
curl -X POST http://localhost:8000/api/v1/create_customer/ \
  -H "Content-Type: application/json" \
  -d '{"first_name": "John", "last_name": "Doe", "dob": "15-08-1990"}'
```

**Search customers:**

```bash
curl "http://localhost:8000/api/v1/customer/?first_name=John"
```

**Create a quote:**

```bash
curl -X POST http://localhost:8000/api/v1/quote/ \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "<customer_id>", "type": "personal-accident"}'
```

**Update quote state:**

```bash
curl -X PATCH http://localhost:8000/api/v1/quote/ \
  -H "Content-Type: application/json" \
  -d '{"policy_id": "<policy_id>", "status": "bound"}'
```

**List policies:**

```bash
curl "http://localhost:8000/api/v1/policies/"
curl "http://localhost:8000/api/v1/policies/?customer_id=<customer_id>"
```

**Get policy details:**

```bash
curl http://localhost:8000/api/v1/policies/<policy_id>/
```

**Get policy state history:**

```bash
curl http://localhost:8000/api/v1/policies/<policy_id>/history/
```

## Pricing

**Supported product:** `personal-accident`

| Age Band | Multiplier | Premium |
|---|---|---|
| 18-25 | 1.20x | 240.00 |
| 26-35 | 1.00x | 200.00 |
| 36-50 | 1.10x | 220.00 |
| 51-65 | 1.50x | 300.00 |
| 66+ | 2.00x | 400.00 |

Base cover: **200,000**

## Local Setup

### Prerequisites

- Docker & Docker Compose
- Python 3.14
- Poetry

### 1. Clone and configure

```bash
git clone <repo-url> && cd Insurance-quote-service
cp .env.example .env
```

### 2. Start the app

```bash
make run
```

This builds the image, runs migrations, and starts the dev server at `http://localhost:8000`.

### 3. Create a superuser

```bash
make superuser
```

Follow the prompts to set a username, email, and password.

### 4. Access Django Admin

Navigate to [http://localhost:8000/admin/](http://localhost:8000/admin/) and log in with the superuser credentials created above.

Currently registered models in admin:
- **Customer** — view, search, and filter customers by name or DOB

## Make Commands

Run `make help` to list all available commands:

| Command | Description |
|---|---|
| **Docker** | |
| `make build` | Build docker images |
| `make up` | Start all services (detached) |
| `make down` | Stop and remove all services |
| `make db` | Start only the database |
| `make shell` | Open a bash shell in the web container |
| `make run` | Build and start dev server (foreground) |
| **Django** | |
| `make setup` | Run initial setup (migrate + makemigrations + migrate) |
| `make migrate` | Run Django migrations |
| `make makemigrations ARGS=app` | Create new migrations |
| `make superuser` | Create a Django admin superuser |
| **Code Quality** | |
| `make format` | Format code with Black |
| `make lint` | Lint code with Ruff |
| `make lint-fix` | Lint and auto-fix with Ruff |
| `make typecheck` | Run type checking with mypy |
| `make test` | Run tests with pytest |
