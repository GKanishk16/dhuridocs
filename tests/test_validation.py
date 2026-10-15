from datetime import date
from src.validation.engine import validate_application, recommendation

def wrapped(v, confidence=.99): return {"value":v,"confidence":confidence}
def test_flags_expired_and_name_mismatch():
    docs={"invoice":{"applicant_name":wrapped("Aarav Synthetic"),"on_road_price":wrapped(1000000),"requested_loan_amount":wrapped(950000)},"insurance":{"applicant_name":wrapped("Different Name"),"end_date":wrapped("2020-01-01"),"idv":wrapped(500000)},"salary_slip":{"applicant_name":wrapped("Aarav Synthetic"),"net_pay":wrapped(50000)},"bank_statement":{"applicant_name":wrapped("Aarav Synthetic"),"salary_credits":[wrapped(50000)],"emi_debits":[wrapped(10000)]}}
    checks=validate_application(docs,today=date(2026,1,1))
    assert next(c for c in checks if c["check"]=="Insurance validity")["status"]=="fail"
    assert recommendation(checks)["decision"]=="Reject"
def test_clean_checks_pass():
    docs={"invoice":{"applicant_name":wrapped("Aarav Synthetic"),"on_road_price":wrapped(1000000),"requested_loan_amount":wrapped(800000)},"insurance":{"applicant_name":wrapped("Aarav Synthetic"),"end_date":wrapped("2027-01-01"),"idv":wrapped(950000)},"salary_slip":{"applicant_name":wrapped("Aarav Synthetic"),"net_pay":wrapped(50000)},"bank_statement":{"applicant_name":wrapped("Aarav Synthetic"),"salary_credits":[wrapped(50000)]*3,"emi_debits":[wrapped(10000)]}}
    assert all(c["status"]=="pass" for c in validate_application(docs,today=date(2026,1,1)))
