#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from onshape_client.client import Client
# Correct import path for the CreateDocument model
from onshape_client.onshape_rest_api.models.bt_document_params import BTDocumentParams

# 1. Load your Onshape API keys from .env
load_dotenv()
ACCESS_KEY = os.getenv("ONSHAPE_ACCESS_KEY")
SECRET_KEY = os.getenv("ONSHAPE_SECRET_KEY")
if not ACCESS_KEY or not SECRET_KEY:
    raise ValueError("Please set ONSHAPE_ACCESS_KEY and ONSHAPE_SECRET_KEY in your .env")

# 2. Initialize the Onshape client
client = Client(configuration={
    "base_url": "https://cad.onshape.com",
    "access_key": ACCESS_KEY,
    "secret_key": SECRET_KEY
})

# 3. Create a fresh document named “AutoRAG Models”
print("Creating new Onshape document…")
doc_resp = client.documents_api.create_document(
    bt_document_params=BTDocumentParams(name="AutoRAG Models")
)
document_id = doc_resp.id
print(" Document ID:", document_id)

# 4. Fetch the list of workspaces in that document (the first one is the default)
ws_resp = client.documents_api.get_workspaces(document_id)
workspace_id = ws_resp.items[0].id
print(" Workspace ID:", workspace_id)

# 5. Print out the .env lines to add
print("\nAdd these to your .env:")
print(f"ONSHAPE_DOCUMENT_ID={document_id}")
print(f"ONSHAPE_WORKSPACE_ID={workspace_id}")
