
# optimize msg update to refresh only the new detected address / thread 
# block xvk untill connected? task can be scheduled ?
# create connection sound ?
# bug tx history not showing to from 
# add tab get free arr change for testing 

# save pass hash to ensure it is correct ? have pass per wallet / db 

# install psutil
# pycryptodome
# python -m pip install pywin32

# todo:
# soft wrap view key export 

import os
import sys
import queue
import time
from PySide2.QtWidgets import QApplication

app = QApplication( )

import modules.gui as gui


import modules.wallet_tab as wallet_tab
import modules.wallet_api as wallet_api
import modules.msg as msg
import modules.donate as donate
import modules.addr_book as addr_book
from modules.wallet_display_set import WalDispSet


from modules.init_checks import InitApp

init_app=InitApp()



tabs0=gui.Tabs(None)

new_root=gui.MainWindow(title="zUndernet",central_widget=tabs0)
new_root.setOnClose(init_app.on_closing)
new_root.show()


queue_start_stop = queue.Queue()	

wds=WalDispSet([init_app.app_password] )
wata=wallet_tab.WalletTab(init_app.autostart,queue_start_stop, wds)


tabs0.insertTab( tab_dict={'Wallet':wata.tabs1})

wds.sending_signal.connect(wata.updateWalletDisplay)
	
	
def uploadTabs():

	###################################################  address book

	addrb=addr_book.AddressBook( wds)
	tabs0.insertTab( tab_dict={'Address Book':addrb.setaddrbook()})

	mmm=msg.Msg( addrb )
	tabs0.insertTab( tab_dict={'Messages':mmm.parent_frame})
	###################################################  donate
	tabs0.insertTab( tab_dict={'Donate':donate.donate(None,wds)})
	
	
	
	wata.init_additional_tabs(addrb)
	# now need a thread with separate deamon running 
	# print('b4 dmn init')
	dmn=init_app.dmn
	dmn.sending_signal.connect(wata.updateWalletDisplay)
	dmn.msg_signal.connect(wata.display_message)
	dmn.msg_signal_list.connect(wata.display_list)
	dmn.start_stop_enable.connect(wata.enableStartStop)
	dmn.start_stop_enable.connect(wata.settings.updatePassChangeState )
	dmn.wallet_status_update.connect(wata.updateStatus)
	dmn.set_wallet_widgets(wds) #,wata,task_history=None,txhi=None,notif=None,messages=None)
	dmn.update_addr_book.connect(addrb.refresh_addr_book)
	dmn.update_addr_book.connect(wds.addr_book_data_refresh)
	dmn.refresh_msgs_signal.connect(mmm.update_msgs)


	wrk=wallet_tab.Worker(init_app, queue_start_stop, dmn)

	wrk_thread=gui.QThread(parent=new_root)
	wrk.moveToThread(wrk_thread)
	wrk_thread.finished.connect(wrk_thread.deleteLater)
	wrk.finished.connect(wrk_thread.quit)
	wrk.finished.connect(wrk.deleteLater)
	wrk.refreshed.connect(wata.updateWalletDisplay)
	# wrk.msg.connect(wata.display_message)

	wrk_thread.started.connect(wrk.run)
	# print('thread start')
	wrk_thread.start()
	# print(wrk)
	# print(wrk_thread)
	new_root.setWorker(wrk,wrk_thread)



gui.QTimer.singleShot(1000,uploadTabs)


app.exec_()
