"""Evaluation helpers. A real model run requires credentials and should be reported separately."""
from pathlib import Path
import json, csv, time

def evaluate_ground_truth(path="data/ground_truth/ground_truth.json", out="reports"):
    data=json.loads(Path(path).read_text()); rows=[]
    for d in data["documents"]:
        for field, truth in d["fields"].items(): rows.append({"application_id":d["application_id"],"document_type":d["document_type"],"variant":"noisy" if d.get("noisy_path") else "clean","field":field,"truth":truth,"prediction":"NOT_RUN","correct":None})
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    with (out/"metrics.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    summary=["# DhuriDocs evaluation report","","**Status: baseline dataset inventory only. No LLM extraction has been run.** Do not read NOT_RUN values as model performance.","",f"- Applications: {data['applications']}",f"- Documents: {len(data['documents'])}",f"- Field labels: {len(rows)}","- Accuracy: not measured","- Inconsistency precision / recall / false positives: not measured","- Processing time and LLM cost: not measured","","## Worst failures","","No extraction run exists yet; worst failures cannot be ranked. The harness is ready to populate from recorded predictions."]
    (out/"evaluation_report.md").write_text("\n".join(summary)+"\n")
    return {"documents":len(data["documents"]),"fields":len(rows),"status":"inventory_only"}
if __name__=="__main__": print(evaluate_ground_truth())
