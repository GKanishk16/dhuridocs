"""Transparent cross-document checks with thresholds centralized in YAML."""
from pathlib import Path
from datetime import date
import yaml
from rapidfuzz.fuzz import ratio

def load_rules(path="config/rules.yaml"):
    return yaml.safe_load(Path(path).read_text())

def val(doc, key, default=None):
    x=doc.get(key, default)
    return x.get("value", default) if isinstance(x,dict) else x

def validate_application(docs: dict, requested_loan_amount: float | None = None, rules_path="config/rules.yaml", today: date | None=None) -> list[dict]:
    """Return checks with pass/flag/fail and human-readable evidence."""
    rules=load_rules(rules_path); today=today or date.today(); out=[]
    def add(name,status,explanation): out.append({"check":name,"status":status,"explanation":explanation})
    names=[val(d,"applicant_name") for d in docs.values() if val(d,"applicant_name")]
    score=min((ratio(str(names[0]),str(n)) for n in names[1:]), default=100) if names else 0
    add("Applicant name consistency", "pass" if score>=rules["name_match_threshold"] else "fail", f"Lowest pairwise fuzzy match: {score:.1f} (threshold {rules['name_match_threshold']}).")
    invoice=docs.get("invoice",{}); price=val(invoice,"on_road_price"); loan=requested_loan_amount or val(invoice,"requested_loan_amount")
    if price and loan:
        ltv=float(loan)/float(price); add("Loan-to-value", "pass" if ltv<=rules["ltv_cap"] else "flag", f"LTV {ltv:.1%}; cap {rules['ltv_cap']:.0%}.")
    else: add("Loan-to-value","flag","Invoice price or requested loan amount is missing.")
    slip=docs.get("salary_slip",{}); bank=docs.get("bank_statement",{}); net=val(slip,"net_pay"); credits=bank.get("salary_credits",[])
    credits=[val({"x":c},"x") for c in credits]
    if net and credits:
        avg=sum(float(c) for c in credits)/len(credits); delta=abs(avg-float(net))/float(net)
        add("Salary vs bank credits","pass" if delta<=rules["salary_credit_tolerance_pct"] else "fail",f"Slip net ₹{float(net):,.0f}; average bank credit ₹{avg:,.0f} ({delta:.1%} difference).")
    else: add("Salary vs bank credits","flag","Salary net pay or bank salary credits are missing.")
    ins=docs.get("insurance",{}); end=val(ins,"end_date"); idv=val(ins,"idv")
    if end:
        try: valid=date.fromisoformat(str(end))>=today
        except ValueError: valid=False
        add("Insurance validity","pass" if valid else "fail",f"Policy end date {end}; evaluation date {today.isoformat()}.")
    else: add("Insurance validity","flag","Policy end date is missing.")
    if idv and price:
        delta=abs(float(idv)-float(price))/float(price)
        add("Insurance IDV vs invoice","pass" if delta<=rules["idv_tolerance_pct"] else "flag",f"IDV differs from on-road price by {delta:.1%}; tolerance {rules['idv_tolerance_pct']:.0%}.")
    else: add("Insurance IDV vs invoice","flag","IDV or invoice price is missing.")
    emis=bank.get("emi_debits",[]); emis=[val({"x":e},"x") for e in emis]
    if net and emis:
        foir=sum(float(e) for e in emis)/float(net); add("Existing FOIR","pass" if foir<=rules["foir_cap"] else "flag",f"Estimated existing EMI/net income: {foir:.1%}; cap {rules['foir_cap']:.0%}.")
    else: add("Existing FOIR","flag","Bank EMI debits or net income are missing.")
    return out

def recommendation(checks):
    failing=[c for c in checks if c["status"]=="fail"]
    flags=[c for c in checks if c["status"]=="flag"]
    if failing: return {"decision":"Reject","reasons":[c["explanation"] for c in failing]}
    if flags: return {"decision":"Manual review","reasons":[c["explanation"] for c in flags]}
    return {"decision":"Auto-approve docs","reasons":["All configured document checks passed. Credit underwriting is out of scope."]}
