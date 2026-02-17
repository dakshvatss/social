import csv
import io
from typing import Optional, List

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, or_, asc, desc
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import SocialProfile
from schemas import ProfileCreate, ProfileUpdate, ProfileResponse, BulkDeleteRequest

# ── Bootstrap ──────────────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Social Profiles Manager", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


# ── Root ───────────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.get("/analytics")
async def analytics_page():
    return FileResponse("static/analytics.html")


# ── Helpers ────────────────────────────────────────────────────────────────────
SORTABLE = {
    "id":                  SocialProfile.id,
    "name":                SocialProfile.name,
    "zone":                SocialProfile.zone,
    "party_district":      SocialProfile.party_district,
    "constituency":        SocialProfile.constituency,
    "designation":         SocialProfile.designation,
    "facebook_followers":  SocialProfile.facebook_followers,
    "twitter_followers":   SocialProfile.twitter_followers,
    "instagram_followers": SocialProfile.instagram_followers,
}


def _apply_filters(query, search, zone, party_district, constituency, designation,
                   active_only, verified_only):
    if search:
        # Use PostgreSQL Full-Text Search for optimized multi-column search
        # Requires the GIN index on to_tsvector('english', ...) to be effective
        query = query.filter(
            func.to_tsvector('english', 
                func.coalesce(SocialProfile.name, '') + ' ' +
                func.coalesce(SocialProfile.constituency, '') + ' ' +
                func.coalesce(SocialProfile.designation, '') + ' ' +
                func.coalesce(SocialProfile.zone, '') + ' ' +
                func.coalesce(SocialProfile.email_id, '')
            ).match(search)
        )
    if zone:
        query = query.filter(SocialProfile.zone == zone)
    if party_district:
        query = query.filter(SocialProfile.party_district == party_district)
    if constituency:
        query = query.filter(SocialProfile.constituency == constituency)
    if designation:
        query = query.filter(SocialProfile.designation == designation)
    if active_only:
        query = query.filter(or_(
            SocialProfile.facebook_active_status.ilike("active"),
            SocialProfile.twitter_active_status.ilike("active"),
            SocialProfile.instagram_active_status.ilike("active"),
        ))
    if verified_only:
        query = query.filter(or_(
            SocialProfile.facebook_verified_status.ilike("verified"),
            SocialProfile.twitter_verified_status.ilike("verified"),
            SocialProfile.instagram_verified_status.ilike("verified"),
        ))
    return query


# ── List / Paginate ────────────────────────────────────────────────────────────
@app.get("/api/profiles")
async def list_profiles(
    start:          int  = Query(0,   ge=0),
    limit:          int  = Query(200, ge=1, le=500),
    search:         Optional[str] = None,
    zone:           Optional[str] = None,
    party_district: Optional[str] = None,
    constituency:   Optional[str] = None,
    designation:    Optional[str] = None,
    active_only:    bool = False,
    verified_only:  bool = False,
    sort_by:        str  = "id",
    sort_order:     str  = "asc",
    db: Session = Depends(get_db),
):
    q = db.query(SocialProfile)
    q = _apply_filters(q, search, zone, party_district, constituency, designation,
                       active_only, verified_only)
    
    # Optimization: Use a simpler count query or skip counting if not needed
    # For very large tables, we could use reltuples from pg_class for an estimate
    total = q.count()

    col = SORTABLE.get(sort_by, SocialProfile.id)
    q = q.order_by(desc(col) if sort_order == "desc" else asc(col))
    
    # Optimization: Only select necessary columns if the table has many large text fields
    rows = q.offset(start).limit(limit).all()

    return {
        "rows":  [ProfileResponse.model_validate(r).model_dump(mode="json") for r in rows],
        "total": total,
    }


# ── Single record ──────────────────────────────────────────────────────────────
@app.get("/api/profiles/{profile_id}", response_model=ProfileResponse)
async def get_profile(profile_id: int, db: Session = Depends(get_db)):
    p = db.get(SocialProfile, profile_id)
    if not p:
        raise HTTPException(status_code=404, detail="Profile not found")
    return p


