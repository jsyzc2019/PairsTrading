#jupyter notebook --no-browser --port 6061 --ip=192.168.56.102


import tushare as ts
%matplotlib inline
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd

import sys
sys.path.append('/home/huangtuo/gitdoc/markowitz-portfolio-optimization')
from markowitz import MarkowitzOpt

#import cvxopt as opt
#from cvxopt import blas, solvers

#tushare升级需要用api进行调用
ts.set_token('fbe098e754f69ea09a7bd0c144a00754e93aab1911508cb408c5cb21')
pro = ts.pro_api()



def output_data(security,source,begin_date,end_date,column): 
	  if source=='tushare':
	     fm=pro.daily(ts_code=security, start_date=begin_date, end_date=end_date)
	     fm.index=fm['trade_date']
	     fm=pd.DataFrame(fm['close'])
	     fm=fm.rename(columns={'close':security})
	  return(fm)

#initialize date	  
begin_date='20190101'
end_date='20191231'	
interest_rate = 0								# Fixed interest rate
min_return = 0.003								# Minimum desired return

  
convertible_bond_code=(['300059.sz','000001.sz','000783.sz','300335.sz'])
symbols= convertible_bond_code
column= "close"	
#outdata 初始化 生成
outdata=output_data(convertible_bond_code[0],'tushare',begin_date,end_date,column)	
for i in range(1,len(symbols)): 
   outdata = outdata.join(output_data(symbols[i],'tushare',begin_date,end_date,column))

####[datetime.strptime(x,'%Y%m%d') for x in outdata.index]
outdata.index=[datetime.strptime(x,'%Y%m%d') for x in outdata.index]

#reset by index order
outdata=outdata.sort_index()



################outdata generate end####################################
# Specify number of days to shift
shift = 1
# Compute returns over the time period specified by shift
shift_returns = outdata/outdata.shift(shift) - 1


# Specify filter "length"
filter_len = 2
# Compute mean and variance
shift_returns_mean = shift_returns.ewm(span=filter_len).mean()
shift_returns_var = shift_returns.ewm(span=filter_len).var()

# Compute covariances
convertible_bond_code=(['300059.sz','000001.sz','000783.sz','300335.sz'])
StockList=convertible_bond_code
NumStocks = len(convertible_bond_code)
covariance = pd.DataFrame()
for FirstStock in np.arange(NumStocks-1):
    for SecondStock in np.arange(FirstStock+1,NumStocks):
        ColumnTitle = StockList[FirstStock] + '-' + StockList[SecondStock]
        covariance[ColumnTitle] = shift_returns[StockList[FirstStock]].ewm(span=filter_len).cov(shift_returns[StockList[SecondStock]])





# Variable Initialization

start_date = '2019-01-04'
index = shift_returns.index
start_index = index.get_loc(start_date)
end_date = index[-1]
end_index = index.get_loc(end_date)
date_index_iter = start_index
convertible_bond_code=(['300059.sz','000001.sz','000783.sz','300335.sz'])
StockList=convertible_bond_code
StockList.append('InterestRate')
distribution = pd.DataFrame(index=StockList)
returns = pd.Series(index=index)
# Start Value
total_value = 1.0
returns[index[date_index_iter]] = total_value
##########MarkowitzOpt_new function #######
##############################################
while date_index_iter + shift < end_index:
	date = index[date_index_iter]
	portfolio_alloc = MarkowitzOpt(shift_returns_mean.ix[date], shift_returns_var.ix[date], covariance.ix[date], interest_rate, min_return)
	distribution[date.strftime('%Y-%m-%d')] = portfolio_alloc

	# Calculating portfolio return
	date2 = index[date_index_iter+shift]
	temp1 = outdata.ix[date2]/outdata.ix[date]
	temp1.ix[StockList[-1]] = interest_rate+1
	temp2 = pd.Series(np.array(portfolio_alloc.ravel()).reshape(len(portfolio_alloc)),index=StockList)
	total_value = np.sum(total_value*temp2*temp1)
	# Increment Date
	date_index_iter += shift
	returns[index[date_index_iter]] = total_value

# Remove dates that there are no trades from returns
returns = returns[np.isfinite(returns)]



# Plot portfolio allocation of last 10 periods
ax = distribution.T.ix[-10:].plot(kind='bar',stacked=True)
plt.ylim([0,1])
plt.xlabel('Date')
plt.ylabel('distribution')
plt.title('distribution vs. Time')
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
# plt.savefig('allocation.png')

# Plot stock prices and shifted returns
fig, axes = plt.subplots(nrows=2,ncols=1)
outdata.plot(ax=axes[0])
shift_returns.plot(ax=axes[1])
axes[0].set_title('Stock Prices')
axes[0].set_xlabel('Date')
axes[0].set_ylabel('Price')
axes[0].legend(loc='center left', bbox_to_anchor=(1, 0.5))
axes[1].set_title(str(shift)+ ' Day Shift returns')
axes[1].set_xlabel('Date')
axes[1].set_ylabel('returns ' + str(shift) + ' Days Apart')
axes[1].legend(loc='center left', bbox_to_anchor=(1, 0.5))
# plt.savefig('stocks.png', pad_inches=1)
fig.tight_layout()

