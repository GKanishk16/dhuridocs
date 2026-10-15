"""Provider-configurable vision extraction with one schema-repair retry."""
from __future__ import annotations
import base64, json, logging, os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import ValidationError
from .schemas import SCHEMAS

log = logging.getLogger(__name__)

def _image_data(path: Path) -> tuple[list[str], str]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        # Rasterize every page so scanned PDFs and visual layout reach the vision model.
        import fitz
        images=[]
        with fitz.open(path) as pdf:
            for page in pdf:
                pix=page.get_pixmap(matrix=fitz.Matrix(1.5,1.5), alpha=False)
                images.append(base64.b64encode(pix.tobytes("png")).decode())
        return images, "image"
    return [base64.b64encode(path.read_bytes()).decode()], suffix.lstrip(".")

def _call_model(path: Path, doc_type: str, repair: str = "") -> dict:
    load_dotenv()
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    schema = SCHEMAS[doc_type]
    payloads, kind = _image_data(path)
    prompt = (f"Extract only facts visible in this {doc_type} document. Return JSON matching this schema: "
              f"{json.dumps(schema.model_json_schema())}. Each field value must be {{'value': ..., 'confidence': number 0..1}}. "
              "Never infer missing values; use null with confidence 0. " + repair)
    if provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        content = [{"type":"text", "text":prompt}]
        if kind in {"png", "jpg", "jpeg", "webp", "image"}:
            media_type="image/jpeg" if path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
            content[0:0]=[{"type":"image","source":{"type":"base64","media_type":media_type,"data":payload}} for payload in payloads]
        else: content[0:0]=[{"type":"text","text":"Document text:\n"+payloads[0]}]
        response = client.messages.create(model=os.getenv("ANTHROPIC_MODEL","claude-3-5-sonnet-latest"), max_tokens=2500, messages=[{"role":"user","content":content}])
        text = response.content[0].text
    else:
        from openai import OpenAI
        content = [{"type":"text","text":prompt}]
        if kind in {"png", "jpg", "jpeg", "webp", "image"}:
            media_type="jpeg" if path.suffix.lower() in {".jpg", ".jpeg"} else "png"
            content[0:0]=[{"type":"image_url","image_url":{"url":f"data:image/{media_type};base64,{payload}"}} for payload in payloads]
        else: content[0:0]=[{"type":"text","text":"Document text:\n"+payloads[0]}]
        response = OpenAI().chat.completions.create(model=os.getenv("OPENAI_MODEL","gpt-4o-mini"), messages=[{"role":"user","content":content}], response_format={"type":"json_object"})
        text = response.choices[0].message.content
    return json.loads(text)

def extract_document(path: str | Path, doc_type: str) -> dict:
    """Extract and validate; retry once after schema errors, then return failure metadata."""
    path = Path(path); schema = SCHEMAS[doc_type]
    for attempt in range(2):
        try:
            raw = _call_model(path, doc_type, "Previous output failed schema validation. Fix it: " if attempt else "")
            return schema.model_validate(raw).model_dump()
        except (ValidationError, ValueError, KeyError) as exc:
            log.warning("Extraction validation failure for %s attempt %d: %s", path, attempt + 1, exc)
            if attempt: return {"document_type":doc_type,"error":str(exc)}
        except Exception as exc:
            log.exception("Extraction provider failure for %s", path)
            return {"document_type":doc_type,"error":str(exc)}
    return {"document_type":doc_type,"error":"unknown failure"}
