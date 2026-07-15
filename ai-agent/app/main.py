from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.routers import user, checks, ai_model

app = FastAPI(title="AI agent backend", version="1.0")
app.openapi_version = "3.0.3"
app.include_router(user.router)
app.include_router(checks.router)
app.include_router(ai_model.router)


def _post_process_openapi(schema: dict) -> dict:
    """Adjust OpenAPI schema so array file items render as file inputs in Swagger UI.

    Swagger UI looks for `format: "binary"` to render a file chooser. FastAPI
    emits `contentMediaType: application/octet-stream` for UploadFile items, but
    some Swagger UI versions don't show file pickers for array items unless the
    item schema has `format: binary`. This function sets that flag for any
    multipart/form-data body with a `files` array of file items.
    """
    comps = schema.get("components", {}).get("schemas", {})
    for name, comp in comps.items():
        props = comp.get("properties") or {}
        if "files" in props:
            items = props["files"].get("items") or {}
            # set format=binary so Swagger UI renders a file input
            if items.get("contentMediaType"):
                items.setdefault("format", "binary")
    return schema


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
    schema = _post_process_openapi(schema)
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/")
async def root():
    return {"message": "Welcome to AI - agent service"}
