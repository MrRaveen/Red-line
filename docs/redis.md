# Redis Setup & Key Naming Conventions

This document outlines the standard Redis connection setup and key naming conventions across all microservices (based on the implementation pattern in `prompt_injection_attack`).

---

## 1. Redis Connection Setup

Each Flask microservice manages Redis using connection pooling and Flask's request context (`g`).

### Environment & Configuration Parameters (`config.py`)
- `REDIS_HOST`: Redis server host address.
- `REDIS_PORT`: Redis server port (e.g., `6379`).
- `REDIS_DB`: Redis database index.
- `REDIS_USERNAME`: Redis auth username (if enabled).
- `REDIS_PASSWORD`: Redis auth password (if enabled).
- `REDIS_SSL`: Boolean flag for SSL (`true`/`false`).
- `REDIS_KEY_PREFIX`: Optional prefix namespace.
- `REDIS_MAX_CONNECTIONS`: Maximum connections in the pool.
- `REDIS_SOCKET_TIMEOUT`: Read timeout in seconds (default: `5`).
- `REDIS_SOCKET_CONNECT_TIMEOUT`: Connect timeout in seconds (default: `5`).

### Pattern Implementation (`extensions.py`)
1. **Application Initialization**: A single `ConnectionPool` is attached to `app.redis_pool` on application startup (`init_redis(app)`).
2. **Request-Scoped Connection**: Individual requests retrieve a thread-safe client using `get_redis()`, cached inside Flask's request context object (`g.redis_client`).

```python
def init_redis(app):
    app.redis_pool = get_redis_pool(app)

def get_redis():
    if "redis_client" not in g:
        g.redis_client = redis.Redis(connection_pool=current_app.redis_pool)
    return g.redis_client
```

---

## 2. Key Naming Rules

To maintain namespace isolation across shared Redis instances and prevent key collision, all Redis keys **must** follow this colon-separated template:

### Key Standard Template
```text
{service_name}:{data_type}:{identifier}
```

### Components
| Segment | Description | Example |
| :--- | :--- | :--- |
| **`service_name`** | Name of the producing microservice | `prompt_injection`, `main_service` |
| **`data_type`** | Category/type of stored data | `llm_context`, `session`, `auth_token` |
| **`identifier`** | Unique resource ID or identifier | `user_123`, `job_456` |

### Examples
- `prompt_injection:llm_context:userID`
- `saga_orchestrator:transaction_state:txn_987`
