from dataclasses import dataclass

@dataclass
class DbRecord:
    user_name: str 
    response: str 
    job_id: str
    role: str
    session_id: str

@dataclass
class ResponseResult:
    response: str
    response_num: int