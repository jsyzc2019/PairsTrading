from WindPy import *
w.start()

class MyOrder(): 
      #def __init__(self):
            #"�˳��µ�"��ť�¼�
    def login(self):
                
        LoginID=w.tlogon("0000","0","w1461511901","login123","SHSZ")
        print(LoginID)
      #��½�˻�, ���ص�½ID
    def windorder(self,stock_code,trade_side,amount):       
        price=w.wsq(stock_code,'rt_last').Data[0]
        windorder_return=w.torder(stock_code,trade_side,price,amount,logonid=1)
        print(windorder_return)	
    #�ǳ����˻�
    def logout(self):
        w.tlogout()
        self.close()
	
if __name__ == "__main__":
    
    order_excel = MyOrder()
    order_excel.login()
    order_excel.windorder()
    #order_excel.logout()



#��ѯ��¼�˺�
#w.tquery("LoginID")

#��ѯ�ʽ����
#w.tquery("Order",logonid=1)

#��ί�����
#w.tquery("Order",logonid=1)

#�鵱Ȼ�ɽ����
#w.tquery("Trade",logonid=1)










w.tlogout(0)


