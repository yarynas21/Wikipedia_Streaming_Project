from fastapi import FastAPI, Query
from cassandra.cluster import Cluster
from datetime import datetime, timedelta, date
from typing import List, Dict
from pydantic_models.models import *
from collections import defaultdict

app = FastAPI()
cluster = Cluster(["cassandra"])
session = cluster.connect("wikipedia")

@app.get("/analytics/domain-stats", response_model=List[DomainStat])
def get_domain_stats():
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    time_end = now - timedelta(hours=1)
    time_start = time_end - timedelta(hours=6)

    results = []
    for i in range(6):
        start = time_start + timedelta(hours=i)
        end = start + timedelta(hours=1)

        rows = session.execute(
            "SELECT domain, page_count FROM domain_stats_by_hour WHERE time_start = %s",
            (start,)
        )
        stats = [DomainStatEntry(domain=row.domain, page_count=row.page_count) for row in rows]
        results.append(DomainStat(
            time_start=start.isoformat(),
            time_end=end.isoformat(),
            statistics=stats
        ))
    return results


@app.get("/analytics/bot-stats", response_model=List[BotStat])
def get_bot_stats():
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    time_end = now - timedelta(hours=1)
    time_start = time_end - timedelta(hours=6)

    results = []
    for i in range(6):
        start = time_start + timedelta(hours=i)
        end = start + timedelta(hours=1)

        rows = session.execute(
            "SELECT domain, created_by_bots FROM bot_stats_last_6h WHERE time_start = %s",
            (start,)
        )
        stats = [BotStatEntry(domain=row.domain, created_by_bots=row.created_by_bots) for row in rows]
        results.append(BotStat(
            time_start=start.isoformat(),
            time_end=end.isoformat(),
            statistics=stats
        ))
    return results


@app.get("/analytics/top-users", response_model=List[TopUsersStat])
def get_top_users():
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    time_end = now - timedelta(hours=1)
    time_start = time_end - timedelta(hours=6)

    results = []
    for i in range(6):
        start = time_start + timedelta(hours=i)
        end = start + timedelta(hours=1)

        rows = session.execute(
            "SELECT user_id, user_name, page_count, page_titles FROM top_users_last_6h WHERE time_start = %s",
            (start,)
        )
        users = [TopUserEntry(
            user_id=row.user_id,
            user_name=row.user_name,
            page_count=row.page_count,
            page_titles=row.page_titles
        ) for row in rows]

        results.append(TopUsersStat(
            time_start=start.isoformat(),
            time_end=end.isoformat(),
            users=users
        ))
    return results

@app.get("/domains", response_model=DomainResponse)
def get_domains():
    rows = session.execute("SELECT domain FROM domains_created")
    domain_set = {row.domain for row in rows if row.domain}
    domains = sorted(domain_set)
    return DomainResponse(domains=domains)

@app.get("/pages/by-user", response_model=List[PageByUser])
def get_pages_by_user(user_id: int):
    rows = session.execute("SELECT page_id, dt FROM pages_by_user WHERE user_id = %s", (user_id,))
    return [PageByUser(page_id=r.page_id, dt=r.dt.isoformat()) for r in rows]

@app.get("/domain/count", response_model=DomainCount)
def get_page_count_by_domain(domain: str):
    row = session.execute("SELECT page_count FROM domain_page_counts WHERE domain = %s", (domain,)).one()
    count = row.page_count if row else 0
    return DomainCount(domain=domain, page_count=count)


@app.get("/page/by-id", response_model=PageInfo)
def get_page_by_id(page_id: int):
    row = session.execute("SELECT * FROM pages_by_id WHERE page_id = %s", (page_id,)).one()
    if not row:
        return PageInfo(page_id=page_id, page_title="Not found", domain="", dt="N/A")
    return PageInfo(
        page_id=row.page_id,
        page_title=row.page_title,
        domain=row.domain,
        dt=row.dt.isoformat()
    )

@app.get("/users/activity", response_model=List[UserActivity])
def get_user_activity(start_date: date, end_date: date):
    counts = defaultdict(int)
    current = start_date
    while current <= end_date:
        rows = session.execute("SELECT user_id, page_count FROM user_page_counts_by_date WHERE dt = %s", (current,))
        for r in rows:
            counts[r.user_id] += r.page_count
        current = current.fromordinal(current.toordinal() + 1)

    result = []
    for user_id, count in counts.items():
        row = session.execute("SELECT user_name FROM users WHERE user_id = %s", (user_id,)).one()
        user_name = row.user_name if row else "Unknown"
        result.append(UserActivity(user_id=user_id, user_name=user_name, page_count=count))

    return sorted(result, key=lambda x: x.page_count, reverse=True)

