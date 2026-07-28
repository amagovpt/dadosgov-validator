"""
Dados.gov API Client
=====================
Thin client responsible for talking to the dados.gov API and translating
its responses into the shapes the rest of this codebase expects.

This module intentionally has no Flask, Celery, or DB imports — it should
be usable and testable in isolation, the same way app/utils/dataframe_processing.py
and app/utils/redis_store.py are.
"""

import os
import requests


DADOSGOV_API_BASE_URL = os.getenv("DADOSGOV_API_BASE_URL")
DADOSGOV_API_TIMEOUT_SECONDS = int(os.getenv("DADOSGOV_API_TIMEOUT_SECONDS", 15))


class DadosGovAPIError(Exception):
    """Raised when the dados.gov API request fails or returns an unexpected shape."""
    pass


def fetch_datasets_for_user(user_id: str, api_key: str = None) -> list[dict]:
    """
    Fetches the list of datasets associated with a given user from the dados.gov API.

    Args:
        user_id: The dados.gov user identifier to fetch datasets for.
        api_key: The API key to authenticate the request.

    Returns:
        A list of dataset dicts, each shaped like:
            {
                "dadosgov_dataset_id": str,
                "name": str,
                "url": str,
            }

    Raises:
        DadosGovAPIError: If the request fails, times out, or the response
            cannot be parsed into the expected shape.
    """
    url = f"{DADOSGOV_API_BASE_URL}/api/1/datasets/"
    req_params = {
        "owner": user_id
    }
    headers = {
        "accept": "application/json",
    }
    if api_key is not None:
        headers["X-API-KEY"] = api_key

    try:
        response = requests.get(
            url,
            params=req_params,
            headers=headers,
            timeout=DADOSGOV_API_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout as e:
        raise DadosGovAPIError(f"Tempo limite excedido ao contactar a API do dados.gov: {e}")
    except requests.exceptions.HTTPError as e:
        raise DadosGovAPIError(f"A API do dados.gov retornou um erro: {e}")
    except requests.exceptions.RequestException as e:
        raise DadosGovAPIError(f"Falha ao contactar a API do dados.gov: {e}")

    try:
        raw_data = response.json()
    except ValueError as e:
        raise DadosGovAPIError(f"A resposta da API do dados.gov não é um JSON válido: {e}")

    return _parse_datasets_response(raw_data)


def _parse_datasets_response(raw_data) -> list[dict]:
    """
    Translates the raw dados.gov API response into the list-of-dicts shape
    used by the rest of the codebase.

    Args:
        raw_data: The parsed JSON body returned by the dados.gov API.

    Returns:
        A list of dataset dicts: {"dadosgov_dataset_id": str, "name": str, "url": str}

    Raises:
        DadosGovAPIError: If the response doesn't match the expected shape.
    """
    if not isinstance(raw_data, dict) or "data" not in raw_data:
        raise DadosGovAPIError(f"Formato de resposta inesperado da API do dados.gov: {raw_data!r}")

    datasets = []
    for item in raw_data["data"]:
        try:
            resource_list = []
            for r in item["resources"]:
                resource_list.append({
                    "resource_id": r["id"],
                    "resource_title": r["title"],
                    "resource_url": r["url"]
                })

            datasets.append({
                "dadosgov_dataset_id": item["id"],
                "title": item["title"],
                "description": item["description"],
                "resource_list": resource_list
            })
        except (KeyError, TypeError) as e:
            raise DadosGovAPIError(f"Item de dataset com formato inesperado: {item!r} ({e})")

    return datasets


def fetch_resource_file(resource_url: str, api_key: str = None) -> bytes:
    """
    Fetches the content of a resource file from the dados.gov API.

    Args:
        resource_url: The URL of the resource file to fetch.
        api_key: The API key to authenticate the request.
    """
    try:
        if api_key is not None:
            headers = { "X-API-KEY": api_key }
            response = requests.get(resource_url, headers=headers, timeout=DADOSGOV_API_TIMEOUT_SECONDS, verify=False)
        else:
            response = requests.get(resource_url, timeout=DADOSGOV_API_TIMEOUT_SECONDS, verify=False)

        response.raise_for_status()
    except requests.exceptions.Timeout as e:
        raise DadosGovAPIError(f"Tempo limite excedido ao baixar o recurso: {e}")
    except requests.exceptions.HTTPError as e:
        raise DadosGovAPIError(f"Erro HTTP ao baixar o recurso: {e}")
    except requests.exceptions.RequestException as e:
        raise DadosGovAPIError(f"Falha ao baixar o recurso: {e}")

    return response.content
