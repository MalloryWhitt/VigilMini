def node_id(group: str, name: str) -> str:
    # Namespacing prevents collisions like "ACME" appearing as both a client and registrant.
    return f"{group}:{name}"

def build_graph_from_filings(filings: list[dict], include_lobbyists: bool) -> dict:
    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    edge_seen: set[tuple[str, str, str]] = set()

    def upsert_node(group: str, name: str):
        nid = node_id(group, name)
        if nid not in nodes:
            nodes[nid] = {"id": nid, "label": name, "group": group}

    def add_edge(src_id: str, dst_id: str, label: str | None = None):
        key = (src_id, dst_id, label or "")
        if key in edge_seen:
            return
        edge_seen.add(key)
        edges.append({"from": src_id, "to": dst_id, "label": label})

    for filing in filings:
        client_name = ((filing.get("client") or {}).get("name") or "").strip()
        registrant_name = ((filing.get("registrant") or {}).get("name") or "").strip()

        if client_name:
            upsert_node("client", client_name)
        if registrant_name:
            upsert_node("registrant", registrant_name)

        if client_name and registrant_name:
            add_edge(
                src_id=node_id("registrant", registrant_name),
                dst_id=node_id("client", client_name),
                label="represents",
            )

        if include_lobbyists and registrant_name:
            lobbyists = filing.get("lobbyists") or []
            for lob in lobbyists:
                lob_name = ((lob or {}).get("name") or "").strip()
                if not lob_name:
                    continue
                upsert_node("lobbyist", lob_name)
                add_edge(
                    src_id=node_id("registrant", registrant_name),
                    dst_id=node_id("lobbyist", lob_name),
                    label="employs",
                )

    return {
        "nodes": list(nodes.values()),
        "edges": edges,
        "filings_matched": len(filings),
    }
