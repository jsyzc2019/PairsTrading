import pandas as pd
import numpy as np
import pywt # С������
from scipy import stats 
import scipy.fftpack as fftpack # ϣ�����ر任
import itertools
import datetime as dt
#from tqdm import *
#from jqdata import *
import talib

from sklearn import preprocessing
from sklearn import svm   

import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import matplotlib.gridspec as mg # ��������ͼ
pd.plotting.register_matplotlib_converters()

# �������� ����������ʾ���ı�ǩ
mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei']
mpl.rcParams['font.family']='serif' # pd.plot����
# ����������ʾ����
mpl.rcParams['axes.unicode_minus'] = False
# ͼ������



plt.style.use('seaborn')



plt.rcParams['font.sans-serif'] = ['SimHei']  # ����������ʾ���ı�ǩ
plt.rcParams['axes.unicode_minus'] = False  # ����������ʾ����





# �ز�ģ��
import datetime
import numpy as np
import pandas as pd
import time
import copy
import pickle
from jqdata import *
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
import seaborn as sns
import itertools


# ������'��������'
class parameter_analysis(object):
    
    # ���庯���в�ͬ�ı���
    def __init__(self, algorithm_id=None):
        self.algorithm_id = algorithm_id            # �ز�id
        
        self.params_df = pd.DataFrame()             # �ز������е��α�ѡֵ�����ݣ�������Ϊ��Ӧ�޸��������ƣ���Ӧ�ز��е� g.XXXX
        self.results = {}                           # �ز����Ļر��ʣ�key Ϊ params_df ������ţ�value Ϊ
        self.evaluations = {}                       # �ز����ĸ���ָ�꣬key Ϊ params_df ������ţ�value Ϊһ�� dataframe
        self.backtest_ids = {}                      # �ز����� id
        
        # �¼���Ļ�׼�Ļز��� id������Ĭ��Ϊ�� ''����ʹ�ûز����趨�Ļ�׼
        self.benchmark_id = 'f16629492d6b6f4040b2546262782c78'                      
        
        self.benchmark_returns = []                 # �¼���Ļ�׼�Ļز�ر���
        self.returns = {}                           # ��¼���лر���
        self.excess_returns = {}                    # ��¼����������
        self.log_returns = {}                       # ��¼�����ʵ� log ֵ
        self.log_excess_returns = {}                # ��¼��������� log ֵ
        self.dates = []                             # �ز��Ӧ����������
        self.excess_max_drawdown = {}               # ���㳬����������س�
        self.excess_annual_return = {}              # ���㳬�������ʵ��껯ָ��
        self.evaluations_df = pd.DataFrame()        # ��¼����ز�ָ�꣬���ջر�����
        self.failed_list= []
    
    # �����Ŷ����ж�����ز⺯��
    def run_backtest(self,                          #
                     algorithm_id=None,             # �ز����id
                     running_max=10,                # �ز���ͬʱѲ�����ز�����
                     start_date='2006-01-01',       # �ز����ʼ����
                     end_date='2016-11-30',         # �ز�Ľ�������
                     frequency='day',               # �ز������Ƶ��
                     initial_cash='1000000',        # �ز�ĳ�ʼ�ֲֽ��
                     param_names=[],                # �ز��е��������漰�ı���
                     param_values=[],               # �ز���ÿ�������ı�ѡ����ֵ
                     python_version = 2,            # �ز��python�汾
                     use_credit =False              # �Ƿ��������Ļ��ּ����ز�
                     ):
        # ���˴��ز���Ե� id û�и���ʱ������������Ĳ��� id
        if algorithm_id == None: algorithm_id=self.algorithm_id
        
        # �������в�����ϲ����ص� df ��
        # �����˲�ͬ�������屸ѡֵ�����������һ������� tuple �� list
        param_combinations = list(itertools.product(*param_values))
        # ����һ�� dataframe�� ��Ӧ����Ϊÿ�����εı�����ÿ��ֵΪ���ζ�Ӧ�ı�ѡֵ
        to_run_df = pd.DataFrame(param_combinations,dtype='object')
        # �޸�������Ϊ���α���������
        to_run_df.columns = param_names
        
        # �趨������ʼʱ��ͱ����ʽ
        start = time.time()
        # ��¼���������лز�
        finished_backtests = {}
        # ��¼�����еĻز�
        running_backtests = {}
        # ������
        pointer = 0
        # �����лز���Ŀ��������������е�Ԫ�ظ���
        total_backtest_num = len(param_combinations)
        # ��¼�ز����Ļر���
        all_results = {}
        # ��¼�ز����ĸ���ָ��
        all_evaluations = {}
        
        # �����п�ʼʱ��ʾ
        print(('�������|������|�����С�:'), end=' ') 
        # �����лز⿪ʼ�����û��ȫ��������ȫ�Ļ���
        while len(finished_backtests)<total_backtest_num:
            # ��ʾ���С���ɺʹ����еĻز����
            print(('[%s|%s|%s].' % (len(finished_backtests), 
                                   len(running_backtests), 
                                   (total_backtest_num-len(finished_backtests)-len(running_backtests)) )), end=' ')
            # ��¼��ǰ�����еĿ�λ����
            to_run = min(running_max-len(running_backtests), total_backtest_num-len(running_backtests)-len(finished_backtests))
            # �ѿ��õĿ�λ�����ܻز�
            for i in range(pointer, pointer+to_run):
                # ��ѡ�Ĳ���������ϵ� df �е� i �б�� dict��ÿ�� key Ϊ�����֣�value Ϊ df �ж�Ӧ��ֵ
                params = to_run_df.iloc[i].to_dict()
                # ��¼���Իز����� id���������� extras ʹ�� params ������
                backtest = create_backtest(algorithm_id = algorithm_id,
                                           start_date = start_date, 
                                           end_date = end_date, 
                                           frequency = frequency, 
                                           initial_cash = initial_cash, 
                                           extras = params, 
                                           # �ٻز��аѸĲ����Ľ����һ�����֣������������漰�ı�������ֵ
                                           name = str(params),
                                           python_version = python_version,
                                           use_credit = use_credit
                                           )
                # ��¼������ i �ز�Ļز� id
                running_backtests[i] = backtest
            # ���������������������    
            pointer = pointer+to_run
            
            # ��ȡ�ز���
            failed = []
            finished = []
            # ���������еĻز⣬key Ϊ to_run_df ��������������е�����
            for key in list(running_backtests.keys()):
                # �о����ûز�Ľ����running_backtests[key] Ϊ�����б���Ľ�� id
                back_id = running_backtests[key]
                bt = get_backtest(back_id)
                # ������лز�����״̬���ɹ���ʧ�ܶ���Ҫ���н����󷵻أ����û�з���������û�н���
                status = bt.get_status()
                # �����лز�ʧ��
                if status == 'failed':
                    # ʧ�� list �м�¼��Ӧ�Ļز��� id
                    print('')
                    print(('�ز�ʧ�� : https://www.joinquant.com/algorithm/backtest/detail?backtestId='+back_id))
                    failed.append(key) 
                # �����лز�ɹ�ʱ
                elif status == 'done':
                    # �ɹ� list ��¼��Ӧ�Ļز��� id��finish ����¼���гɹ���
                    finished.append(key)
                    # �ز�ر��ʼ�¼��Ӧ�ز�Ļر��� dict�� key to_run_df ��������������е������� value Ϊ�ر��ʵ� dict
                    # ÿ�� value һ�� list ÿ������Ϊһ������ʱ�䡢�ջر��ʺͻ�׼�ر��ʵ� dict
                    all_results[key] = bt.get_results()
                    # �ز�ر��ʼ�¼��Ӧ�ز���ָ�� dict�� key to_run_df ��������������е������� value Ϊ�ز���ָ��� dataframe
                    all_evaluations[key] = bt.get_risk()
            # ��¼�����лز��� id �� list ��ɾ��ʧ�ܵ�����
            for key in failed:
                finished_backtests[key] = running_backtests.pop(key)
            # �ڽ����ز��� dict �м�¼���гɹ��Ļز��� id��ͬʱ�������еļ�¼��ɾ���ûز�
            for key in finished:
                finished_backtests[key] = running_backtests.pop(key)
