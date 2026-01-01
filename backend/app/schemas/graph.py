from pydantic import BaseModel, Field, ConfigDict

class GraphNode(BaseModel):
    id: str
    label: str
    group: str

class GraphEdge(BaseModel):
    # Allow population by field name OR alias during validation
    model_config = ConfigDict(populate_by_name=True)

    # Accept/emit JSON key "from"
    from_: str = Field(alias="from")
    to: str
    label: str | None = None

class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    filings_matched: int

class PingResponse(BaseModel):
    status: str
    count: int | None = None
    next: str | None = None
    sample_keys: list[str]

