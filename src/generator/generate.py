"""Create obviously synthetic documents and a traceable ground truth corpus."""
from pathlib import Path
import json, random, argparse
from datetime import date, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PIL import Image, ImageFilter

NAMES=["Aarav Synthetic","Diya Sample","Ishaan Demo","Meera Fiction","Kabir Placeholder","Anaya Test","Reyansh Example","Saanvi Mock","Vivaan Dummy","Aditi Sandbox"]
VEHICLES=[("Maruti Suzuki","Brezza","ZXi"),("Hyundai","Venue","SX"),("Tata Motors","Nexon","Fearless"),("Mahindra","XUV 3XO","AX5")]
def emit_pdf(path,title,fields):
    path.parent.mkdir(parents=True,exist_ok=True); c=canvas.Canvas(str(path),pagesize=A4); c.setFont("Helvetica-Bold",16); c.drawString(48,790,"SYNTHETIC SAMPLE — NOT A REAL DOCUMENT"); c.setFont("Helvetica-Bold",13); c.drawString(48,755,title); c.setFont("Helvetica",11)
    y=725
    for k,v in fields.items():
        c.drawString(48,y,f"{k.replace('_',' ').title()}: {v}"); y-=24
        if y<60: c.showPage(); y=790
    c.save()
def main(count=30, seed=16, root=Path("data")):
    random.seed(seed); root=Path(root); gt=[]; docsroot=root/"applications"
    for i in range(1,count+1):
        app=f"APP-{i:03d}"; name=random.choice(NAMES); make,model,variant=random.choice(VEHICLES); ex=random.randrange(900000,1700000,10000); rto=ex*.10; ins=ex*.035; acc=ex*.02; price=round(ex+rto+ins+acc); loan=round(price*.85,-3); gross=random.randrange(70000,150001,1000); deductions=round(gross*.15); net=gross-deductions; month="2026-08"; start=date(2025,1,1); expiry=date(2027,1,1)
        injected=[]
        if i%3==0:
            name2=random.choice([x for x in NAMES if x!=name]); injected.append("applicant_name_mismatch")
        else: name2=name
        if i%3==1: injected.append("salary_credit_mismatch"); banknet=net+random.randrange(7000,14000,1000)
        else: banknet=net
        idv=round(price*.72) if i%5==0 else round(price*.93)
        if idv/price < .8: injected.append("insurance_idv_mismatch")
        if i%7==0: expiry=date(2025,6,1); injected.append("expired_insurance")
        d=docsroot/app; d.mkdir(parents=True,exist_ok=True)
        records={
          "invoice":{"applicant_name":name,"dealer_name":"Demo Motors India Pvt Ltd","gstin":"27ZZZDE1234Z1Z5","vehicle_make":make,"vehicle_model":model,"variant":variant,"ex_showroom_price":ex,"rto":rto,"insurance":ins,"accessories":acc,"on_road_price":price,"requested_loan_amount":loan},
          "salary_slip":{"applicant_name":name,"employer":"Example Mobility Services","gross_pay":gross,"deductions":deductions,"net_pay":net,"month":month},
          "bank_statement":{"applicant_name":name2,"account_id":f"SYNTH-AC-{i:04d}","period_start":"2026-06-01","period_end":"2026-08-31","salary_credits":[banknet]*3,"emi_debits":[8500,8500,8500]},
          "insurance":{"applicant_name":name,"insurer":"Sample General Insurance","policy_id":f"SYNTH-POL-{i:04d}","idv":idv,"start_date":"2026-01-01","end_date":expiry.isoformat(),"vehicle_make":make,"vehicle_model":model,"registration":f"XX00ZZ{i:04d}"},
          "pan":{"applicant_name":name,"pan_number":f"ZZ{chr(65+i%26)}DE{1000+i:04d}Z"}}
        clean_variants=[]
        for typ,fields in records.items():
            path=d/f"{typ}.pdf"; emit_pdf(path,typ.replace('_',' ').upper(),fields)
            noisy=(i+len(typ))%4==0
            if noisy:
                im=Image.new("RGB",(900,1200),"white"); from PIL import ImageDraw
                draw=ImageDraw.Draw(im); draw.text((40,40),"SYNTHETIC SAMPLE — " + typ,fill="black"); y=100
                for k,v in fields.items(): draw.text((40,y),f"{k}: {v}",fill="black"); y+=36
                im=im.rotate(random.uniform(-2,2),resample=Image.Resampling.BICUBIC,expand=False).filter(ImageFilter.GaussianBlur(.45)).resize((600,800)); img=d/f"{typ}_noisy.png"; im.save(img)
                clean_variants.append(str(img))
            gt.append({"application_id":app,"document_type":typ,"path":str(path),"noisy_path":clean_variants[-1] if clean_variants else None,"fields":fields,"inconsistencies":injected if typ=="invoice" else []})
    (root/"ground_truth").mkdir(parents=True,exist_ok=True)
    (root/"ground_truth"/"ground_truth.json").write_text(json.dumps({"seed":seed,"applications":count,"documents":gt},indent=2))
    (root/"ground_truth"/"inconsistencies.json").write_text(json.dumps([{"application_id":f"APP-{i:03d}","inconsistencies":sorted({x for row in gt if row["application_id"]==f"APP-{i:03d}" for x in row["inconsistencies"]})} for i in range(1,count+1)],indent=2))
    print(f"Generated {count} applications / {len(gt)} PDFs under {docsroot}")
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--count",type=int,default=30); ap.add_argument("--seed",type=int,default=16); ap.add_argument("--root",default="data"); a=ap.parse_args(); main(a.count,a.seed,Path(a.root))