#                 print (finished_backtests)
            # ��һ��ͬʱ���еĻز����ʱ����ʱ��
            if len(finished_backtests) != 0 and len(finished_backtests) % running_max == 0 and to_run !=0:
                # ��¼��ʱʱ��
                middle = time.time()
                # ����ʣ��ʱ�䣬����û������ʱ����ȵĻ�
                remain_time = (middle - start) * (total_backtest_num - len(finished_backtests)) / len(finished_backtests)
                # print ��ǰ����ʱ��
                print(('[����%sʱ,����%sʱ,�벻Ҫ�ر������].' % (str(round((middle - start) / 60.0 / 60.0,3)), 
                                          str(round(remain_time / 60.0 / 60.0,3)))), end=' ')
            self.failed_list  += failed
            # 5���Ӻ�����һ��
            time.sleep(5) 
        # ��¼����ʱ��
        end = time.time() 
        print('')
        print(('���ز���ɡ�����ʱ��%s��(��%sСʱ)��' % (str(int(end-start)), 
                                           str(round((end-start)/60.0/60.0,2)))), end=' ')
#         print (to_run_df,all_results,all_evaluations,finished_backtests)
        # ��Ӧ�޸����ڲ���Ӧ
#         to_run_df = {key:value for key,value in returns.items() if key not in faild}
        self.params_df = to_run_df
