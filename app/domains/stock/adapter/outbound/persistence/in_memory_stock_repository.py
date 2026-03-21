from typing import List

from app.domains.stock.application.usecase.stock_repository_port import StockRepositoryPort
from app.domains.stock.domain.entity.stock import Stock

STOCK_LIST: List[Stock] = [
    # KOSPI
    Stock("005930", "삼성전자", "KOSPI"),
    Stock("000660", "SK하이닉스", "KOSPI"),
    Stock("035420", "NAVER", "KOSPI"),
    Stock("035720", "카카오", "KOSPI"),
    Stock("373220", "LG에너지솔루션", "KOSPI"),
    Stock("005380", "현대자동차", "KOSPI"),
    Stock("000270", "기아", "KOSPI"),
    Stock("051910", "LG화학", "KOSPI"),
    Stock("006400", "삼성SDI", "KOSPI"),
    Stock("068270", "셀트리온", "KOSPI"),
    Stock("207940", "삼성바이오로직스", "KOSPI"),
    Stock("005490", "POSCO홀딩스", "KOSPI"),
    Stock("000810", "삼성화재", "KOSPI"),
    Stock("012330", "현대모비스", "KOSPI"),
    Stock("028260", "삼성물산", "KOSPI"),
    Stock("066570", "LG전자", "KOSPI"),
    Stock("003550", "LG", "KOSPI"),
    Stock("015760", "한국전력", "KOSPI"),
    Stock("096770", "SK이노베이션", "KOSPI"),
    Stock("017670", "SK텔레콤", "KOSPI"),
    Stock("030200", "KT", "KOSPI"),
    Stock("032830", "삼성생명", "KOSPI"),
    Stock("009150", "삼성전기", "KOSPI"),
    Stock("010130", "고려아연", "KOSPI"),
    Stock("011200", "HMM", "KOSPI"),
    Stock("055550", "신한지주", "KOSPI"),
    Stock("105560", "KB금융", "KOSPI"),
    Stock("086790", "하나금융지주", "KOSPI"),
    Stock("032640", "LG유플러스", "KOSPI"),
    Stock("003490", "대한항공", "KOSPI"),
    Stock("018260", "삼성에스디에스", "KOSPI"),
    Stock("033780", "KT&G", "KOSPI"),
    Stock("004020", "현대제철", "KOSPI"),
    Stock("011170", "롯데케미칼", "KOSPI"),
    Stock("010950", "S-Oil", "KOSPI"),
    Stock("090430", "아모레퍼시픽", "KOSPI"),
    Stock("034220", "LG디스플레이", "KOSPI"),
    Stock("097950", "CJ제일제당", "KOSPI"),
    Stock("139480", "이마트", "KOSPI"),
    Stock("271560", "오리온", "KOSPI"),
    Stock("259960", "크래프톤", "KOSPI"),
    Stock("316140", "우리금융지주", "KOSPI"),
    Stock("000100", "유한양행", "KOSPI"),
    Stock("008770", "호텔신라", "KOSPI"),
    Stock("010060", "OCI홀딩스", "KOSPI"),
    Stock("001040", "CJ", "KOSPI"),
    Stock("002790", "아모레퍼시픽그룹", "KOSPI"),
    Stock("003230", "삼양식품", "KOSPI"),
    Stock("007070", "GS리테일", "KOSPI"),
    Stock("006360", "GS건설", "KOSPI"),

    # KOSDAQ
    Stock("247540", "에코프로비엠", "KOSDAQ"),
    Stock("086520", "에코프로", "KOSDAQ"),
    Stock("196170", "알테오젠", "KOSDAQ"),
    Stock("293490", "카카오게임즈", "KOSDAQ"),
    Stock("035900", "JYP엔터테인먼트", "KOSDAQ"),
    Stock("041510", "에스엠", "KOSDAQ"),
    Stock("122870", "와이지엔터테인먼트", "KOSDAQ"),
    Stock("112040", "위메이드", "KOSDAQ"),
    Stock("263750", "펄어비스", "KOSDAQ"),
    Stock("357780", "솔브레인", "KOSDAQ"),
    Stock("145020", "휴젤", "KOSDAQ"),
    Stock("214150", "클래시스", "KOSDAQ"),
    Stock("091990", "셀트리온헬스케어", "KOSDAQ"),
    Stock("053800", "안랩", "KOSDAQ"),
    Stock("067160", "아프리카TV", "KOSDAQ"),
    Stock("039030", "이오테크닉스", "KOSDAQ"),
    Stock("240810", "원익IPS", "KOSDAQ"),
    Stock("064760", "티씨케이", "KOSDAQ"),
    Stock("047810", "한국항공우주", "KOSDAQ"),
    Stock("060310", "3S", "KOSDAQ"),

    # NASDAQ / NYSE
    Stock("AAPL", "Apple Inc.", "NASDAQ"),
    Stock("MSFT", "Microsoft Corporation", "NASDAQ"),
    Stock("GOOGL", "Alphabet Inc.", "NASDAQ"),
    Stock("AMZN", "Amazon.com Inc.", "NASDAQ"),
    Stock("META", "Meta Platforms Inc.", "NASDAQ"),
    Stock("NVDA", "NVIDIA Corporation", "NASDAQ"),
    Stock("TSLA", "Tesla Inc.", "NASDAQ"),
    Stock("NFLX", "Netflix Inc.", "NASDAQ"),
    Stock("AMD", "Advanced Micro Devices", "NASDAQ"),
    Stock("INTC", "Intel Corporation", "NASDAQ"),
    Stock("QCOM", "Qualcomm Inc.", "NASDAQ"),
    Stock("AVGO", "Broadcom Inc.", "NASDAQ"),
    Stock("ADBE", "Adobe Inc.", "NASDAQ"),
    Stock("CRM", "Salesforce Inc.", "NYSE"),
    Stock("ORCL", "Oracle Corporation", "NYSE"),
    Stock("TSM", "Taiwan Semiconductor", "NYSE"),
    Stock("V", "Visa Inc.", "NYSE"),
    Stock("JPM", "JPMorgan Chase & Co.", "NYSE"),
    Stock("BRK.B", "Berkshire Hathaway", "NYSE"),
    Stock("BABA", "Alibaba Group", "NYSE"),
]


class InMemoryStockRepository(StockRepositoryPort):

    def search(self, query: str) -> List[Stock]:
        q = query.lower()
        results = [
            s for s in STOCK_LIST
            if q in s.symbol.lower() or q in s.name.lower()
        ]
        return results[:50]