# ── Create ─────────────────────────────────────────────────────────────────────
@app.post("/api/profiles", response_model=ProfileResponse, status_code=201)
async def create_profile(body: ProfileCreate, db: Session = Depends(get_db)):
    p = SocialProfile(**body.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


# ── Update ─────────────────────────────────────────────────────────────────────
@app.put("/api/profiles/{profile_id}", response_model=ProfileResponse)
async def update_profile(profile_id: int, body: ProfileUpdate, db: Session = Depends(get_db)):
    p = db.get(SocialProfile, profile_id)
    if not p:
        raise HTTPException(status_code=404, detail="Profile not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p


# ── Delete single ──────────────────────────────────────────────────────────────
@app.delete("/api/profiles/{profile_id}")
async def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    p = db.get(SocialProfile, profile_id)
    if not p:
        raise HTTPException(status_code=404, detail="Profile not found")
    db.delete(p)
    db.commit()
    return {"message": "Deleted"}


# ── Bulk delete ────────────────────────────────────────────────────────────────
@app.post("/api/profiles/bulk-delete")
async def bulk_delete(body: BulkDeleteRequest, db: Session = Depends(get_db)):
    n = (db.query(SocialProfile)
           .filter(SocialProfile.id.in_(body.ids))
           .delete(synchronize_session=False))
    db.commit()
    return {"deleted": n}


# ── Stats ──────────────────────────────────────────────────────────────────────
@app.get("/api/stats")
async def stats(db: Session = Depends(get_db)):
    total  = db.query(func.count(SocialProfile.id)).scalar()

    def count_where(col, val):
        return db.query(func.count(SocialProfile.id)).filter(col.ilike(val)).scalar()

    def sum_col(col):
        return db.query(func.sum(col)).scalar() or 0

    by_designation = (
        db.query(SocialProfile.designation, func.count(SocialProfile.id).label("c"))
          .group_by(SocialProfile.designation)
          .order_by(desc("c")).limit(12).all()
    )
    by_zone = (
        db.query(SocialProfile.zone, func.count(SocialProfile.id).label("c"))
          .group_by(SocialProfile.zone)
          .order_by(desc("c")).all()
    )

    return {
        "total": total,
        "facebook": {
            "active":   count_where(SocialProfile.facebook_active_status,   "active"),
            "verified": count_where(SocialProfile.facebook_verified_status, "verified"),
            "followers": sum_col(SocialProfile.facebook_followers),
        },
        "twitter": {
            "active":   count_where(SocialProfile.twitter_active_status,   "active"),
            "verified": count_where(SocialProfile.twitter_verified_status, "verified"),
            "followers": sum_col(SocialProfile.twitter_followers),
        },
        "instagram": {
            "active":   count_where(SocialProfile.instagram_active_status,   "active"),
            "verified": count_where(SocialProfile.instagram_verified_status, "verified"),
            "followers": sum_col(SocialProfile.instagram_followers),
        },
        "by_designation": [{"label": d or "Unknown", "count": c} for d, c in by_designation],
        "by_zone":        [{"label": z or "Unknown", "count": c} for z, c in by_zone],
    }


# ── Analytics ─────────────────────────────────────────────────────────────────
@app.get("/api/analytics/platform-comparison")
async def platform_comparison(
    zone: Optional[str] = None,
    party_district: Optional[str] = None,
    constituency: Optional[str] = None,
    designation: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Average followers per platform with optional filters"""
    q = db.query(SocialProfile)
    q = _apply_filters(q, None, zone, party_district, constituency, designation, False, False)
    
    fb_avg = db.query(func.avg(SocialProfile.facebook_followers)).filter(
        SocialProfile.facebook_followers.isnot(None)
    ).select_from(q.subquery()).scalar() or 0
    
    tw_avg = db.query(func.avg(SocialProfile.twitter_followers)).filter(
        SocialProfile.twitter_followers.isnot(None)
    ).select_from(q.subquery()).scalar() or 0
    
    ig_avg = db.query(func.avg(SocialProfile.instagram_followers)).filter(
        SocialProfile.instagram_followers.isnot(None)
    ).select_from(q.subquery()).scalar() or 0
    
    return {
        "labels": ["Facebook", "Twitter", "Instagram"],
        "datasets": [{
            "label": "Avg Followers",
            "data": [int(fb_avg), int(tw_avg), int(ig_avg)],
            "backgroundColor": ["#1877F2", "#1DA1F2", "#E1306C"]
        }]
    }


@app.get("/api/analytics/top-profiles")
async def top_profiles(
    zone: Optional[str] = None,
    party_district: Optional[str] = None,
    constituency: Optional[str] = None,
    designation: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Top 15 profiles by total followers with optional filters"""
    q = db.query(
        SocialProfile.name,
        SocialProfile.zone,
        SocialProfile.facebook_followers,
        SocialProfile.twitter_followers,
        SocialProfile.instagram_followers
    )
    
    base_q = db.query(SocialProfile)
    base_q = _apply_filters(base_q, None, zone, party_district, constituency, designation, False, False)
    
    profiles = q.filter(SocialProfile.id.in_([p.id for p in base_q])).filter(
        (SocialProfile.facebook_followers.isnot(None)) |
        (SocialProfile.twitter_followers.isnot(None)) |
        (SocialProfile.instagram_followers.isnot(None))
    ).all()
    
    top = sorted(
        [{
            "name": p[0],
            "zone": p[1],
            "total": (p[2] or 0) + (p[3] or 0) + (p[4] or 0)
        } for p in profiles],
        key=lambda x: x["total"],
        reverse=True
    )[:15]
    
    return {
        "labels": [p["name"][:20] + "..." if len(p["name"]) > 20 else p["name"] for p in top],
        "datasets": [{
            "label": "Total Followers",
            "data": [p["total"] for p in top],
            "backgroundColor": "#36A2EB"
        }]
    }


@app.get("/api/analytics/active-status")
async def active_status_dist(
    zone: Optional[str] = None,
    party_district: Optional[str] = None,
    constituency: Optional[str] = None,
    designation: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Active status distribution across platforms with optional filters"""
    q = db.query(SocialProfile)
    q = _apply_filters(q, None, zone, party_district, constituency, designation, False, False)
    
    fb_active = q.filter(SocialProfile.facebook_active_status.ilike("active")).count()
    tw_active = q.filter(SocialProfile.twitter_active_status.ilike("active")).count()
    ig_active = q.filter(SocialProfile.instagram_active_status.ilike("active")).count()
    
    return {
        "labels": ["Facebook", "Twitter", "Instagram"],
        "datasets": [{
            "label": "Active Profiles",
            "data": [fb_active, tw_active, ig_active],
            "backgroundColor": ["#1877F2", "#1DA1F2", "#E1306C"]
        }]
    }


@app.get("/api/analytics/verified-status")
async def verified_status_dist(
    zone: Optional[str] = None,
    party_district: Optional[str] = None,
    constituency: Optional[str] = None,
    designation: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Verified status distribution across platforms with optional filters"""
    q = db.query(SocialProfile)
    q = _apply_filters(q, None, zone, party_district, constituency, designation, False, False)
    
    fb_verified = q.filter(SocialProfile.facebook_verified_status.ilike("verified")).count()
    tw_verified = q.filter(SocialProfile.twitter_verified_status.ilike("verified")).count()
    ig_verified = q.filter(SocialProfile.instagram_verified_status.ilike("verified")).count()
    
    return {
        "labels": ["Facebook", "Twitter", "Instagram"],
        "datasets": [{
            "label": "Verified Profiles",
            "data": [fb_verified, tw_verified, ig_verified],
            "backgroundColor": ["#1877F2", "#1DA1F2", "#E1306C"]
        }]
    }


@app.get("/api/analytics/zone-followers")
async def zone_followers(
    zone: Optional[str] = None,
    party_district: Optional[str] = None,
    constituency: Optional[str] = None,
    designation: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Total followers by zone with optional filters"""
    q = db.query(SocialProfile)
    q = _apply_filters(q, None, zone, party_district, constituency, designation, False, False)
    
    zones = q.with_entities(
        SocialProfile.zone,
        func.sum(SocialProfile.facebook_followers + SocialProfile.twitter_followers + SocialProfile.instagram_followers).label("total_followers")
    ).filter(
        (SocialProfile.facebook_followers.isnot(None)) |
        (SocialProfile.twitter_followers.isnot(None)) |
        (SocialProfile.instagram_followers.isnot(None))
    ).group_by(SocialProfile.zone).order_by(desc("total_followers")).limit(12).all()
    
    return {
        "labels": [z[0] or "Unknown" for z in zones],
        "datasets": [{
            "label": "Total Followers by Zone",
            "data": [int(z[1] or 0) for z in zones],
            "backgroundColor": "#FFCE56"
        }]
    }


@app.get("/api/analytics/designation-count")
async def designation_count(
    zone: Optional[str] = None,
    party_district: Optional[str] = None,
    constituency: Optional[str] = None,
    designation: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Profile count by designation with optional filters"""
    q = db.query(SocialProfile)
    q = _apply_filters(q, None, zone, party_district, constituency, designation, False, False)
    
    designations = q.with_entities(
        SocialProfile.designation,
        func.count(SocialProfile.id).label("count")
    ).group_by(SocialProfile.designation).order_by(desc("count")).limit(10).all()
    
    return {
        "labels": [d[0] or "Unknown" for d in designations],
        "datasets": [{
            "label": "Profiles by Designation",
            "data": [d[1] for d in designations],
            "backgroundColor": "#4BC0C0"
        }]
    }


# ── Filter options ─────────────────────────────────────────────────────────────
@app.get("/api/filter-options")
async def filter_options(db: Session = Depends(get_db)):
    def distinct(col):
        return sorted(filter(None, [
            r[0] for r in db.query(col).distinct().filter(col.isnot(None)).all()
        ]))
    return {
        "zones":           distinct(SocialProfile.zone),
        "party_districts": distinct(SocialProfile.party_district),
        "constituencies":  distinct(SocialProfile.constituency),
        "designations":    distinct(SocialProfile.designation),
    }


# ── CSV Export ─────────────────────────────────────────────────────────────────
EXPORT_FIELDS = [
    "id", "zone", "party_district", "constituency", "designation", "name",
    "whatsapp_number", "dob", "address", "email_id",
    "facebook_id", "facebook_followers", "facebook_active_status", "facebook_verified_status",
    "twitter_id",   "twitter_followers",  "twitter_active_status",  "twitter_verified_status",
    "instagram_id", "instagram_followers","instagram_active_status","instagram_verified_status",
]

@app.get("/api/export/csv")
async def export_csv(
    search:         Optional[str] = None,
    zone:           Optional[str] = None,
    party_district: Optional[str] = None,
    constituency:   Optional[str] = None,
    designation:    Optional[str] = None,
    active_only:    bool = False,
    verified_only:  bool = False,
    db: Session = Depends(get_db),
):
    q = db.query(SocialProfile)
    q = _apply_filters(q, search, zone, party_district, constituency, designation,
                       active_only, verified_only)
    rows = q.order_by(SocialProfile.id).all()

    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=EXPORT_FIELDS)
    w.writeheader()
    for r in rows:
        w.writerow({f: getattr(r, f, None) for f in EXPORT_FIELDS})

    return StreamingResponse(
        io.BytesIO(buf.getvalue().encode("utf-8-sig")),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="export.csv"'},
    )


# ── Entrypoint ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
    )