#         all_results = {key:value for key,value in all_results.items() if key not in faild}
        self.results = all_results
#         all_evaluations = {key:value for key,value in all_evaluations.items() if key not in faild}
        self.evaluations = all_evaluations
#         finished_backtests = {key:value for key,value in finished_backtests.items() if key not in faild}
        self.backtest_ids = finished_backtests

        
    #7 ���س����㷽��
    def find_max_drawdown(self, returns):
        # �������س��ı���
        result = 0
        # ��¼��ߵĻر��ʵ�
        historical_return = 0
        # ������������
        for i in range(len(returns)):
            # ��߻ر��ʼ�¼
            historical_return = max(historical_return, returns[i])
            # ���س���¼
            drawdown = 1-(returns[i] + 1) / (historical_return + 1)
            # ��¼���س�
            result = max(drawdown, result)
        # �������س�ֵ
        return result

    # log ���桢�»�׼�³��������������»�׼�����س�
    def organize_backtest_results(self, benchmark_id=None):
        # ���»�׼�Ļز��� id û����
        if benchmark_id==None:
            # ʹ��Ĭ�ϵĻ�׼�ر��ʣ�Ĭ�ϵĻ�׼�ڻز�������趨
            self.benchmark_returns = [x['benchmark_returns'] for x in self.results[0]]
        # ���»�׼ָ�������    
        else:
            # ��׼ʹ���¼���Ļ�׼�ز���
            self.benchmark_returns = [x['returns'] for x in get_backtest(benchmark_id).get_results()]
        # �ز�����Ϊ����м�¼�ĵ�һ���Ӧ������
        self.dates = [x['time'] for x in self.results[0]]
        
        # ��Ӧÿ���ز������б�ѡ�ز��е�˳�� ��key��������������
        # �� {key��{u'benchmark_returns': 0.022480100091729405,
        #           u'returns': 0.03184566700000002,
        #           u'time': u'2006-02-14'}} ��ʽת��Ϊ��
        # {key: []} ��ʽ������ list Ϊ��Ӧ date ��һ���ر��� list
        for key in list(self.results.keys()):
            self.returns[key] = [x['returns'] for x in self.results[key]]
        # ���ɶ��ڻ�׼�����»�׼���ĳ���������
        for key in list(self.results.keys()):
            self.excess_returns[key] = [(x+1)/(y+1)-1 for (x,y) in zip(self.returns[key], self.benchmark_returns)]
        # ���� log ��ʽ��������
        for key in list(self.results.keys()):
            self.log_returns[key] = [log(x+1) for x in self.returns[key]]
        # ���ɳ��������ʵ� log ��ʽ
        for key in list(self.results.keys()):
            self.log_excess_returns[key] = [log(x+1) for x in self.excess_returns[key]]
        # ���ɳ��������ʵ����س�
        for key in list(self.results.keys()):
            self.excess_max_drawdown[key] = self.find_max_drawdown(self.excess_returns[key])
        # �����껯����������
        for key in list(self.results.keys()):
            self.excess_annual_return[key] = (self.excess_returns[key][-1]+1)**(252./float(len(self.dates)))-1
        # �ѵ��������еĲ������ df ���Ӧ����� df ���кϲ�
        self.evaluations_df = pd.concat([self.params_df, pd.DataFrame(self.evaluations).T], axis=1)
