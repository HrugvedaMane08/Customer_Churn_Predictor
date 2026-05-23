from pydantic import BaseModel, Field

class ChurnInputSchema(BaseModel):
    """
    Pydantic schema enforcing strict validation on incoming API requests.
    Validates data types, restricts limits (e.g. non-negative charges), and
    provides clear documentation examples.
    """
    tenure: int = Field(
        ..., 
        description="Number of months the customer has been with the company", 
        ge=0, 
        example=12
    )
    MonthlyCharges: float = Field(
        ..., 
        description="Monthly bill amount charged to the customer", 
        ge=0.0, 
        example=70.5
    )
    TotalCharges: float = Field(
        ..., 
        description="Cumulative charges since contract start date", 
        ge=0.0, 
        example=846.0
    )
    Gender: str = Field(
        ..., 
        description="Customer gender (Male or Female)", 
        example="Male"
    )
    Contract: str = Field(
        ..., 
        description="Contract commitment type (Month-to-month, One year, Two year)", 
        example="Month-to-month"
    )
