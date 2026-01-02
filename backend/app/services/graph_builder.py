from __future__ import annotations

def node_id(group: str, name: str) -> str:
    return f"{group}:{name}"

def _shorten(name: str, max_len: int = 28) -> str:
    name = (name or "").strip()
    return name if len(name) <= max_len else name[: max_len - 1] + "…"

def build_graph_from_filings(filings: list[dict], include_lobbyists: bool) -> dict:
    nodes: dict[str, dict] = {}
    node_degree: dict[str, int] = {}

    # Aggregate edges by (src, dst, relation)
    # Each record: {"from":..., "to":..., "label":..., "count":...}
    edge_agg: dict[tuple[str, str, str], dict] = {}

    def upsert_node(group: str, name: str) -> str:
        name = (name or "").strip()
        nid = node_id(group, name)
        if nid not in nodes:
            nodes[nid] = {
                "id": nid,
                "label": _shorten(name),
                "title": name,  # hover shows full name
                "group": group,
            }
        return nid

    def add_edge(src_id: str, dst_id: str, relation: str):
        key = (src_id, dst_id, relation)
        rec = edge_agg.get(key)
        if rec is None:
            rec = {
                "from": src_id,
                "to": dst_id,
                "label": relation,
                "count": 0,
            }
            edge_agg[key] = rec

        rec["count"] += 1

        node_degree[src_id] = node_degree.get(src_id, 0) + 1
        node_degree[dst_id] = node_degree.get(dst_id, 0) + 1

    for filing in filings:
        client_name = ((filing.get("client") or {}).get("name") or "").strip()
        registrant_name = ((filing.get("registrant") or {}).get("name") or "").strip()

        client_id = reg_id = None
        if client_name:
            client_id = upsert_node("client", client_name)
        if registrant_name:
            reg_id = upsert_node("registrant", registrant_name)

        if client_id and reg_id:
            add_edge(
                src_id=reg_id,
                dst_id=client_id,
                relation="represents",
            )

        if include_lobbyists and reg_id:
            for lob in (filing.get("lobbyists") or []):
                lob_name = ((lob or {}).get("name") or "").strip()
                if not lob_name:
                    continue
                lob_id = upsert_node("lobbyist", lob_name)
                add_edge(
                    src_id=reg_id,
                    dst_id=lob_id,
                    relation="employs",
                )

    # Node sizing: based on degree
    for nid, n in nodes.items():
        d = node_degree.get(nid, 0)
        n["value"] = max(1, d)

    # Edge sizing: based on filings count
    edges: list[dict] = []
    for rec in edge_agg.values():
        cnt = int(rec["count"])

        # vis-network edge thickness uses `value`.
        value = max(1.0, float(cnt))

        edges.append({
            "from": rec["from"],
            "to": rec["to"],
            "label": rec["label"],
            "value": value,
            "count": cnt,
            "title": f"{rec['label']} • {cnt} filings",
        })

    return {
        "nodes": list(nodes.values()),
        "edges": edges,
        "filings_matched": len(filings),
    }
