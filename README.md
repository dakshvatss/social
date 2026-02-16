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

## Quick Start

### 1. Clone / unzip this folder

```
social_profiles_app/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── requirements.txt
├── .env.example
├── setup.sql
└── static/
    └── index.html
```

### 2. Set up PostgreSQL

```sql
-- In psql as superuser:
CREATE DATABASE social_profiles;
```

Then run the setup script in that database:
```bash
psql -U postgres -d social_profiles -f setup.sql
```

### 3. Load your CSV

Edit `setup.sql` and uncomment the COPY block at the bottom, or run directly:

```sql
-- In psql connected to social_profiles:
COPY public.social_profiles (
    zone, party_district, constituency, designation, name,
    whatsapp_number, dob, address, email_id,
    facebook_id, facebook_followers, facebook_active_status, facebook_verified_status,
    twitter_id, twitter_followers, twitter_active_status, twitter_verified_status,
    instagram_id, instagram_followers, instagram_active_status, instagram_verified_status
)
FROM 'C:\path\to\your\file.csv'
DELIMITER ',' CSV HEADER;
```

> **If your table already exists** (id column missing), use the ALTER TABLE
> commands in the OPTION B section of setup.sql.

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env — set your DATABASE_URL
```

```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/social_profiles
```

### 5. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the app

```bash
python main.py
```

Open **http://localhost:8000** in your browser.

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

## Performance Notes

- Indexes are created on zone, district, constituency, designation, name, and all followers columns.
- The grid uses AG Grid's **Infinite Row Model** — only 200 rows loaded per scroll block.
- Server handles all sorting and filtering; the browser never holds 60k rows.
- `pool_size=10` connection pool handles concurrent requests without overhead.