# Plot portfolio returns vs. time
plt.figure()
returns.plot()
plt.xlabel('Date')
plt.ylabel('Portolio returns')
plt.title('Portfolio returns vs. Time')
# plt.savefig('returns.png')

plt.show()



########################################
##########################################
#########################################
#another method 20200321

########################################
#######################################
#########################################
import matplotlib.pyplot as plt
import cvxopt as opt
from cvxopt import blas, solvers

def optimal_portfolio(returns):
    n = len(returns)
    #returns = np.asmatrix(returns)  #"ndarray is not contiguous" what a fuck error message!
    returns = returns.as_matrix(columns=None)
    N = 100
    mus = [10**(5.0 * t/N - 1.0) for t in range(N)]
    
    # Convert to cvxopt matrices
    S = opt.matrix(np.cov(returns))
    pbar = opt.matrix(np.mean(returns, axis=1))
    
    # Create constraint matrices
    G = -opt.matrix(np.eye(n))   # negative n x n identity matrix
    h = opt.matrix(0.0, (n ,1))
    A = opt.matrix(1.0, (1, n))
    b = opt.matrix(1.0)
    
    # Calculate efficient frontier weights using quadratic programming
    portfolios = [solvers.qp(mu*S, -pbar, G, h, A, b)['x'] 
                  for mu in mus]
    ## CALCULATE RISKS AND RETURNS FOR FRONTIER
    returns = [blas.dot(pbar, x) for x in portfolios]
    risks = [np.sqrt(blas.dot(x, S*x)) for x in portfolios]
    ## CALCULATE THE 2ND DEGREE POLYNOMIAL OF THE FRONTIER CURVE
    m1 = np.polyfit(returns, risks, 2)
    x1 = np.sqrt(m1[2] / m1[0])
    # CALCULATE THE OPTIMAL PORTFOLIO
    wt = solvers.qp(opt.matrix(x1 * S), -pbar, G, h, A, b)['x']
    return np.asarray(wt)
# Specify number of days to shift
shift = 1
# Compute returns over the time period specified by shift
cvxopt_returns = outdata/outdata.shift(shift) - 1

# Variable Initialization

start_date = '2019-01-04'
index = cvxopt_returns.index
start_index = index.get_loc(start_date)
end_date = index[-1]
end_index = index.get_loc(end_date)
date_index_iter = start_index
convertible_bond_code=(['300059.sz','000001.sz','000783.sz','300335.sz'])
StockList=convertible_bond_code
StockList.append('InterestRate')
distribution = pd.DataFrame(index=StockList)
returns = pd.Series(index=index)
# Start Value
total_value = 1.0
returns[index[date_index_iter]] = total_value

while date_index_iter + shift < 6:
	date = index[date_index_iter]
	index_returns=cvxopt_returns[date_index_iter-1:date_index_iter+1]
	index_returns.insert(4,'InterestRate',[0,0])
	index_returns=index_returns.T
	portfolio_alloc = optimal_portfolio(index_returns)
	distribution[date.strftime('%Y-%m-%d')] = portfolio_alloc

	# Calculating portfolio return
	date2 = index[date_index_iter+shift]
	temp1 = outdata.ix[date2]/outdata.ix[date]
	temp1.ix[StockList[-1]] = interest_rate+1
	temp2 = pd.Series(np.array(portfolio_alloc.ravel()).reshape(len(portfolio_alloc)),index=StockList)
	total_value = np.sum(total_value*temp2*temp1)
	# Increment Date
	date_index_iter += shift
	returns[index[date_index_iter]] = total_value

# Remove dates that there are no trades from returns
returns = returns[np.isfinite(returns)]

# Plot portfolio allocation of last 10 periods
ax = distribution.T.ix[-10:].plot(kind='bar',stacked=True)
plt.ylim([0,1])
plt.xlabel('Date')
plt.ylabel('distribution')
plt.title('distribution vs. Time')
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
# plt.savefig('allocation.png')

# Plot stock prices and shifted returns
fig, axes = plt.subplots(nrows=2,ncols=1)
outdata.plot(ax=axes[0])
shift_returns.plot(ax=axes[1])
axes[0].set_title('Stock Prices')
axes[0].set_xlabel('Date')
axes[0].set_ylabel('Price')
axes[0].legend(loc='center left', bbox_to_anchor=(1, 0.5))
axes[1].set_title(str(shift)+ ' Day Shift returns')
axes[1].set_xlabel('Date')
axes[1].set_ylabel('returns ' + str(shift) + ' Days Apart')
axes[1].legend(loc='center left', bbox_to_anchor=(1, 0.5))
# plt.savefig('stocks.png', pad_inches=1)
fig.tight_layout()

# Plot portfolio returns vs. time
plt.figure()
returns.plot()
plt.xlabel('Date')
plt.ylabel('Portolio returns')
plt.title('Portfolio returns vs. Time')
# plt.savefig('returns.png')

plt.show()








