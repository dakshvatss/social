# Social Profiles Intel — Local App

A high-performance local data management app for 60k+ social profiles with
AG Grid infinite-scroll tabulation, server-side filtering, and full CRUD.

---

## Tech Stack

| Layer      | Technology               | Why                                      |
|------------|--------------------------|------------------------------------------|
| Backend    | **FastAPI** (Python)     | Fast async API, auto Swagger docs        |
| ORM        | **SQLAlchemy 2**         | Clean models, query builder              |
| Validation | **Pydantic v2**          | Request/response schemas                 |
| Database   | **PostgreSQL**           | Handles 60k+ rows with indexes easily    |
| DB Driver  | **psycopg2-binary**      | Reliable Postgres adapter                |
| Server     | **Uvicorn**              | ASGI server with hot-reload              |
| Frontend   | **AG Grid Community**    | Virtual scrolling for 60k rows — CDN     |
| UI Fonts   | **Google Fonts CDN**     | Barlow Condensed + JetBrains Mono        |

No React, no Node.js, no build step — just Python + one HTML file.

---

## Quick Start (Local Setup)

**Prerequisites:** PostgreSQL server running, database tables already created, PgAdmin access available

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd social
```

### Step 2: Create Environment File

Create a `.env` file in the project root with your PostgreSQL connection details:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/social_profiles
```

Replace `your_password` with your actual PostgreSQL password and update other connection parameters if needed.

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
python -m uvicorn main:app --reload
```

Or without hot-reload:
```bash
uvicorn main:app
```

The application will start on `http://localhost:8000`

### Step 5: Access the Application

- **Web UI:** Open browser and navigate to `http://localhost:8000`
- **API Docs:** Visit `http://localhost:8000/docs` (interactive Swagger UI)
- **ReDoc:** Visit `http://localhost:8000/redoc` (alternative API documentation)

---

## Features

| Feature              | Detail                                          |
|----------------------|-------------------------------------------------|
| Infinite scroll grid | AG Grid loads 200 rows/block — handles 60k+     |
| Multi-column groups  | Identity / Contact / Facebook / Twitter / Instagram |
| Status badges        | Color-coded Active / Verified badges per cell   |
| Follower formatting  | Auto K/M suffix (e.g. 125.3K, 4.2M)            |
| Search               | Full-text across name, IDs, email, constituency |
| Dropdowns            | Zone, District, Constituency, Designation       |
| Toggle filters       | Active-only / Verified-only quick filters       |
| Add/Edit modal       | Tabbed form (Basic Info + 3 platform tabs)      |
| Delete               | Single delete with confirmation                 |
| Bulk delete          | Select rows → Delete Selected button            |
| CSV Export           | Respects current filters                        |
| Stats sidebar        | Total followers per platform, active counts     |
| Header pills         | Total, active, verified counts live             |

---

## API Endpoints

| Method | Path                          | Description                        |
|--------|-------------------------------|------------------------------------|
| GET    | `/api/profiles`               | List with pagination + filters     |
| GET    | `/api/profiles/{id}`          | Single profile                     |
| POST   | `/api/profiles`               | Create                             |
| PUT    | `/api/profiles/{id}`          | Update                             |
| DELETE | `/api/profiles/{id}`          | Delete                             |
| POST   | `/api/profiles/bulk-delete`   | Bulk delete `{ids: [1,2,3]}`       |
| GET    | `/api/stats`                  | Aggregated stats                   |
| GET    | `/api/filter-options`         | Dropdown values                    |
| GET    | `/api/export/csv`             | CSV export (filter-aware)          |
| GET    | `/docs`                       | Auto-generated Swagger UI          |

---

## Performance Notes:

- Indexes are created on zone, district, constituency, designation, name, and all followers columns.
- The grid uses AG Grid's **Infinite Row Model** — only 200 rows loaded per scroll block.
- Server handles all sorting and filtering; the browser never holds 60k rows.
- `pool_size=10` connection pool handles concurrent requests without overhead.
