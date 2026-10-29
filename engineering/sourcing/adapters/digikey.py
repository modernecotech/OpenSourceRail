"""DigiKey v4 pricing observations with explicit package and quantity evidence.

No production request occurs without environment credentials. Test transports and
sandbox payloads are not live commercial evidence. OAuth tokens stay in memory.
"""
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import os
import time
from urllib.parse import quote, urlencode

from ..model import day, decimal, decimal_text, is_id, record, validate_record
from .http import FetchError, request
from ._source import checked_source


def _locale(payload, expected):
    settings = payload.get("SettingsUsed", {})
    actual = payload.get("SearchLocaleUsed") or settings.get("SearchLocale") or settings.get("SearchLocaleUsed") or {}
    if not isinstance(actual, dict) or not isinstance(expected, dict):
        raise ValueError("Explicit expected and returned DigiKey locale required")
    for key in ("Site", "Language", "Currency"):
        if not isinstance(actual.get(key), str) or not isinstance(expected.get(key), str):
            raise ValueError("DigiKey locale incomplete")
        if actual[key].casefold() != expected[key].casefold():
            raise ValueError("Returned DigiKey locale/currency differs from request")
    return actual


def _quantity_options(payload, source, *, expected_locale, price_date, quantity_constraints):
    """Admit single-package quotes only at their actually priced quantity.

    A recommendation combining package types is an indivisible commercial
    bundle and stays held; its component prices cannot become independent offers.
    """
    locale = _locale(payload, expected_locale)
    options = payload.get("MyPricingOptions") or payload.get("StandardPricingOptions") or []
    if not isinstance(options, list) or len(options) > 1000:
        raise ValueError("Bounded DigiKey quantity options required")
    result = []
    for option in options:
        rows = option.get("Products")
        if not isinstance(rows, list) or not rows or len(rows) > 1000:
            raise ValueError("Explicit package options required")
        if len(rows) != 1:
            result.append(record("run", adapter="digikey-quantity-options", source_id=source["record_id"],
                status="held", reason="mixed-package-option-cannot-be-split-into-independent-offers",
                pricing_option=option.get("PricingOption"),
                package_skus=[r.get("DigiKeyProductNumber") for r in rows], price_offers_created=0))
            continue
        row = rows[0]
        quantity = decimal(row.get("QuantityPriced"), "actually priced quantity", positive=True)
        if quantity != int(quantity):
            raise ValueError("Whole component quantity required")
        if decimal(option.get("TotalQuantityPriced"), positive=True) != quantity:
            raise ValueError("Quantity-option total differs from actual package quantity")
        variant = dict(row, MarketPlace=row.get("Marketplace"),
                       StandardPricing=[dict(BreakQuantity=str(quantity), UnitPrice=row.get("UnitPrice"))],
                       _exact_quantity=str(quantity), _pricing_option=option.get("PricingOption"))
        normalized = dict(SettingsUsed=dict(SearchLocale=locale), ProductPricings=[dict(
            Manufacturer=payload.get("Manufacturer"),
            ManufacturerProductNumber=payload.get("ManufacturerPartNumber"),
            Description=payload.get("Description"), ProductVariations=[variant])])
        result.extend(_parse_object(normalized, source, expected_locale=expected_locale,
            price_date=price_date, quantity_constraints=quantity_constraints))
    if not result:
        raise ValueError("No quantity pricing options returned")
    return result


def parse_digikey_response(payload, source, *, expected_locale,
                           price_date=None, quantity_constraints=None):
    """Return canonical leads and observed prices with explicit purchasing holds.

    ``quantity_constraints`` maps exact DigiKey SKUs to
    ``{order_multiple: decimal, source_id: validated observation identity}``.
    StandardPackage is not inferred to be the order multiple. Missing explicit
    order-multiple evidence preserves price facts but holds purchasable costing.
    """
    checked_source(source, "distributor_catalogue", payload)
    if isinstance(payload, bytes):
        if len(payload) > 20 * 1024**2:
            raise ValueError("DigiKey payload budget exceeded")
        payload = json.loads(payload, parse_float=Decimal)
    if not isinstance(payload, dict):
        raise ValueError("DigiKey object response required")
    return _parse_object(payload, source, expected_locale=expected_locale,
                         price_date=price_date, quantity_constraints=quantity_constraints)


