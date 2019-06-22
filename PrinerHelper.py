#encoding:UTF-8  
import os
import json
import urllib  
import urllib.request
import urllib.parse
import time

Company_Id = 10
Server = "http://192.168.1.127/api/Register"
JobServer = "http://192.168.1.127/api/PrinterJobs"
DownloadPath = "/tmp/download/"

def En_Json(data):
	return json.dumps(data)

def De_Json(data):
	return json.loads(data)

def GetUrl(url,data):
	if len(data):
		url = url+"/"+data
	print(url)
	try:
		request_data = urllib.request.urlopen(url).read()
	except BaseException as err:
		return None
	else:
		return request_data.decode('UTF-8')

def PostUrl(url,data):
	data = urllib.parse.urlencode(data).encode('utf-8')
	headers = {"Content-type": "application/x-www-form-urlencoded",'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
	request = urllib.request.Request(url,data,headers)
	print(url)
	try:
		request_d = urllib.request.urlopen(request).read()
	except BaseException as err:
		return None
	else:
		return request_d.decode('utf-8')

def Shell_Con(command):
	return os.popen(command).read()

def Get_Printers():
	All_printer_msg = Shell_Con("lpstat -a").splitlines()
	All_printers = {}
	for strs in All_printer_msg:
		printername = strs.split(" accepting requests")
		if len(printername) != 2:
			continue
		else:
			statusPt = Shell_Con("lpstat -p " + printername[0])
			All_printers[printername[0]] = statusPt.split('.',1)[0]
	return All_printers

def Get_Files(filenames,conid):
	for strfilename in filenames:
		url = JobServer + "/" + str(conid) + "/" + str(strfilename)
		urllib.request.urlretrieve(url,DownloadPath+strfilename)
	return "OK"

def Log_Control():
	return None

def Server_Error(code):
	Log_Control()

def Print_Server(filename,obj_info):
	printComm = ""
	print(filename + "/"  +str(obj_info["pices"])+ "/" + str(obj_info["printer"]))
	path = DownloadPath + filename
	suffix_file = filename.split(".")[len(filename.split(".")) - 1]
	#office_suffix = ["doc","docx","xls","pptx"]
	if not len(obj_info["printer"]):
		printComm = "libreoffice --headless -pt "+ obj_info["printer"] + " " +path
	else :
		printComm = "libreoffice --headless -p " + path
	allready = 0
	while allready < int(obj_info["pices"]):
		Shell_Con(printComm)
		allready = allready + 1
	print(path)
	#os.remove(path)
	return None

def Get_Print_To_Printer_Server(company_id,con_id):
	GetJobs = GetUrl(JobServer,str(company_id))
	if not len(GetJobs):
		return
	else:
		GetJobs = De_Json(GetJobs)
	if len(GetJobs):
		status = Get_Files(GetJobs,str(company_id))
		if status == "OK":
			for filename in GetJobs:
				Print_Server(filename,GetJobs[filename])
		else:
			Server_Error(500)
 
if __name__=="__main__":
	Connection_Id = ""
	reg_get = GetUrl(Server,str(Company_Id))
	if reg_get is None:
		print("Can not connect to Server!!")
		exit()
	reg_get = De_Json(reg_get)
	if reg_get["ConName"] is not None:
		Connection_Id = reg_get["ConName"]
	All_printers = Get_Printers()
	printers = []
	for kvp in All_printers:
		printers.append(kvp)
	Update_printers = {}
	Update_printers["con"] = Connection_Id
	Update_printers["printers"] = str(printers)
	EndRegister = PostUrl(Server,Update_printers)
	ServerStat = True
	while ServerStat:
		Get_Print_To_Printer_Server(str(Company_Id),Connection_Id)
		time.sleep(5)
