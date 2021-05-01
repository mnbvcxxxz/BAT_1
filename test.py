import pyupbit
import numpy as np

# 위키독스 링크: https://wikidocs.net/book/1665
# 위키도독스 깃헙링크:  https://github.com/sharebook-kr/book-cryptocurrency
# 조코딩 깃헙링크:  https://github.com/youtube-jocoding/pyupbit-autotrade

access = "NoRVfwch6I71UZHCZq3ji9Z5xcXz8r7U2QnxlGQn"          # 본인 값으로 변경
secret = "J7t7vx31yrnbETxKroRJ6M1nyiddgGR571UL1YfG"          # 본인 값으로 변경
upbit = pyupbit.Upbit(access, secret)

print(upbit.get_balance("KRW-ETH"))     # KRW-XRP 조회
print(upbit.get_balance("KRW"))         # 보유 현금 조회
# print(pyupbit.get_tickers(fiat="KRW"))  # 특정Fiat로 매매 가능한 목록 조회
#
print(pyupbit.get_ohlcv("KRW-ETH", interval="minute30", count=30))

print("----------------------백테스팅-------------------")

# OHLCV(open, high, low, close, volume)로 당일 시가, 고가, 저가, 종가, 거래량에 대한 데이터
print("지난 데이터 추출")

df = pyupbit.get_ohlcv("KRW-ETH", interval="minute30", count=7)
print(df)


# 변동폭 * k 계산, (고가 - 저가) * k값
print("변동폭 * 0.5 계산")

df['range'] = (df['high'] - df['low']) * 0.5
print(df['range'])

# target(매수가), range 컬럼을 한칸씩 밑으로 내림(.shift(1))
df['target'] = df['open'] + df['range'].shift(1)

# ror(수익률), np.where(조건문, 참일때 값, 거짓일때 값)
df['ror'] = np.where(df['high'] > df['target'],
                     df['close'] / df['target'],
                     1)

# 누적 곱 계산(cumprod) => 누적 수익률
df['hpr'] = df['ror'].cumprod()

# Draw Down 계산 (누적 최대 값과 현재 hpr 차이 / 누적 최대값 * 100)
df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100

#MDD 계산
print("MDD(%): ", df['dd'].max())

#엑셀로 출력
# df.to_excel("dd.xlsx")
