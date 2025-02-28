import logging
import random
from dataclasses import dataclass
from typing import List, Union

import pytest
import requests


@dataclass
class CoinCapAsset:
    id: str
    name: str
    symbol: str
    explorer: str
    rank: int
    priceUsd: Union[None, float]
    marketCapUsd: Union[None, float]
    volumeUsd24Hr: Union[None, float]
    changePercent24Hr: Union[None, float]
    supply: Union[None, float]
    maxSupply: Union[None, float]
    vwap24Hr: Union[None, float]


@dataclass
class CoinCapAPIResponse:
    data: List[CoinCapAsset]
    timestamp: int


@dataclass
class CoinCapAPIErrorResponse:
    error: str
    timestamp: int


class TestCoinCapAPI:
    BASE_URL = "https://api.coincap.io/v2/assets"

    # Class variable to store headers needed for the requests
    headers = {
        'Content-Encoding': 'gzip',
        'Content-Type': 'application/json; charset=utf-8',
    }

    def _parse_response(self, response: requests.Response) -> Union[CoinCapAPIResponse, CoinCapAPIErrorResponse]:
        """
        Helper method to parse the JSON response into the correct dataclass.
        Returns:
            - CoinCapAPIResponse if the status code is 200 (successful).
            - CoinCapAPIErrorResponse if the status code is 400 (error with 'limit' parameter).
        """
        response_json = response.json()
        if response.status_code == 200:
            response_json = response.json()
            data = []
            for item in response_json.get('data', []):
                # Convert the fields to the correct data types
                try:
                    asset = CoinCapAsset(
                        id = item['id'],
                        name = item['name'],
                        symbol = item['symbol'],
                        rank = int(item['rank']),
                        explorer = item['explorer'],
                        priceUsd = float(item['priceUsd']) if item['priceUsd'] is not None else None,
                        marketCapUsd = float(item['marketCapUsd']) if item['marketCapUsd'] is not None else None,
                        volumeUsd24Hr = float(item['volumeUsd24Hr']) if item['volumeUsd24Hr'] is not None else None,
                        changePercent24Hr = float(item['changePercent24Hr']) if item['changePercent24Hr'] is not None else None,
                        supply = float(item['supply']) if item['supply'] is not None else None,
                        maxSupply = float(item['maxSupply']) if item['maxSupply'] is not None else None,
                        vwap24Hr = float(item['vwap24Hr']) if item['vwap24Hr'] is not None else None,
                    )
                    data.append(asset)
                except TypeError as e:
                    logging.error('Failed to convert json into correct data type')
                    logging.error(f'Failed item:{item}')
                    raise e
            return CoinCapAPIResponse(data=data, timestamp=response_json.get('timestamp', 0))
        elif response.status_code == 400:
            return CoinCapAPIErrorResponse(error=response_json.get('error', ''), timestamp=response_json.get('timestamp', 0))
        else:
            raise Exception(f"Unhandled status code: {response.status_code}")

    def test_timestamp(self):
        """
        Positive Test: Verifies that the API response contains a valid timestamp field.
        """
        response = requests.get(self.BASE_URL, headers=self.headers)
        assert response.status_code == 200
        api_response = self._parse_response(response)
        # Check that the 'timestamp' field is present and a valid integer
        assert isinstance(api_response.timestamp, int)
        assert api_response.timestamp > 0  # Ensure the timestamp is a positive integer

    def test_no_parameters(self):
        """
        Positive Test: Verifies that all assets are returned when no query parameters are provided.
        """
        response = requests.get(self.BASE_URL, headers=self.headers)
        assert response.status_code == 200
        api_response = self._parse_response(response)
        assert len(api_response.data) > 0, 'No information found in response data when request with no parameter.'

    def test_asset_field_type(self):
        """
        Positive Test: Verifies assets fields is correct
        """
        response = requests.get(self.BASE_URL, headers=self.headers)
        assert response.status_code == 200
        api_response = self._parse_response(response)
        asset = random.choice(api_response.data)
        assert isinstance(asset.id, str)
        assert isinstance(asset.name, str)
        assert isinstance(asset.symbol, str)
        assert isinstance(asset.explorer, str)
        assert isinstance(asset.rank, int)
        assert isinstance(asset.priceUsd, Union[None, float])
        assert isinstance(asset.marketCapUsd, Union[None, float])
        assert isinstance(asset.volumeUsd24Hr, Union[None, float])
        assert isinstance(asset.changePercent24Hr, Union[None, float])
        assert isinstance(asset.supply, Union[None, float])
        assert isinstance(asset.maxSupply, Union[None, float])
        assert isinstance(asset.vwap24Hr, Union[None, float])

    def test_asset_fields(self):
        """
        Positive Test: Verifies that assets contain essential fields such as 'id', 'name', 'symbol', etc.
        """
        response = requests.get(self.BASE_URL, headers=self.headers)
        assert response.status_code == 200
        api_response = self._parse_response(response)
        # Check that each asset contains the necessary fields
        for asset in api_response.data:
            assert hasattr(asset, 'id')
            assert hasattr(asset, 'name')
            assert hasattr(asset, 'symbol')
            assert hasattr(asset, 'priceUsd')
            assert hasattr(asset, 'marketCapUsd')
            assert hasattr(asset, 'volumeUsd24Hr')
            assert hasattr(asset, 'changePercent24Hr')
            assert hasattr(asset, 'supply')
            assert hasattr(asset, 'maxSupply')
            assert hasattr(asset, 'explorer')
            assert hasattr(asset, 'rank')
            assert hasattr(asset, 'vwap24Hr')

    def test_ids_parameter_bitcoin(self):
        """
        Possitive Test: Verifies the response when using an known Bitcoin ids which will only return Bitcoin information.
        """
        params = {'ids': 'bitcoin'}
        response = requests.get(self.BASE_URL, headers=self.headers, params=params)
        assert response.status_code == 200
        api_response = self._parse_response(response)
        assert len(api_response.data) == 1
        bitcoint_info: CoinCapAsset = api_response.data[0]
        assert bitcoint_info.id == 'bitcoin'

    def test_invalid_search_parameter(self):
        """
        Negative Test: Verifies the response when using an invalid search parameter.
        """
        invalid_search_target = 'invalidassetname'
        params = {'search': invalid_search_target}
        response = requests.get(self.BASE_URL, headers=self.headers, params=params)
        assert response.status_code == 200
        api_response = self._parse_response(response)
        assert len(api_response.data) == 0, f'Variable:{invalid_search_target} for testing invalid search name found information, need to update'

    @pytest.mark.parametrize('limit', [1, 10, 100, 1000])
    def test_limit_parameter(self, limit):
        """
        Positive Test: Verifies the API correctly applies the 'limit' parameter to return the correct number of assets.
        """
        params = {'limit': limit}  # Requesting a limit of 5 results
        response = requests.get(self.BASE_URL, headers=self.headers, params=params)
        assert response.status_code == 200
        api_response = self._parse_response(response)
        assert len(api_response.data) == limit, f'Set limit variable:{limit}'

    @pytest.mark.parametrize('bound', [0, 2000])
    def test_limit_parameter_bound(self, bound):
        """
        Positive limit Test: Verifies the API 'limit' parameter can return the correct upper bound.
        """
        params = {'limit': bound}  # Requesting a limit of 5 results
        response = requests.get(self.BASE_URL, headers=self.headers, params=params)
        assert response.status_code == 200
        api_response = self._parse_response(response)
        assert len(api_response.data) == bound, f"Set upper bound:{bound}"

    def test_invalid_limit_negative(self):
        """
        Negative Test: Verifies that the API returns a 400 error with the correct message when the 'limit' parameter is -1.
        """
        params = {'limit': -1}
        response = requests.get(self.BASE_URL, headers=self.headers, params=params)
        assert response.status_code == 400
        error_response = self._parse_response(response)
        assert isinstance(error_response, CoinCapAPIErrorResponse)
        assert error_response.error == "limit/offset cannot be negative"

    def test_invalid_limit_exceed_upperbound(self):
        """
        Negative Test: Verifies that the API returns a 400 error with the correct message when the 'limit' parameter exceeds 2000.
        """
        params = {'limit': 2001}
        response = requests.get(self.BASE_URL, headers=self.headers, params=params)
        assert response.status_code == 400
        error_response = self._parse_response(response)
        assert isinstance(error_response, CoinCapAPIErrorResponse)
        assert error_response.error == "limit exceeds 2000"