def _parse_object(payload, source, *, expected_locale, price_date=None,
                  quantity_constraints=None):
    if "StandardPricingOptions" in payload or "MyPricingOptions" in payload:
        return _quantity_options(payload, source, expected_locale=expected_locale,
            price_date=price_date, quantity_constraints=quantity_constraints)
    locale = _locale(payload, expected_locale)
    observed = source["retrieved_at"][:10] if price_date is None else price_date
    day(observed)
    if observed > source["retrieved_at"][:10]:
        raise ValueError("Price observation cannot follow source retrieval")
    if isinstance(payload.get("ProductPricings"), list):
        products = payload["ProductPricings"]
    elif isinstance(payload.get("Product"), dict):
        products = [payload["Product"]]
    else:
        raise ValueError("Official ProductPricing/ProductDetails response required")
    if len(products) > 1000:
        raise ValueError("DigiKey product budget exceeded")
    constraints = quantity_constraints or {}
    records = []
    seen = set()
    variation_count = 0
    for product in products:
        manufacturer = product.get("Manufacturer", {}).get("Name")
        part_number = product.get("ManufacturerProductNumber")
        if not manufacturer or not part_number:
            raise ValueError("Exact manufacturer and manufacturer part number required")
        variations = product.get("ProductVariations")
        if not isinstance(variations, list) or len(variations) > 1000:
            raise ValueError("Bounded exact product variations required")
        for variation in variations:
            variation_count += 1
            if variation_count > 10000:
                raise ValueError("Total DigiKey variation budget exceeded")
            sku = variation.get("DigiKeyProductNumber")
            packaging = variation.get("PackageType", {})
            if not sku or not isinstance(packaging, dict) or not packaging.get("Name"):
                raise ValueError("Exact DigiKey SKU and package identity required")
            supplier = variation.get("Supplier")
            marketplace = variation.get("MarketPlace")
            key = (manufacturer, part_number, sku, packaging.get("Id"), packaging["Name"],
                   json.dumps(supplier, sort_keys=True))
            if key in seen:
                raise ValueError("Duplicate DigiKey package variation")
            seen.add(key)
            holds = []
            if source.get("environment") == "sandbox":
                holds.append("sandbox-data-not-live-price-evidence")
            if marketplace is True and not supplier:
                holds.append("marketplace-supplier-identity-unreported")
            moq = variation.get("MinimumOrderQuantity")
            if moq is None:
                holds.append("minimum-order-quantity-unreported")
            else:
                moq = decimal_text(moq, "MOQ", positive=True)
                if decimal(moq) != int(decimal(moq)):
                    raise ValueError("Whole DigiKey MOQ required")
            constraint = constraints.get(sku)
            multiple = None
            constraint_source = None
            if constraint is None:
                holds.append("order-multiple-evidence-unreported")
            elif not isinstance(constraint, dict) or not is_id(constraint.get("source_id")):
                raise ValueError("Order multiple requires an explicit source identity")
            else:
                multiple = decimal_text(constraint.get("order_multiple"), "order multiple", positive=True)
                if decimal(multiple) != int(decimal(multiple)):
                    raise ValueError("Whole DigiKey order multiple required")
                constraint_source = constraint["source_id"]
            prices = variation.get("MyPricing") or variation.get("StandardPricing") or []
            if not isinstance(prices, list) or len(prices) > 1000:
                raise ValueError("Bounded DigiKey price tiers required")
            if not prices:
                holds.append("published-price-unreported")
            spec = dict(distributor_sku=sku, package_type=packaging, supplier=supplier,
                        marketplace=marketplace, minimum_order_quantity=moq,
                        order_multiple=multiple, order_multiple_source_id=constraint_source,
                        quantity_available=variation.get("QuantityAvailableforPackageType"),
                        manufacturer_lead_weeks=product.get("ManufacturerLeadWeeks"),
                        country_of_origin=None, technical_compatibility="pending",
                        sourcing_holds=holds, parameters=product.get("Parameters", []),
                        exact_quantity_quote=variation.get("_exact_quantity"),
                        pricing_option=variation.get("_pricing_option"))
            source_ids = [source["record_id"]]
            if constraint_source and constraint_source not in source_ids:
                source_ids.append(constraint_source)
            description = product.get("Description", {})
            if isinstance(description, dict):
                description = description.get("DetailedDescription") or description.get("ProductDescription")
            lead = record("product", product_key="DigiKey:" + sku,
                          manufacturer=manufacturer, part_number=part_number,
                          category="catalogue-electronics", description=description or part_number,
                          specifications=spec, source_ids=source_ids)
            records.append(lead)
            if not prices or source.get("environment") == "sandbox":
                continue
            breaks = []
            for row in prices:
                lower = decimal(row.get("BreakQuantity"), "price-break quantity", positive=True)
                price = decimal(row.get("UnitPrice"), "unit price")
                breaks.append((lower, price, row.get("TotalPrice")))
            breaks.sort(key=lambda row: row[0])
            if len({q for q, _, _ in breaks}) != len(breaks):
                raise ValueError("Duplicate DigiKey break quantity")
            tiers = [dict(minimum_quantity=str(q),
                          maximum_quantity=str(breaks[i + 1][0]) if i + 1 < len(breaks) else None,
                          unit_price=str(price)) for i, (q, price, _) in enumerate(breaks)]
            if variation.get("_exact_quantity") is not None:
                if len(tiers) != 1:
                    raise ValueError("Exact-quantity observation must have one price")
                tiers[0]["maximum_quantity"] = str(decimal(variation["_exact_quantity"]) + 1)
            fee = variation.get("DigiReelingFee", variation.get("DigiReelFee"))
            records.append(record("offer", product_id=lead["record_id"],
                source_id=source["record_id"], price_date=observed, valid_until=None,
                currency=locale["Currency"].upper(), quantity_unit="each", source_class="B",
                tax_basis="unknown", tax_rate=None, minimum_order_quantity=moq,
                order_multiple=multiple, tiers=tiers, order_multiple_source_id=constraint_source,
                distributor_sku=sku, package_type=packaging, supplier=supplier,
                availability=variation.get("QuantityAvailableforPackageType"),
                maximum_order_quantity=variation.get("MaxQuantityForDistribution"),
                reeling_fee=None if fee is None else decimal_text(fee, "reeling fee"),
                marketplace=marketplace, freight_cost=None, incoterm=None,
                country_of_origin=None, authentication_status="catalogue-observation",
                price_kind="account-specific" if variation.get("MyPricing") else "standard",
                sourcing_holds=holds,
                purchase_cost_admission="held" if holds else "catalogue-screening-only",
                installed_cost_complete=False))
    return records


