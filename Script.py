import re
import subprocess
import os
from optparse import OptionParser

root=os.getcwd()
def parsertxt(filename):
	value_re=re.compile('\n')
	info=[]
	with open(filename,'r') as inputfile:
		value=inputfile.readlines()
	for line in value:
		list1=line.split('  ')
		list1 = [t for t in list1 if t != ''] #remove ' '
		c=''.join(list1[1:])
		b=value_re.sub('',c)
		if "|" in b:
			a=b.split("|")
			tmp=[list1[0],a[0],a[1]]
		else:
			tmp=[list1[0],b]
		info.append(tmp)
	return info

def DEC_INF_test(txtfile,decfile,inffile):
	value=parsertxt(txtfile)
	try:
		with open(decfile,'a+') as dec:
			dec.write('\n')
			for i in range(len(value)):
				dec.write('  gEfiStructuredPcdPkgTokenSpaceGuid.JUSTFORTEST%d|%s|%s|0x%08x\n'%(i,value[i][1],value[i][0],(int('0x00010076',16)+i)))
		with open(inffile,'a+') as inf:
			inf.write('\n')
			for i in range(len(value)):
				inf.write('  gEfiStructuredPcdPkgTokenSpaceGuid.JUSTFORTEST%d\n'%i)
		print "Modify File Successful"
	except Exception,e:
		print "Modify File Error"+str(e)

def parserdsc(filename):
	section_re=re.compile('(\S+)]\n')
	info_dict={};info_list=[]
	with open(filename,'r')as dsc:
		read=dsc.read()
	section=read.split('\n[')
	for Q in section:
		sec=section_re.findall(Q)
		if sec:
			if 'Pcd' in sec[0]:
				line=Q.split('\n',1)
				x=['[%s'%line[0]]
				line=x+line[1:]
				info_list.append([sec[0],line])
	for i in range(len(info_list)):
		info_dict[i]=info_list[i]
	return info_dict
	
def DSC_DEC_test(txtfile,Dscfile,Decfile,switch):
	value=parsertxt(txtfile)
	dsc=parserdsc(Dscfile)
	value_txt=[]
	print "Select for test"
	for i in dsc.keys():
		print '%s: %s'%(i,dsc[i][0])
	num=raw_input('Input the num:')
	if int(num) not in dsc.keys():
		print "!"*10+"ERROR: Input Error"+"!"*10
		exit()
	else:
		if "Hii" in dsc[int(num)][0]:
			pass
			print "HII"
		elif "Vpd" in dsc[int(num)][0]:
			pass
			print "VPD"
		else:
			for i in range(len(value)):
				if len(value[i]) ==3:
					value_txt.append('  gEfiStructuredPcdPkgTokenSpaceGuid.JUSTFORTEST%d|%s\n'%(i,value[i][2]))
				else:
					if switch == 1:
						if len(value[i]) ==2:
							value_txt.append('  gEfiStructuredPcdPkgTokenSpaceGuid.JUSTFORTEST%d|%s\n'%(i,value[i][1]))
	txt=''.join(value_txt)
	new = txt+dsc[int(num)][1][1]
	data=new,dsc[int(num)][1][1]
	write_DEC_DSC(data,value,Dscfile,Decfile,switch)
	
def write_DEC_DSC(data,value,Dscfile,Decfile,switch):
	try:
		with open(Dscfile,'r') as dsc:
			dsc_read=dsc.read()
		with open(Dscfile,'w+') as new_dsc:
			if data[1] in dsc_read:
				dsc_read=dsc_read.replace(data[1],data[0])
			new_dsc.write(dsc_read)
		with open(Decfile,'a+') as dec:
			dec.write('\n')
			for i in range(len(value)):
				if len(value[i]) == 3:
					dec.write('gEfiStructuredPcdPkgTokenSpaceGuid.JUSTFORTEST%d|%s|%s|0x%08x\n'%(i,value[i][1],value[i][0],(int('0x00010076',16)+i)))
				else:
					if switch == 1:
						if len(value[i]) == 2:
							dec.write('gEfiStructuredPcdPkgTokenSpaceGuid.JUSTFORTEST%d|%s|%s|0x%08x\n'%(i,value[i][1],value[i][0],(int('0x00010076',16)+i)))  
		print "PASS: Modify File Successful"
	except Exception,e:
		print "ERROR: Modify File Error"+str(e)

def main():
	usage="Script.py [-v <value file>]"
	parser = OptionParser(usage)
	parser.add_option('-v','--value',metavar='FILENAME',dest='filename',help="Input the value files")
	parser.add_option('-s','--switch',metavar='NUMBER',default=0,dest='switch',help='0 for not write,1 for write')
	(options,args)=parser.parse_args()
	if options.filename:
		print '\n1: DEC test\n'
		print '2: DSC test\n'
		print '3: Quit\n'
		x=raw_input('Input the number to run test:')
		os.chdir("edk2-staging")
		subprocess.check_call('git checkout TestPkg',shell=True)
		os.chdir(root)
		if int(x) == 3:
			exit()
		elif int(x) == 1:
			DEC_INF_test(options.filename,dec,inf)
		elif int(x) == 2:
			DSC_DEC_test(options.filename,dsc,dec,switch=int(options.switch))
		else:
			print "!"*10+"ERROR: Input Error\n"+"!"*10
		main()
	else:
		print 'Error command, use -h for help'

if __name__=='__main__':
	dec=os.path.join(root,'edk2-staging','TestPkg','TestPkg.dec')
	inf=os.path.join(root,'edk2-staging','TestPkg','Application','TestApp','TestApp.inf')
	dsc=os.path.join(root,'edk2-staging','TestPkg','TestPkg.dsc')
	main()
