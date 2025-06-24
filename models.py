from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import date

class DrivingLicense(BaseModel):
    """Model for driving license data extraction"""
    name: str = Field(description="Full name of the license holder")
    date_of_birth: str = Field(description="Date of birth in YYYY-MM-DD format")
    license_number: str = Field(description="License number/ID")
    issuing_state: str = Field(description="State that issued the license")
    expiry_date: str = Field(description="Expiry date in YYYY-MM-DD format")

class ReceiptItem(BaseModel):
    """Model for individual items in a receipt"""
    name: str = Field(description="Name of the item")
    quantity: Union[int, float] = Field(description="Quantity purchased (can be decimal for items sold by weight)")
    price: float = Field(description="Price per item")

class ShopReceipt(BaseModel):
    """Model for shop receipt data extraction"""
    merchant_name: str = Field(description="Name of the merchant/store")
    total_amount: float = Field(description="Total amount of the purchase")
    date_of_purchase: str = Field(description="Date of purchase in YYYY-MM-DD format")
    items: List[ReceiptItem] = Field(description="List of items purchased")
    payment_method: str = Field(description="Payment method used")

class WorkExperience(BaseModel):
    """Model for work experience entries"""
    company: str = Field(description="Company name")
    role: str = Field(description="Job title/role")
    dates: str = Field(description="Employment period (e.g., '2020-2023' or 'Jan 2020 - Dec 2023')")

class Education(BaseModel):
    """Model for education entries"""
    institution: str = Field(description="Educational institution name")
    degree: str = Field(description="Degree obtained")
    graduation_year: Optional[Union[int, str]] = Field(description="Year of graduation or date range", default=None)

class Resume(BaseModel):
    """Model for resume/CV data extraction"""
    full_name: str = Field(description="Full name of the person")
    email: str = Field(description="Email address")
    phone_number: str = Field(description="Phone number")
    skills: List[str] = Field(default_factory=list, description="List of skills")
    work_experience: List[WorkExperience] = Field(default_factory=list, description="List of work experiences")
    education: Optional[List[Education]] = Field(default_factory=list, description="List of educational background")

DocumentData = DrivingLicense | ShopReceipt | Resume 