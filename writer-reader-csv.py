#�������д��CSV�ļ�
import csv
data = [
    ("SH", "600000.SH", 1000,'buy'),
    ("SZ", "000001.SZ", 1000,'buy'),
    ("SH", "600004.SH", 1000,'buy')
]

#Python3.4�Ժ���·�ʽ�������������
with open('c://excel-export//write.csv', 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    for list in data:
        print(list)
        csv_writer.writerow(list)

       
#��ȡcsv�ļ�����
import csv
stock_code  = []
trade_side  = []
reader = csv.reader(open("c://excel-export//write.csv"))
#csv�����������ݣ�������ȡʱʹ���ĸ������ֱ��Ӧ
for market, code, amount,tradeside in reader:
  stock_code.append(code)
  trade_side.append(tradeside)
  print(market, "; ",  code , "; ",  amount,"; ",  tradeside)

print(stock_code)
print(trade_side)




##########ֱ���µ�###############


import csv
stock_code  = []
trade_side  = []
reader = csv.reader(open("c://excel-export//write.csv"))
#csv�����������ݣ�������ȡʱʹ�����������ֱ��Ӧ
for market, code, amount,tradeside in reader:
  stock_code.append(code)
  trade_side.append(tradeside)
  print(market,"; ",code,"; ",amount,"; ",tradeside)

print(stock_code)
print(trade_side)


order_excel = MyOrder()
order_excel.login()
order_excel.windorder(stock_code,trade_side)