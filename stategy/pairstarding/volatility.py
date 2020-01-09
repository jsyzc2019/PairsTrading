#����������ģ��
#Vega���ͣ�����������ʲ��۸񲨶��ʱ䶯ʱ����Ȩ�۸�ı仯���ȣ�
#�����������ڻ��۸�Ĳ����ʵı仯����Ȩ��ֵ��Ӱ�졣
#Vega��ָ��Ȩ�ѣ�P���仯���Ļ��ʲ����ԣ�Volatility���仯�������ԡ�

#�������Ͻ���Ҫ������������ʵĴ�С�������ѡ�������Ȩ����ģ��(��BSģ��)
#��������Ȩ�۸��������������(��Ĺɼۡ�ִ�м۸����ʡ�����ʱ�䡢������)
#֮��Ķ�����ϵ��ֻҪ������ǰ4��������������Ȩ��ʵ���г��۸���Ϊ��֪����
#�붨�۹�ʽ���Ϳ��Դ��н��Ωһ��δ֪�������С�������������ʡ�
# Black-Scholes-Merton (1973)
#
# Valuation of European call options in Black-Scholes-Merton model
# incl. Vega function and inplied volatility estimation
# bsm_function.py
#

# Analytical Black-Scholes-Merton (BSM) Formula

def bsm_call_value(S0, K, T, r, sigma):
""" Valuation of European call option in BSM model.
Analytical formula.

Parameters
==========
S0 : float
initial stock/index level
K : float
strick price
T : float
maturity date (in year fractions)
r : float
constant risk-free short rate
sigma : float
volatility factor in diffusion term

Returns
=======
values : float
present value of the European call option
"""
from math import log, sqrt, exp
from scipy import stats

S0 = float(S0)
d1 = (log(S0 / K) + (r + 0.5 *sigma ** 2) * T) / (sigma * sqrt(T))
d2 = (log(S0 / K) + (r - 0.5 *sigma ** 2) * T) / (sigma * sqrt(T))
value = (S0 * stats.norm.cdf(d1, 0.0, 1.0)
- K * exp(-r * T) * stats.norm.cdf(d2, 0.0, 1.0))
# stats.norm.cdf -> cumulative distribution function
# for normal distribution
return value

# Vega function

def bsm_vega(S0, K, T, r, sigma):
""" Vega of European option in BSM model.

Parameters
==========
S0 : float
initial stock/index level
K : float
strick price
T : float
maturity date (in year fractions)
r : float
constant risk-free short rate
sigma : float
volatility factor in diffusion term

Returns
=======
Vega : float
partial derivation of BSM formula with respect
to sigma, i.e. Vega
"""
from math import log, sqrt
from scipy import stats

S0 = float(S0)
d1 = (log(S0 / K) + (r + 0.5 *sigma ** 2) * T) / (sigma * sqrt(T))
vega = S0 * stats.norm.cdf(d1, 0.0, 1.0) * sqrt(T)
return vega

# implied volatility function

def bsm_imp_vol(S0, K, T, r, C0, sigma_est, it=100):
""" Implied volatility of European call option in BSM model.

Parameters
==========
S0 : float
initial stock/index level
K : float
strick price
T : float
maturity date (in year fractions)
r : float
constant risk-free short rate
sigma_est : float
estimate of impl. volatility
it : integer


Returns
=======
Vega : float
partial derivation of BSM formula with respect
to sigma, i.e. Vega
"""
for i in range(it):
sigma_est -= ((bsm_call_value(S0, K, T, r, sigma_est) - C0)
/bsm_vega(S0, K, T, r, sigma_est))
return sigma_est





#�й���ָiVIX,000188.SH
#��ʵ�ֲ����ʣ�RV��


#vanna��ʾvega�Ա�ļ۸�仯�����ж�
#volga��ʾvega�Բ����ʱ仯�����ж�

#VVģ������

#SABR������ģ��	  	