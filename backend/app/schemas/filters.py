from pydantic import BaseModel

class FilingFilters(BaseModel):
    affiliated_organization_country: str | None = None
    affiliated_organization_listed_indicator: bool | None = None
    affiliated_organization_name: str | None = None

    client_country: str | None = None
    client_id: int | None = None
    client_name: str | None = None
    client_ppb_country: str | None = None
    client_ppb_state: str | None = None
    client_state: str | None = None

    filing_amount_reported_max: float | None = None
    filing_amount_reported_min: float | None = None
    filing_dt_posted_after: str | None = None
    filing_dt_posted_before: str | None = None
    filing_period: str | None = None
    filing_specific_lobbying_issues: str | None = None
    filing_type: str | None = None
    filing_uuid: str | None = None
    filing_year: int | None = None

    foreign_entity_country: str | None = None
    foreign_entity_listed_indicator: bool | None = None
    foreign_entity_name: str | None = None
    foreign_entity_ownership_percentage_max: str | None = None
    foreign_entity_ownership_percentage_min: str | None = None
    foreign_entity_ppb_country: str | None = None

    lobbyist_conviction_date_range_after: str | None = None
    lobbyist_conviction_date_range_before: str | None = None
    lobbyist_conviction_disclosure: str | None = None
    lobbyist_conviction_disclosure_indicator: bool | None = None
    lobbyist_covered_position: str | None = None
    lobbyist_covered_position_indicator: bool | None = None
    lobbyist_id: int | None = None
    lobbyist_name: str | None = None

    ordering: str | None = None

    registrant_country: str | None = None
    registrant_id: int | None = None
    registrant_name: str | None = None
    registrant_ppb_country: str | None = None

    def to_query_params(self) -> dict:
        # Only include fields that are not None.
        # This keeps requests clean and avoids sending unused params.
        data = self.model_dump()
        params: dict[str, str | int | float | bool] = {}
        for k, v in data.items():
            if v is None:
                continue
            params[k] = v
        return params