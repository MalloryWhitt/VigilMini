from __future__ import annotations

def node_id(group: str, name: str) -> str:
    return f"{group}:{name}"

def _shorten(name: str, max_len: int = 28) -> str:
    name = (name or "").strip()
    return name if len(name) <= max_len else name[: max_len - 1] + "…"

def _parse_amount(value) -> float:
    """
    Attempt to parse reported amount from LDA payload.
    Handles float/int, numeric strings, and strings with commas/$.
    Returns 0.0 if missing/unparseable.
    """
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        s = value.strip().replace("$", "").replace(",", "")
        if not s:
            return 0.0
        try:
            return float(s)
        except ValueError:
            return 0.0
    return 0.0

def _fmt_usd(x: float) -> str:
    # Simple USD formatting without locale dependency
    return f"${x:,.0f}"

def build_graph_from_filings(filings: list[dict], include_lobbyists: bool) -> dict:
    nodes: dict[str, dict] = {}
    node_degree: dict[str, int] = {}

    # Aggregate edges by (src, dst, relation)
    # Each record: {"from":..., "to":..., "label":..., "count":..., "amount":...}
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

    def add_edge(src_id: str, dst_id: str, relation: str, amount: float):
        key = (src_id, dst_id, relation)
        rec = edge_agg.get(key)
        if rec is None:
            rec = {
                "from": src_id,
                "to": dst_id,
                "label": relation,
                "count": 0,
                "amount": 0.0,
            }
            edge_agg[key] = rec

        rec["count"] += 1
        rec["amount"] += max(0.0, amount)

        node_degree[src_id] = node_degree.get(src_id, 0) + 1
        node_degree[dst_id] = node_degree.get(dst_id, 0) + 1

    for filing in filings:
        client_name = ((filing.get("client") or {}).get("name") or "").strip()
        registrant_name = ((filing.get("registrant") or {}).get("name") or "").strip()

        # IMPORTANT: verify actual field name in your LDA payload.
        # Based on your filters schema, this is likely present as `filing_amount_reported`.
        # If your payload uses a different key, change it here.
        amount = _parse_amount(filing.get("filing_amount_reported"))

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
                amount=amount,
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
                    amount=amount,
                )

    # Node sizing: based on degree
    for nid, n in nodes.items():
        d = node_degree.get(nid, 0)
        n["value"] = max(1, d)

    # Edge sizing: based on total amount (with a safe fallback to count)
    edges: list[dict] = []
    for rec in edge_agg.values():
        amt = float(rec["amount"])
        cnt = int(rec["count"])

        # vis-network edge thickness uses `value`.
        # Amounts can be huge; compress with sqrt-like scaling via power 0.5.
        # Avoid importing math by using ** 0.5.
        base = (amt ** 0.5) if amt > 0 else 0.0
        value = max(1.0, base / 100.0)  # tune divisor to taste

        edges.append({
            "from": rec["from"],
            "to": rec["to"],
            "label": rec["label"],
            "value": value,
            "title": f"{rec['label']} • {cnt} filings • total {_fmt_usd(amt)}",
        })

    return {
        "nodes": list(nodes.values()),
        "edges": edges,
        "filings_matched": len(filings),
    }
