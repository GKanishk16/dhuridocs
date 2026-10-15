"""DhuriDocs interactive prototype."""
from pathlib import Path
import json, streamlit as st
from src.validation.engine import validate_application, recommendation
from src.extraction.pipeline import extract_document

st.set_page_config(page_title="DhuriDocs",page_icon="📄",layout="wide")
st.title("DhuriDocs")
st.caption("Synthetic vehicle-loan document intelligence prototype · Kanishk Gupta")
tabs=st.tabs(["Application review","Evaluation","Business case"])
with tabs[0]:
    choice=st.radio("Document source",["Sample application","Upload documents"],horizontal=True)
    docs={}
    if choice=="Sample application":
        ids=sorted(p.name for p in Path("data/applications").glob("APP-*"))
        if ids:
            app=st.selectbox("Sample",ids); folder=Path("data/applications")/app
            if st.button("Extract sample"):
                for path in folder.glob("*.pdf"):
                    typ=path.stem.replace("_noisy","")
                    if typ in {"invoice","salary_slip","bank_statement","insurance","pan"}:
                        docs[typ]=extract_document(path,typ)
                st.session_state["docs"]=docs
        else: st.info("Generate samples with python -m src.generator.generate")
    else:
        uploads=st.file_uploader("Upload PDF or image documents",type=["pdf","png","jpg","jpeg"],accept_multiple_files=True)
        mapping={"invoice":"Proforma invoice","salary_slip":"Salary slip","bank_statement":"Bank statement","insurance":"Insurance policy","pan":"PAN card"}
        for u in uploads or []:
            typ=st.selectbox(f"Document type for {u.name}",list(mapping),format_func=lambda x:mapping[x],key=u.name)
            if st.button(f"Extract {u.name}",key="extract"+u.name):
                tmp=Path(".upload_"+u.name); tmp.write_bytes(u.getvalue()); res=extract_document(tmp,typ); st.session_state.setdefault("docs",{})[typ]=res
    docs=st.session_state.get("docs",docs)
    if docs:
        st.subheader("Extracted fields")
        for typ,doc in docs.items():
            with st.expander(typ.replace("_"," ").title(),expanded=True):
                for k,v in doc.items():
                    if isinstance(v,dict) and "confidence" in v:
                        conf=v["confidence"]; label=f"⚠️ Low confidence · {conf:.0%}" if conf<.7 else f"Confidence {conf:.0%}"
                        st.write(f"**{k}**: {v.get('value')} — {label}")
        checks=validate_application(docs)
        st.subheader("Cross-document checks")
        for c in checks: st.write(f"**{c['status'].upper()} · {c['check']}** — {c['explanation']}")
        rec=recommendation(checks); st.info(f"Loan officer view: **{rec['decision']}**\n\n"+"\n".join("• "+r for r in rec["reasons"]))
        st.caption("Recommendation concerns document checks only; it is not a credit decision.")
with tabs[1]:
    report=Path("reports/evaluation_report.md")
    st.markdown(report.read_text() if report.exists() else "Generate the corpus and run `python -m src.evaluation.run`.")
    metrics=Path("reports/metrics.csv")
    if metrics.exists(): st.dataframe(__import__("pandas").read_csv(metrics))
with tabs[2]:
    import yaml
    bc=yaml.safe_load(Path("config/business_case.yaml").read_text())
    st.warning("Placeholder assumptions only; validate all inputs before using the estimate.")
    mins=st.number_input("Manual minutes/application",value=float(bc["manual_minutes_per_application"]))
    cost=st.number_input("Officer cost/hour (₹)",value=float(bc["loan_officer_cost_per_hour_inr"]))
    volume=st.number_input("Monthly applications",value=int(bc["monthly_application_volume"]))
    saved_minutes=mins*volume
    st.metric("Potential hours saved / month",f"{saved_minutes/60:,.0f}")
    st.metric("Potential officer time value / month",f"₹{saved_minutes/60*cost:,.0f}")
    st.caption("Upper-bound scenario assumes full manual effort removed; evaluation has not measured achievable automation rate.")
st.divider(); st.caption("DhuriDocs · Prototype by Kanishk Gupta · Synthetic data only")