#         self.evaluations_df = 

    # ��ȡ���ܷ������ݣ������Ŷӻز⺯������������ĺ���    
    def get_backtest_data(self,
                          algorithm_id=None,                         # �ز����id
                          benchmark_id=None,                         # �»�׼�ز���id
                          file_name='results.pkl',                   # �������� pickle �ļ�����
                          running_max=10,                            # ���ͬʱ���лز�����
                          start_date='2006-01-01',                   # �ز⿪ʼʱ��
                          end_date='2016-11-30',                     # �ز��������
                          frequency='day',                           # �ز������Ƶ��
                          initial_cash='1000000',                    # �ز��ʼ�ֲ��ʽ�
                          param_names=[],                            # �ز���Ҫ���Եı���
                          param_values=[],                           # ��Ӧÿ�������ı�ѡ����
                          python_version = 2,
                          use_credit = False
                          ):
        # �����Ŷӻز⺯�������ݶ�Ӧ����
        self.run_backtest(algorithm_id=algorithm_id,
                          running_max=running_max,
                          start_date=start_date,
                          end_date=end_date,
                          frequency=frequency,
                          initial_cash=initial_cash,
                          param_names=param_names,
                          param_values=param_values,
                          python_version = python_version,
                          use_credit = use_credit,
                          )
        # �ز���ָ���м��� log �����ʺͳ��������ʵ�ָ��
        self.organize_backtest_results(benchmark_id)
        # ���� dict �������н����
        results = {'returns':self.returns,
                   'excess_returns':self.excess_returns,
                   'log_returns':self.log_returns,
                   'log_excess_returns':self.log_excess_returns,
                   'dates':self.dates,
                   'benchmark_returns':self.benchmark_returns,
                   'evaluations':self.evaluations,
                   'params_df':self.params_df,
                   'backtest_ids':self.backtest_ids,
                   'excess_max_drawdown':self.excess_max_drawdown,
                   'excess_annual_return':self.excess_annual_return,
                   'evaluations_df':self.evaluations_df,
                    "failed_list" : self.failed_list}
        # ���� pickle �ļ�
        pickle_file = open(file_name, 'wb')
        pickle.dump(results, pickle_file)
        pickle_file.close()

    # ��ȡ����� pickle �ļ����������еĶ�������Ӧ�ı�������    
    def read_backtest_data(self, file_name='results.pkl'):
        pickle_file = open(file_name, 'rb')
        results = pickle.load(pickle_file)
        self.returns = results['returns']
        self.excess_returns = results['excess_returns']
        self.log_returns = results['log_returns']
        self.log_excess_returns = results['log_excess_returns']
        self.dates = results['dates']
        self.benchmark_returns = results['benchmark_returns']
        self.evaluations = results['evaluations']
        self.params_df = results['params_df']
        self.backtest_ids = results['backtest_ids']
        self.excess_max_drawdown = results['excess_max_drawdown']
        self.excess_annual_return = results['excess_annual_return']
        self.evaluations_df = results['evaluations_df']
        self.failed_list =  results['failed_list']
    # �ر�������ͼ    
    def plot_returns(self):
        # ͨ��figsize��������ָ����ͼ����Ŀ�Ⱥ͸߶ȣ���λΪӢ�磻
        fig = plt.figure(figsize=(20,8))
        ax = fig.add_subplot(111)
        # ��ͼ
        for key in list(self.returns.keys()):
            ax.plot(list(range(len(self.returns[key]))), self.returns[key], label=key)
        # �趨benchmark���߲����
        ax.plot(list(range(len(self.benchmark_returns))), self.benchmark_returns, label='benchmark', c='k', linestyle='--') 
        ticks = [int(x) for x in np.linspace(0, len(self.dates)-1, 11)]
        plt.xticks(ticks, [self.dates[i] for i in ticks])
        # ����ͼ����ʽ
        ax.legend(loc = 2, fontsize = 10)
        # ����y��ǩ��ʽ
        ax.set_ylabel('returns',fontsize=20)
        # ����x��ǩ��ʽ
        ax.set_yticklabels([str(x*100)+'% 'for x in ax.get_yticks()])
        # ����ͼƬ������ʽ
        ax.set_title("Strategy's performances with different parameters", fontsize=21)
        plt.xlim(0, len(self.returns[0]))

    # ����������ͼ    
    def plot_excess_returns(self):
        # ͨ��figsize��������ָ����ͼ����Ŀ�Ⱥ͸߶ȣ���λΪӢ�磻
        fig = plt.figure(figsize=(20,8))
        ax = fig.add_subplot(111)
        # ��ͼ
        for key in list(self.returns.keys()):
            ax.plot(list(range(len(self.excess_returns[key]))), self.excess_returns[key], label=key)
        # �趨benchmark���߲����
        ax.plot(list(range(len(self.benchmark_returns))), [0]*len(self.benchmark_returns), label='benchmark', c='k', linestyle='--')
        ticks = [int(x) for x in np.linspace(0, len(self.dates)-1, 11)]
        plt.xticks(ticks, [self.dates[i] for i in ticks])
        # ����ͼ����ʽ
        ax.legend(loc = 2, fontsize = 10)
        # ����y��ǩ��ʽ
        ax.set_ylabel('excess returns',fontsize=20)
        # ����x��ǩ��ʽ
        ax.set_yticklabels([str(x*100)+'% 'for x in ax.get_yticks()])
        # ����ͼƬ������ʽ
        ax.set_title("Strategy's performances with different parameters", fontsize=21)
        plt.xlim(0, len(self.excess_returns[0]))
        
    # log�ر���ͼ    
    def plot_log_returns(self):
        # ͨ��figsize��������ָ����ͼ����Ŀ�Ⱥ͸߶ȣ���λΪӢ�磻
        fig = plt.figure(figsize=(20,8))
        ax = fig.add_subplot(111)
        # ��ͼ
        for key in list(self.returns.keys()):
            ax.plot(list(range(len(self.log_returns[key]))), self.log_returns[key], label=key)
        # �趨benchmark���߲����
        ax.plot(list(range(len(self.benchmark_returns))), [log(x+1) for x in self.benchmark_returns], label='benchmark', c='k', linestyle='--')
        ticks = [int(x) for x in np.linspace(0, len(self.dates)-1, 11)]
        plt.xticks(ticks, [self.dates[i] for i in ticks])
        # ����ͼ����ʽ
        ax.legend(loc = 2, fontsize = 10)
        # ����y��ǩ��ʽ
        ax.set_ylabel('log returns',fontsize=20)
        # ����ͼƬ������ʽ
        ax.set_title("Strategy's performances with different parameters", fontsize=21)
        plt.xlim(0, len(self.log_returns[0]))
    
    # ���������ʵ� log ͼ
    def plot_log_excess_returns(self):
        # ͨ��figsize��������ָ����ͼ����Ŀ�Ⱥ͸߶ȣ���λΪӢ�磻
        fig = plt.figure(figsize=(20,8))
        ax = fig.add_subplot(111)
        # ��ͼ
        for key in list(self.returns.keys()):
            ax.plot(list(range(len(self.log_excess_returns[key]))), self.log_excess_returns[key], label=key)
        # �趨benchmark���߲����
        ax.plot(list(range(len(self.benchmark_returns))), [0]*len(self.benchmark_returns), label='benchmark', c='k', linestyle='--')
        ticks = [int(x) for x in np.linspace(0, len(self.dates)-1, 11)]
        plt.xticks(ticks, [self.dates[i] for i in ticks])
        # ����ͼ����ʽ
        ax.legend(loc = 2, fontsize = 10)
        # ����y��ǩ��ʽ
        ax.set_ylabel('log excess returns',fontsize=20)
        # ����ͼƬ������ʽ
        ax.set_title("Strategy's performances with different parameters", fontsize=21)
        plt.xlim(0, len(self.log_excess_returns[0]))

        
    # �ز��4����Ҫָ�꣬�����ܻر��ʡ����س������ʺͲ���
    def get_eval4_bar(self, sort_by=[]): 
        
        sorted_params = self.params_df
        for by in sort_by:
            sorted_params = sorted_params.sort(by)
        indices = sorted_params.index
        indices = set(sorted_params.index)-set(self.failed_list)
        fig = plt.figure(figsize=(20,7))

        # ����λ��
        ax1 = fig.add_subplot(221)
        # �趨����Ϊ��Ӧ��λ������Ϊ��Ӧָ��
        ax1.bar(list(range(len(indices))), 
                [self.evaluations[x]['algorithm_return'] for x in indices], 0.6, label = 'Algorithm_return')
        plt.xticks([x+0.3 for x in range(len(indices))], indices)
        # ����ͼ����ʽ
        ax1.legend(loc='best',fontsize=15)
        # ����y��ǩ��ʽ
        ax1.set_ylabel('Algorithm_return', fontsize=15)
        # ����y��ǩ��ʽ
        ax1.set_yticklabels([str(x*100)+'% 'for x in ax1.get_yticks()])
        # ����ͼƬ������ʽ
        ax1.set_title("Strategy's of Algorithm_return performances of different quantile", fontsize=15)
        # x�᷶Χ
        plt.xlim(0, len(indices))

        # ����λ��
        ax2 = fig.add_subplot(224)
        # �趨����Ϊ��Ӧ��λ������Ϊ��Ӧָ��
        ax2.bar(list(range(len(indices))), 
                [self.evaluations[x]['max_drawdown'] for x in indices], 0.6, label = 'Max_drawdown')
        plt.xticks([x+0.3 for x in range(len(indices))], indices)
        # ����ͼ����ʽ
        ax2.legend(loc='best',fontsize=15)
        # ����y��ǩ��ʽ
        ax2.set_ylabel('Max_drawdown', fontsize=15)
        # ����x��ǩ��ʽ
        ax2.set_yticklabels([str(x*100)+'% 'for x in ax2.get_yticks()])
        # ����ͼƬ������ʽ
        ax2.set_title("Strategy's of Max_drawdown performances of different quantile", fontsize=15)
        # x�᷶Χ
        plt.xlim(0, len(indices))

        # ����λ��
        ax3 = fig.add_subplot(223)
        # �趨����Ϊ��Ӧ��λ������Ϊ��Ӧָ��
        ax3.bar(list(range(len(indices))),
                [self.evaluations[x]['sharpe'] for x in indices], 0.6, label = 'Sharpe')
        plt.xticks([x+0.3 for x in range(len(indices))], indices)
        # ����ͼ����ʽ
        ax3.legend(loc='best',fontsize=15)
        # ����y��ǩ��ʽ
        ax3.set_ylabel('Sharpe', fontsize=15)
        # ����x��ǩ��ʽ
        ax3.set_yticklabels([str(x*100)+'% 'for x in ax3.get_yticks()])
        # ����ͼƬ������ʽ
        ax3.set_title("Strategy's of Sharpe performances of different quantile", fontsize=15)
        # x�᷶Χ
        plt.xlim(0, len(indices))

        # ����λ��
        ax4 = fig.add_subplot(222)
        # �趨����Ϊ��Ӧ��λ������Ϊ��Ӧָ��
        ax4.bar(list(range(len(indices))), 
                [self.evaluations[x]['algorithm_volatility'] for x in indices], 0.6, label = 'Algorithm_volatility')
        plt.xticks([x+0.3 for x in range(len(indices))], indices)
        # ����ͼ����ʽ
        ax4.legend(loc='best',fontsize=15)
        # ����y��ǩ��ʽ
        ax4.set_ylabel('Algorithm_volatility', fontsize=15)
        # ����x��ǩ��ʽ
        ax4.set_yticklabels([str(x*100)+'% 'for x in ax4.get_yticks()])
        # ����ͼƬ������ʽ
        ax4.set_title("Strategy's of Algorithm_volatility performances of different quantile", fontsize=15)
        # x�᷶Χ
        plt.xlim(0, len(indices))
        
    #14 �껯�ر������س�������˫ɫ��ʾ
    def get_eval(self, sort_by=[]):

        sorted_params = self.params_df
        for by in sort_by:
            sorted_params = sorted_params.sort(by)
        indices = sorted_params.index
        indices = set(sorted_params.index)-set(self.failed_list)
        # ��С
        fig = plt.figure(figsize = (20, 8))
        # ͼ1λ��
        ax = fig.add_subplot(111)
        # ����ͼ���������ʵ����س�
        ax.bar([x+0.3 for x in range(len(indices))],
               [-self.evaluations[x]['max_drawdown'] for x in indices], color = '#32CD32',  
                     width = 0.6, label = 'Max_drawdown', zorder=10)
        # ͼ�껯��������
        ax.bar([x for x in range(len(indices))],
               [self.evaluations[x]['annual_algo_return'] for x in indices], color = 'r', 
                     width = 0.6, label = 'Annual_return')
        plt.xticks([x+0.3 for x in range(len(indices))], indices)
        # ����ͼ����ʽ
        ax.legend(loc='best',fontsize=15)
        # ��׼��
        plt.plot([0, len(indices)], [0, 0], c='k', 
                 linestyle='--', label='zero')
        # ����ͼ����ʽ
        ax.legend(loc='best',fontsize=15)
        # ����y��ǩ��ʽ
        ax.set_ylabel('Max_drawdown', fontsize=15)
        # ����x��ǩ��ʽ
        ax.set_yticklabels([str(x*100)+'% 'for x in ax.get_yticks()])
        # ����ͼƬ������ʽ
        ax.set_title("Strategy's performances of different quantile", fontsize=15)
        #   �趨x�᳤��
        plt.xlim(0, len(indices))


    #14 ����������껯�ر������س�
    # �����µ�benchmark�󳬶������
    def get_excess_eval(self, sort_by=[]):

        sorted_params = self.params_df
        for by in sort_by:
            sorted_params = sorted_params.sort(by)
        indices = sorted_params.index
        indices = set(sorted_params.index)-set(self.failed_list)
        # ��С
        fig = plt.figure(figsize = (20, 8))
        # ͼ1λ��
        ax = fig.add_subplot(111)
        # ����ͼ���������ʵ����س�
        ax.bar([x+0.3 for x in range(len(indices))],
               [-self.excess_max_drawdown[x] for x in indices], color = '#32CD32',  
                     width = 0.6, label = 'Excess_max_drawdown')
        # ͼ�껯��������
        ax.bar([x for x in range(len(indices))],
               [self.excess_annual_return[x] for x in indices], color = 'r', 
                     width = 0.6, label = 'Excess_annual_return')
        plt.xticks([x+0.3 for x in range(len(indices))], indices)
        # ����ͼ����ʽ
        ax.legend(loc='best',fontsize=15)
        # ��׼��
        plt.plot([0, len(indices)], [0, 0], c='k', 
                 linestyle='--', label='zero')
        # ����ͼ����ʽ
        ax.legend(loc='best',fontsize=15)
        # ����y��ǩ��ʽ
        ax.set_ylabel('Max_drawdown', fontsize=15)
        # ����x��ǩ��ʽ
        ax.set_yticklabels([str(x*100)+'% 'for x in ax.get_yticks()])
        # ����ͼƬ������ʽ
        ax.set_title("Strategy's performances of different quantile", fontsize=15)
        #   �趨x�᳤��

