import pyupbit

access = "NoRVfwch6I71UZHCZq3ji9Z5xcXz8r7U2QnxlGQn"          # 본인 값으로 변경
secret = "J7t7vx31yrnbETxKroRJ6M1nyiddgGR571UL1YfG"          # 본인 값으로 변경
upbit = pyupbit.Upbit(access, secret)

print(upbit.get_balance("KRW-ETH"))     # KRW-XRP 조회
print(upbit.get_balance("KRW"))         # 보유 현금 조회
print(pyupbit.get_tickers(fiat="KRW"))  # 특정Fiat로 매매 가능한 목록 조회
#
print(pyupbit.get_ohlcv("KRW-BTC", interval="day", count=8))