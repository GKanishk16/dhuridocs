"""Typed extraction schemas; each extracted field carries its own confidence."""
from datetime import date
from pydantic import BaseModel, Field
from typing import Optional

class Extracted(BaseModel):
    value: object | None = None
    confidence: float = Field(ge=0, le=1)

class DocumentSchema(BaseModel):
    document_type: str
    applicant_name: Extracted

class Invoice(DocumentSchema):
    document_type: str = "invoice"
    dealer_name: Extracted
    gstin: Extracted
    vehicle_make: Extracted
    vehicle_model: Extracted
    variant: Extracted
    ex_showroom_price: Extracted
    rto: Extracted
    insurance: Extracted
    accessories: Extracted
    on_road_price: Extracted
    requested_loan_amount: Extracted

class SalarySlip(DocumentSchema):
    document_type: str = "salary_slip"
    employer: Extracted
    gross_pay: Extracted
    deductions: Extracted
    net_pay: Extracted
    month: Extracted

class BankStatement(DocumentSchema):
    document_type: str = "bank_statement"
    account_id: Extracted
    period_start: Extracted
    period_end: Extracted
    salary_credits: list[Extracted]
    emi_debits: list[Extracted]

class InsurancePolicy(DocumentSchema):
    document_type: str = "insurance"
    insurer: Extracted
    policy_id: Extracted
    idv: Extracted
    start_date: Extracted
    end_date: Extracted
    vehicle_make: Extracted
    vehicle_model: Extracted
    registration: Extracted

class PanCard(DocumentSchema):
    document_type: str = "pan"
    pan_number: Extracted

SCHEMAS = {"invoice": Invoice, "salary_slip": SalarySlip, "bank_statement": BankStatement, "insurance": InsurancePolicy, "pan": PanCard}
