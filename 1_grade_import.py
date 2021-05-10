#to run in python >> exec(open('1_grade_import.py',encoding='UTF-8').read())
#to run in dos >> python 1_grade_import.py
#This prog convert grade.txt to <<<studentid.txt>>> with one class per line
#need grade.txt to run
#grade.txt is the text copy from the unofficial transcript in reg.chula.ac.th


#ไม่รู้ทำไมใช้ Sublime Text ไม่ได้ ไทยใช้ได้ แต่ run ไม่ได้?? -> might be solved by using utf-8 for all files
#run in pycharm = ok


import re
import os

T_path = './transcripts/' #path to transcript

'''
#combinetheline so it is easy to verify, might not need it
with open(T_path + 'test_outfile.txt','w', encoding='utf8') as out:
  with open('grade.txt', 'r', encoding='utf8') as f:
    for line in f:
      #print(repr(line),end='')
      out.write(repr(line))
      #out.write(line)
    out.write('this file is not used')
#auto file closing using 'with'
'''

#extracting start using 'outfile.txt'
#should have use the 'with-as' statement

f= open(T_path + 'grade.txt', encoding='utf8')
all=f.read()
f.close()
#p=re.compile('2103[^0][0-9]*') # to get all the course id
#m=p.findall(all)
#print(m)
#find major
p=re.compile('MAJOR CODE')
m=p.search(all)
major = all[m.end()+1:m.end()+6]
#fout.write('major ='+ major + '\n')
#find name
p=re.compile('ชื่อ-นามสกุล.*\\n')
m1=p.search(all)
p=re.compile('ภาค')
m2=p.search(all)
name = all[m1.start()+13:m1.end()-1]
#name = all[m1.end()+1:m2.start()-4]
#fout.write('name ='+ name + '\n')
#find student id
p=re.compile('เลขประจำตัวนิสิต')
m=p.search(all)
id = all[m.end()+2:m.end()+5]+all[m.end()+6:m.end()+11]+all[m.end()+12:m.end()+14]
#fout.write('id ='+ id + '\n')

p=re.compile('ภาคการศึกษา')
m=p.search(all)
all=all[m.start():] #cut the beginning off
sem_start, year, sem = [],[],[]
#now get the location of semseters
#p=re.compile('ภาคการศึกษา.*    ปีการศึกษา \d\d\d\d')
p=re.compile('ภาค.*    ปีการศึกษา \d\d\d\d')
for m in p.finditer(all):
  string=m.group()
  print(string)
  s=string[11]
  if s=='ต':
    sem_now=1
  elif s=='ป':
    sem_now=2
  else:
    sem_now=3
  sem_start_now=m.start()
  year_now=string[-4:]
  print('found=>', sem_start_now,year_now, sem_now)
  sem_start.append(sem_start_now)
  year.append(year_now)
  sem.append(sem_now)
  
#loop to find all courses
start,cid,cname,credit,grade=[],[],[],[],[]
p = re.compile('\d\d\d\d\d\d\d.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n')
p_cname=re.compile('\\n\\n.*\\n\\n')
p_credit=re.compile('\\n\\n.*[.].*\\n\\n')
p_grade=re.compile('\\n\\n\s*[ABCDFWMISUVX]\+*\s*\\n\\n')
for m in p.finditer(all):  #don't really understand
  string=m.group()
  print(m.start(), repr(string))
  start.append(m.start())
  cid_now=string[0:7]
  cid.append(cid_now)
  tmp=p_cname.search(string)
  tmp=tmp.group()
  cname_now=tmp[3:-2]
  cname.append(cname_now)
  tmp=p_credit.search(string)
  tmp=tmp.group()
  credit_now=tmp.strip()
  credit.append(credit_now)
  tmp=p_grade.search(string)
  tmp=tmp.group()
  grade_now=tmp.strip()
  grade.append(grade_now)
  print('found=>',m.start(),cid_now,cname_now,credit_now,grade_now)

#writing out the csv file
fout= open(T_path + id + '.csv','w', encoding='utf8')
sem_end=sem_start[1:]
sem_end.append(99999)
for i in range(len(sem_start)):
  #print(i, sem_start[i], sem_end[i])
  for j in range(len(start)):
    if sem_start[i]<start[j]<sem_end[i]:
      #print(sem_start[i], start[j])
      fout.write(id+','+cid[j]+','+cname[j]+',' +credit[j] +','+year[i]+','+str(sem[i])+','+grade[j]+'\n')
fout.close()
cmd = 'copy '+id+'.csv grade.csv'
os.system(cmd)
print('\nGrade for '+id+' is written to '+id+'.csv and grade.csv')
print('please run 2_Graduation_Check.py next')