class DigiKeyClient:
    """Read-only official v4 client; no ordering, quoting or account mutation API."""

    def __init__(self, *, environment="production", transport=None, environ=None,
                 clock=time.monotonic):
        if environment not in {"production", "sandbox"}:
            raise ValueError("Explicit DigiKey environment required")
        env = os.environ if environ is None else environ
        self._client_id = env.get("DIGIKEY_CLIENT_ID")
        self._client_secret = env.get("DIGIKEY_CLIENT_SECRET")
        self._account_id = env.get("DIGIKEY_ACCOUNT_ID")
        self.environment = environment
        self._host = "api.digikey.com" if environment == "production" else "sandbox-api.digikey.com"
        self._transport = transport
        self._clock = clock
        self._token = None
        self._expires_at = 0

    def __repr__(self):
        return "DigiKeyClient(environment=" + repr(self.environment) + ", credentials=<redacted>)"

    def _call(self, method, path, *, headers=None, body=None):
        return request(method, "https://" + self._host + path,
                       headers=headers, body=body, allowed_hosts={self._host},
                       timeout=30, max_bytes=20 * 1024**2,
                       transport=self._transport, credentialled=True)

    def _authorize(self):
        if self._token is not None and self._clock() < self._expires_at:
            return self._token
        body = urlencode(dict(client_id=self._client_id,
                              client_secret=self._client_secret,
                              grant_type="client_credentials")).encode()
        _, _, raw, _ = self._call("POST", "/v1/oauth2/token", body=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"})
        try:
            value = json.loads(raw)
            token = value["access_token"]
            lifetime = float(decimal(value["expires_in"], "token lifetime", positive=True))
            if not isinstance(token, str) or not token or value.get("token_type", "").lower() != "bearer":
                raise ValueError
        except (ValueError, TypeError, KeyError):
            raise FetchError("invalid-oauth-response") from None
        self._token = token
        self._expires_at = self._clock() + max(0, lifetime - min(30, lifetime / 10))
        return token

    def get_pricing(self, product_number, *, requested_quantity=None,
                    expected_locale=None, quantity_constraints=None):
        if not self._client_id or not self._client_secret or not self._account_id:
            return [record("run", adapter="digikey", status="held",
                           reason="authentication-required", network_executed=False,
                           required_environment_variables=["DIGIKEY_CLIENT_ID", "DIGIKEY_CLIENT_SECRET", "DIGIKEY_ACCOUNT_ID"])]
        if not isinstance(product_number, str) or not product_number.strip() or len(product_number) > 250:
            raise ValueError("Bounded exact product number required")
        locale = expected_locale or dict(Site="UK", Language="en", Currency="GBP")
        if set(locale) != {"Site", "Language", "Currency"} or not all(isinstance(v, str) and v for v in locale.values()):
            raise ValueError("Explicit DigiKey site/language/currency required")
        path = "/products/v4/search/" + quote(product_number, safe="")
        if requested_quantity is None:
            path += "/pricing"
        else:
            quantity = decimal(requested_quantity, "requested quantity", positive=True)
            if quantity != int(quantity) or quantity > 2147483647:
                raise ValueError("DigiKey requested quantity requires a positive int32")
            path += "/pricingbyquantity/" + str(int(quantity))
        try:
            token = self._authorize()
            headers = {"Authorization": "Bearer " + token,
                       "X-DIGIKEY-Client-Id": self._client_id,
                       "X-DIGIKEY-Account-Id": self._account_id,
                       "X-DIGIKEY-Locale-Site": locale["Site"],
                       "X-DIGIKEY-Locale-Language": locale["Language"],
                       "X-DIGIKEY-Locale-Currency": locale["Currency"],
                       "Accept": "application/json"}
            _, _, raw, url = self._call("GET", path, headers=headers)
            source = record("source", publisher="DigiKey", url=url,
                            retrieved_at=datetime.now(timezone.utc).isoformat(),
                            access="official-authenticated-API", source_kind="distributor_catalogue",
                            document_sha256=hashlib.sha256(raw).hexdigest(), licence=None,
                            environment=self.environment)
            result = parse_digikey_response(raw, source, expected_locale=locale,
                                           quantity_constraints=quantity_constraints)
            return [source] + result
        except FetchError as error:
            if error.status == 401:
                self._token = None
            return [record("run", adapter="digikey", status="held", reason=error.code,
                           http_status=error.status, network_executed=True)]
