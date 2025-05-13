# agent/cad_integration.py

import os
from dotenv import load_dotenv
from onshape_client.client import Client
from onshape_client.oas.models.bt_app_element_params import BTAppElementParams

load_dotenv()

# ─── Configuration from .env ────────────────────────────────
BASE_URL     = os.getenv("CAD_API_BASE", "https://cad.onshape.com")
ACCESS_KEY   = os.getenv("ONSHAPE_ACCESS_KEY")
SECRET_KEY   = os.getenv("ONSHAPE_SECRET_KEY")
DOCUMENT_ID  = os.getenv("ONSHAPE_DOCUMENT_ID")
WORKSPACE_ID = os.getenv("ONSHAPE_WORKSPACE_ID")

for var in ("ACCESS_KEY", "SECRET_KEY", "DOCUMENT_ID", "WORKSPACE_ID"):
    if not locals()[var]:
        raise ValueError(f"Missing {var} in .env")

# ─── Initialize Onshape client ───────────────────────────────
client = Client(
    configuration={
        "base_url": BASE_URL,
        "access_key": ACCESS_KEY,
        "secret_key": SECRET_KEY
    }
)

def create_parametric_model(params: dict) -> str:
    """
    Creates a FeatureStudio element in Onshape and returns its URL.
    `params` should include keys like 'stroke' and 'bore' (in mm).
    """
    stroke = params.get("stroke", 80)
    bore   = params.get("bore", 50)

    # ─── Build pure FeatureScript code ──────────────────────────
    fs_code = f'''
annotation @{{
  "Feature Type Name": "Crankshaft"
}}
export const crankshaft = defineFeature(function(context is Context, id is IdHandle, definition is map)
{{
    // parameters in mm
    const stroke = {stroke} * millimeter;
    const bore   = {bore} * millimeter;
    const rThrow = stroke / 2;

    // Draw main journal circle
    opCircle(context, id + "mainJournal", {{
      "center": vector(0, 0) * millimeter,
      "radius": (bore * 0.6) / 2
    }});

    // Draw crank pin circle offset by throw radius
    opCircle(context, id + "crankPin", {{
      "center": vector(rThrow, 0) * millimeter,
      "radius": (bore * 0.5) / 2
    }});

    // Web sketch (simple rectangle with fillets)
    const webThickness = 20 * millimeter;
    const webHeight    = bore + 2 * webThickness;
    opRectangle(context, id + "webSketch", {{
      "plane": plane(vector(0,0,0), vector(0,0,1)),
      "corner1": vector(-webThickness/2, -webHeight/2) * millimeter,
      "corner2": vector(webThickness/2,  webHeight/2) * millimeter
    }});
    opFillet(context, id + "webFillet", {{
      "entities": qAllSolidEdges(context, {{ "model": qCreatedBy(context, id + "webSketch", EntityType.EDGE) }}),
      "radius": 3 * millimeter
    }});
}});
'''

    # ─── Create the FeatureStudio element via the Features API ──
    create_elem = BTAppElementParams(feature_studio_element=fs_code)
    resp = client.features_api.create_feature_studio_element(
        DOCUMENT_ID,
        WORKSPACE_ID,
        bt_app_element_params=create_elem
    )
    element_id = resp.id

    # ─── Return the shareable URL ───────────────────────────────
    return f"{BASE_URL}/documents/{DOCUMENT_ID}/w/{WORKSPACE_ID}/e/{element_id}"
