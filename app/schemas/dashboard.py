from pydantic import BaseModel

class DashboardResponse(BaseModel):
    message: str
    # Add other fields you want to return in the dashboard response if needed
