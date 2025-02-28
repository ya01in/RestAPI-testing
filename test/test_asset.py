from dataclasses import dataclass
from typing import List, Union


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