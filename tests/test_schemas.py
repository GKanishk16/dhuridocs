import pytest
from pydantic import ValidationError
from src.extraction.schemas import Invoice, Extracted

def test_invoice_schema_parses_confidence_fields():
    data={"applicant_name":{"value":"Aarav Synthetic","confidence":.98},"dealer_name":{"value":"Demo Motors","confidence":.9},"gstin":{"value":"27ZZZDE1234Z1Z5","confidence":.9},"vehicle_make":{"value":"Tata","confidence":.9},"vehicle_model":{"value":"Nexon","confidence":.9},"variant":{"value":"SX","confidence":.8},"ex_showroom_price":{"value":100,"confidence":.9},"rto":{"value":10,"confidence":.9},"insurance":{"value":5,"confidence":.9},"accessories":{"value":2,"confidence":.9},"on_road_price":{"value":117,"confidence":.9},"requested_loan_amount":{"value":90,"confidence":.9}}
    assert Invoice.model_validate(data).document_type=="invoice"
def test_confidence_bounds():
    with pytest.raises(ValidationError): Extracted(value="x",confidence=1.2)
