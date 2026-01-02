from fastapi import APIRouter, Depends, Query

from app.schemas.filters import FilingFilters
from app.schemas.graph import GraphResponse, PingResponse
from app.services.lda_client import lda_ping, lda_list_filings
from app.services.graph_builder import build_graph_from_filings

router = APIRouter(tags=["lda"])


def filters_dep(
    affiliated_organization_country: str | None = None,
    affiliated_organization_listed_indicator: bool | None = None,
    affiliated_organization_name: str | None = None,
    client_country: str | None = None,
    client_id: int | None = None,
    client_name: str | None = None,
    client_ppb_country: str | None = None,
    client_ppb_state: str | None = None,
    client_state: str | None = None,
    filing_amount_reported_max: float | None = None,
    filing_amount_reported_min: float | None = None,
    filing_dt_posted_after: str | None = None,
    filing_dt_posted_before: str | None = None,
    filing_period: str | None = None,
    filing_specific_lobbying_issues: str | None = None,
    filing_type: str | None = None,
    filing_uuid: str | None = None,
    filing_year: int | None = None,
    foreign_entity_country: str | None = None,
    foreign_entity_listed_indicator: bool | None = None,
    foreign_entity_name: str | None = None,
    foreign_entity_ownership_percentage_max: str | None = None,
    foreign_entity_ownership_percentage_min: str | None = None,
    foreign_entity_ppb_country: str | None = None,
    lobbyist_conviction_date_range_after: str | None = None,
    lobbyist_conviction_date_range_before: str | None = None,
    lobbyist_conviction_disclosure: str | None = None,
    lobbyist_conviction_disclosure_indicator: bool | None = None,
    lobbyist_covered_position: str | None = None,
    lobbyist_covered_position_indicator: bool | None = None,
    lobbyist_id: int | None = None,
    lobbyist_name: str | None = None,
    ordering: str | None = None,
    registrant_country: str | None = None,
    registrant_id: int | None = None,
    registrant_name: str | None = None,
    registrant_ppb_country: str | None = None,
) -> FilingFilters:
    # Explicit, readable mapping. No magic.
    return FilingFilters(
        affiliated_organization_country=affiliated_organization_country,
        affiliated_organization_listed_indicator=affiliated_organization_listed_indicator,
        affiliated_organization_name=affiliated_organization_name,
        client_country=client_country,
        client_id=client_id,
        client_name=client_name,
        client_ppb_country=client_ppb_country,
        client_ppb_state=client_ppb_state,
        client_state=client_state,
        filing_amount_reported_max=filing_amount_reported_max,
        filing_amount_reported_min=filing_amount_reported_min,
        filing_dt_posted_after=filing_dt_posted_after,
        filing_dt_posted_before=filing_dt_posted_before,
        filing_period=filing_period,
        filing_specific_lobbying_issues=filing_specific_lobbying_issues,
        filing_type=filing_type,
        filing_uuid=filing_uuid,
        filing_year=filing_year,
        foreign_entity_country=foreign_entity_country,
        foreign_entity_listed_indicator=foreign_entity_listed_indicator,
        foreign_entity_name=foreign_entity_name,
        foreign_entity_ownership_percentage_max=foreign_entity_ownership_percentage_max,
        foreign_entity_ownership_percentage_min=foreign_entity_ownership_percentage_min,
        foreign_entity_ppb_country=foreign_entity_ppb_country,
        lobbyist_conviction_date_range_after=lobbyist_conviction_date_range_after,
        lobbyist_conviction_date_range_before=lobbyist_conviction_date_range_before,
        lobbyist_conviction_disclosure=lobbyist_conviction_disclosure,
        lobbyist_conviction_disclosure_indicator=lobbyist_conviction_disclosure_indicator,
        lobbyist_covered_position=lobbyist_covered_position,
        lobbyist_covered_position_indicator=lobbyist_covered_position_indicator,
        lobbyist_id=lobbyist_id,
        lobbyist_name=lobbyist_name,
        ordering=ordering,
        registrant_country=registrant_country,
        registrant_id=registrant_id,
        registrant_name=registrant_name,
        registrant_ppb_country=registrant_ppb_country,
    )


@router.get("/lda/ping", response_model=PingResponse)
async def ping():
    return await lda_ping()


# IMPORTANT: response_model_by_alias=True ensures edges serialize as {"from": "..."}
@router.get("/graph/sample", response_model=GraphResponse, response_model_by_alias=True)
async def graph_sample(
    limit: int = Query(default=50, ge=1, le=100),
    include_lobbyists: bool = Query(default=True),
    filters: FilingFilters = Depends(filters_dep),
):
    base_filters = filters.to_query_params()
    base_filters.setdefault("ordering", "-filing_dt_posted")

    filings = await lda_list_filings(
        page_size=limit,
        extra_params=base_filters,
    )
    return build_graph_from_filings(
        filings=filings,
        include_lobbyists=include_lobbyists,
    )


from math import ceil

@router.get("/graph/entity", response_model=GraphResponse, response_model_by_alias=True)
async def graph_search_entity(
    q: str = Query(min_length=1),
    limit: int = Query(default=50, ge=1, le=100),
    include_lobbyists: bool = Query(default=True),
    filters: FilingFilters = Depends(filters_dep),
):
    base_filters = filters.to_query_params()
    base_filters.setdefault("ordering", "-filing_dt_posted")

    per = max(1, ceil(limit / 3))

    filings_client = await lda_list_filings(
        page_size=per,
        extra_params={**base_filters, "client_name": q},
    )
    filings_reg = await lda_list_filings(
        page_size=per,
        extra_params={**base_filters, "registrant_name": q},
    )
    filings_lob = await lda_list_filings(
        page_size=per,
        extra_params={**base_filters, "lobbyist_name": q},
    )

    by_uuid: dict[str, dict] = {}
    for f in (filings_client + filings_reg + filings_lob):
        uid = (f.get("filing_uuid") or "").strip()
        if uid:
            by_uuid[uid] = f

    filings = list(by_uuid.values())
    filings.sort(key=lambda f: (f.get("filing_dt_posted") or ""), reverse=True)
    filings = filings[:limit]

    return build_graph_from_filings(
        filings=filings,
        include_lobbyists=include_lobbyists,
    )



@router.get("/graph/topic", response_model=GraphResponse, response_model_by_alias=True)
async def graph_search_topic(
    q: str = Query(min_length=1),
    limit: int = Query(default=50, ge=1, le=100),
    include_lobbyists: bool = Query(default=True),
    filters: FilingFilters = Depends(filters_dep),
):
    base_filters = filters.to_query_params()
    base_filters.setdefault("ordering", "-filing_dt_posted")

    filings = await lda_list_filings(
        page_size=limit,
        extra_params={**base_filters, "filing_specific_lobbying_issues": q},
    )
    return build_graph_from_filings(
        filings=filings,
        include_lobbyists=include_lobbyists,
    )
