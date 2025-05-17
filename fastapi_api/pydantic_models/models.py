from pydantic import BaseModel
from typing import List, Optional

class DomainResponse(BaseModel):
    domains: List[str]

class PageByUser(BaseModel):
    page_id: int
    dt: str

class DomainCount(BaseModel):
    domain: str
    page_count: int

class PageInfo(BaseModel):
    page_id: int
    page_title: str
    domain: str
    dt: str 

class UserActivity(BaseModel):
    user_id: int
    user_name: str
    page_count: int
    
class DomainResponse(BaseModel):
    domains: List[str]

class PageByUser(BaseModel):
    page_id: int
    dt: str

class DomainCount(BaseModel):
    domain: str
    page_count: int

class PageInfo(BaseModel):
    page_id: int
    page_title: str
    domain: str
    dt: str

class UserActivity(BaseModel):
    user_id: int
    user_name: str
    page_count: int

class DomainStatEntry(BaseModel):
    domain: str
    page_count: int

class DomainStat(BaseModel):
    time_start: str
    time_end: str
    statistics: List[DomainStatEntry]

class BotStatEntry(BaseModel):
    domain: str
    created_by_bots: int

class BotStat(BaseModel):
    time_start: str
    time_end: str
    statistics: List[BotStatEntry]

class TopUserEntry(BaseModel):
    user_id: int
    user_name: str
    page_count: int
    page_titles: List[str]

class TopUsersStat(BaseModel):
    time_start: str
    time_end: str
    users: List[TopUserEntry]