print('�鿴С�������壺',pywt.families())
print('�鿴symС�����µ����к�����',pywt.wavelist(family='sym',kind='all'))
print('�鿴mode�����з���:',pywt.Modes.modes)  


#С����ֵ����

# �ź�ȥ��
class DenoisingThreshold(object):
    '''
    ��ȡС��ȥ�����ֵ
    1. CalSqtwolog �̶���ֵ׼��(sqtwolog)
    2. CalRigrsure ��ƫ���չ���׼��rigrsure��
    3. CalMinmaxi ��С����׼�� minimaxi��
    4. CalHeursure
    
    �ο���https://wenku.baidu.com/view/63d62a818762caaedd33d463.html
    
    �Թ�Ʊ�۸�����ݶ��ԣ����ź�Ƶ�ʽ��ٵ��������ص���˿���ѡ��sqtwolog��heursure׼��ʹȥ��Ч�������ԡ� 
    ���������������ĸ�Ƶ���ݣ��������ñ��ص� rigrsure �� minimaxi ׼����ȷ����ֵ���Ա����϶���źš�
    '''
    

    def __init__(self,signal: np.array):

        self.signal = signal

        self.N = len(signal)

    # �̶���ֵ׼��(sqtwolog)
    @property
    def CalSqtwolog(self) -> float:

        return np.sqrt(2 * np.log(self.N))

   
    # ��ƫ���չ���׼��rigrsure��
    @property
    def CalRigrsure(self)->float:

        N = self.N
        signal = np.abs(self.signal)
        signal = np.sort(signal)
        signal = np.power(signal, 2)

        risk_j = np.zeros(N)

        for j in range(N):

            if j == 0:
                risk_j[j] = 1 + signal[N - 1]
            else:
                risk_j[j] = (N - 2 * j + (N - j) *
                             (signal[N - j]) + np.sum(signal[:j])) / N

        k = risk_j.argmin()

        return np.sqrt(signal[k])

    # ��С����׼�� minimaxi��
    @property
    def CalMinmaxi(self)->float:
        
        if self.N > 32:
            # N>32 ����ʹ��minmaxi��ֵ ��֮��Ϊ0
            return 0.3936 + 0.1829 * (np.log(self.N) / np.log(2))
        
        else:
            
            return 0

    @property
    def GetCrit(self)->float:

        return np.sqrt(np.power(np.log(self.N) / np.log(2), 3) * 1 / self.N)

    @property
    def GetEta(self)->float:

        return (np.sum(np.abs(self.signal)**2) - self.N) / self.N
    
    #���׼��heursure��
    @property
    def CalHeursure(self):

        if self.GetCrit > self.GetEta:

            #print('�Ƽ�ʹ��sqtwolog��ֵ')
            return self.CalSqtwolog
            
        else:

            #print('�Ƽ�ʹ�� Min(sqtwolog��ֵ,rigrsure��ֵ)')
            return min(self.CalRigrsure,self.CalSqtwolog)



# ���ݻ�ȡ                              
HS300 = my_pro.query('index_daily', ts_code='000300.SH', 
start_date='20140101', end_date='20200531',fields='trade_date,close') 
HS300.index=HS300['trade_date']
HS300=pd.DataFrame(HS300['adj_nav'])
HS300=HS300.sort_index()
HS300.index=[datetime.strptime(x,'%Y%m%d') for x in HS300.index]
#HS300 = get_price('000300.XSHG','2014-01-01','2020-05-31',fields='close',panel=False)
HS300.columns = ['HS300']
HS300.head()  



HS300_data=distributed_query(my_pro.index_daily,
                                   '000300.SH',
                                   '20130101',
                                   '20200531',
                                   fields='trade_date,high,low,amount,pre_close,close')
                                   
HS300_data.index=HS300_data['trade_date']
HS300_data.rename(columns={ 'amount':'money'}, inplace = True)
HS300_data=HS300_data.drop(columns=['trade_date'])
HS300_data = HS300_data.dropna()
HS300_data.head()
HS300_data.index=[datetime.strptime(x,'%Y%m%d') for x in HS300_data.index]

test[test.name.str.contains('300')]                