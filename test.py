import pyupbit

access = "NoRVfwch6I71UZHCZq3ji9Z5xcXz8r7U2QnxlGQn"          # 본인 값으로 변경
secret = "J7t7vx31yrnbETxKroRJ6M1nyiddgGR571UL1YfG"          # 본인 값으로 변경
upbit = pyupbit.Upbit(access, secret)

print(upbit.get_balance("KRW-ETH"))     # KRW-XRP 조회
print(upbit.get_balance("KRW"))         # 보유 현금 조회