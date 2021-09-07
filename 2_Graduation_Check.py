'''
to run in python : exec(open('2_Graduation_Check.py').read())

cd D:\OneDrive\Teaching\admin\advisors\graduation_check_pycharm

program flow
load transcript
load cirriculum data
mainloop
fill_required()
fill_electives()
Check_requisite()
    manual modification loop
        show data
        wait for input (change group)
            1) change group
            2) restart
            3) quit and write to file

future:
    reload save file?
    text base navigation?

Edition notes
MAY 9, 2021
    - Add printing of original transcript to the report file
    
'''

# note what to do with ENG PRACTICE = S/U ? and 21st Cen Gen-ED = S/U

import csv
from os import path
import re

T_path = './transcripts/'  # path to transcript

while 1:
    value = input('Please enter student id to load transcript from <id>.csv'
                  '(CTRL-C to quit)\n>')
    if value == '':  # put default here, for fast debugging
        # Student_ID = '6030055121' #Kisitas
        Student_ID = '5930323921'  # Panus for debugging only
        break
    if value.isnumeric() and len(value) == 10:
        Student_ID = value[0:10]
        if path.exists(T_path + Student_ID + '.csv'):
            print('Found ' + Student_ID + '.csv')
            break
        else:
            print('cannot find ' + Student_ID + '.csv, please try again')
    else:
        print('please enter 10 digit number for the ID')

# Student_ID = '5930323921'
Student_Start_Year = int(Student_ID[0:2])

while 1:
    value = input('Please type program to check <ME59> <ME61> <AE59> <AE61> (CTRL-C to quit)\n>')
    if value == '':  # put default here
        Program = 'AE59'
        break
    elif value.lower() == 'me59':
        Program = 'ME59'
        break
    elif value.lower() == 'me61':
        Program = 'ME61'
        break
    elif value.lower() == 'ae59':
        Program = 'AE59'
        break
    elif value.lower() == 'ae61':
        Program = 'AE61'
        break
    else:
        print('Invalid Program')

# program info
if Program == 'ME59':
    Required_Files = ['59_ME_Basic_Required.csv', '59_ME_Specific_Required.csv']
    Elective_Files = ['GenEd_Hum.csv', 'GenEd_Multi.csv', 'GenEd_SciMath.csv', 'GenEd_Social.csv',
                      '59_ME_Approve_Electives.csv']
    Free_Credits = 6
elif Program == 'AE59':
    Required_Files = ['59_AE_Basic_Required.csv', '59_AE_Specific_Required.csv']
    Elective_Files = ['GenEd_Hum.csv', 'GenEd_Multi.csv', 'GenEd_SciMath.csv', 'GenEd_Social.csv',
                      '59_AE_Approve_Electives.csv']
    Free_Credits = 6
elif Program == 'ME61':
    Required_Files = ['61_ME_Basic_Required.csv', '61_ME_Specific_Required.csv']
    Elective_Files = ['GenEd_Hum.csv', 'GenEd_Multi.csv', 'GenEd_SciMath.csv', 'GenEd_Social.csv',
                      '61_ME_Approve_Electives.csv']
    Free_Credits = 6
elif Program == 'AE61':
    Required_Files = ['61_AE_Basic_Required.csv', '61_AE_Specific_Required.csv']
    Elective_Files = ['GenEd_Hum.csv', 'GenEd_Multi.csv', 'GenEd_SciMath.csv', 'GenEd_Social.csv',
                      '61_AE_Approve_Electives.csv']
    Free_Credits = 6

Tran_Master = []  # for keeping grades, and checking pre-req and co-req
Tran_tmp = []  # temporary file
Tran = []  # Tran with F, W, and regrade removed, keeping the first occurrence only
Tran_tmp2 = []
Tran_AFSU = []  # Tran with W removed, keeping the first occurrence
# all Tran are list of dictionary, each dict is one course, see key/value in load_transcript()
Free_and_Unassigned = [1]  # Free and Unassigned lists
Verbose = False
Course_All = []  # for detecting duplications in required/electives
# course are put in this if not already in it
Course_All_Source = []  # for keeping the group the course came from

print_to_file = 'No'
fout = []


def myprint(string):  # print to screen or to file
    if print_to_file == 'Yes':
        fout.write(string + '\n')
    else:
        print(string)


def vprint(string):  # for showing pre-req and co-req check
    if Verbose == True:
        myprint(string)
    else:
        pass


def padzero(x):  # excel might drop leading zero in class ID
    if len(x) == 6:  # add zero if leading zero is dropped
        return ('0' + x)
    else:
        return x


def left(s, l):  # s = string, l = total length, left justify the string with
    # space added so that the total length is l
    x = "{: <" + str(l) + "}"
    return x.format(s)


def right(s, l):  # right justify with added space to length l
    x = "{: >" + str(l) + "}"
    return x.format(s)


def load_transcript():
    Pass = ['A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'S']
    Taken = ['A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'S', 'F', 'U']
    print('\n\tLoading transcript for ' + Student_ID)
    with open(T_path + Student_ID + '.csv', 'r', encoding='utf8') as transcript_file:
        csv_reader = csv.reader(transcript_file, delimiter=',')
        for row in csv_reader:
            # print(row)
            Year = int(row[4])
            Semestor = int(row[5])
            Sem_no = ((Year - 2500 - Student_Start_Year) * 3 + Semestor)
            # semeter number, 1 = 1st year 1st sem, 2 = 1st year 2nd sem, 3 = 1st year summer
            # 4 = 2nd year 1st sem, etc
            Course = {'ID': padzero(row[1]), 'Name': row[2], 'Credit': int(row[3][0]), 'Sem': Sem_no, 'Grade': row[6],
                      'Counted': 'Free'}
            Tran_Master.append(Course)  # keep all information
            if Course['Grade'] in Pass:  # Pass grade only A-D, S
                Tran_tmp.append(Course)
            if Course['Grade'] in Taken:  # Pass grade + F and U
                Tran_tmp2.append(Course)
    # now that we have all the data, we can remove the re-grade one (duplicate)
    # could be a problem if the student take course twice one for grade and one for S/U
    # one of them will be removed!
    print('\t\tRemoving W, F, and duplicated (regraded) courses')  # W and F is removed already for Tran_tmp
    print('\t\tIf regraded only the first one is kept for checking')
    for row in Tran_tmp:  # building Tran, Tran start out empty
        found = 0  # 0 = duplication not found
        for item in Tran:
            if row['ID'] == item['ID']:
                found = 1
                break
        if found == 0:
            Tran.append(row)

    for row in Tran_tmp2:  # for building Tran_AFSU, needed to check co-requisite
        found = 0
        for item in Tran_AFSU:
            if row['ID'] == item['ID']:
                found = 1
                break
        if found == 0:
            Tran_AFSU.append(row)


def print_fulltranscript(mode):
    # mode 0 = unmodified (should already be sorted by semester number), 1 = sort id, 2 = sort by name
    Tran_Sorted = Tran_Master
    if mode == 0:
        Tran_Sorted.sort(key=lambda x: x['Sem'])
    elif mode == 1:
        Tran_Sorted.sort(key=lambda x: x['ID'])  # or x.get('ID')
    elif mode == 2:
        Tran_Sorted.sort(key=lambda x: x['Name'])
    myprint('Printing original transcript\n')
    for C in Tran_Sorted:
        x = C['Grade']
        if x in ['A', 'B+', 'B', 'C+', 'C', 'D+', 'D']:
            grade = left(x, 4)  # left justify for normal passing grades
        else:
            grade = right(x, 4)  # just to make others like F easier to see
        myprint('\t' + C['ID'] + ' ' + "{:<22}".format(C['Name']) + '' + str(C['Credit']) +
              '\t' + grade + '\t' + "sem = {:>2}".format(str(C['Sem'])))


def print_transcript():  # for debugging
    print('Printing stripped trascript\n')
    for C in Tran:
        x = C['Grade']
        if x in ['A', 'B+', 'B', 'C+', 'C', 'D+', 'D']:
            grade = left(x, 4)
        else:
            grade = right(x, 4)
        print('\t' + C['ID'] + ' ' + "{:<22}".format(C['Name']) + '' + str(C['Credit']) +
              '\t' + grade + '\t' + "sem = {:>2}".format(str(C['Sem'])))

def print_TRAN():
    print('TRAN\n')
    for C in Tran:
        x = C['Grade']
        if x in ['A', 'B+', 'B', 'C+', 'C', 'D+', 'D']:
            grade = left(x, 4)
        else:
            grade = right(x, 4)
        print('\t' + C['ID'] + ' ' + "{:<22}".format(C['Name']) + '' + str(C['Credit']) +
              '\t' + grade + '\t' + "sem = {:>2}".format(str(C['Sem'])) + "\tcounted =" + C['Counted'])

def check_dup(ID, Source):  # check for duplication in the Required and Electives Group
    # if duplication found, exit the program
    # currently the program remove all duplication in the required course and electives
    for i in range(len(Course_All)):
        if Course_All[i] == ID:
            print('Duplicated entry for ID = ' + ID + ' in ' + Source + ' and ' + Course_All_Source[i])
            input('Please recheck it.  Press Enter to exit or Ctrl-C to keep python running\n')
            exit()
    Course_All.append(ID)
    Course_All_Source.append(Source)


Group_Required = []  # list of list of dictionary = [ group 0, group 1, ... ]
# group = [ {dict} , ... , {dict} ]
# each dict is course information see key/value load_required()
# first dict is the group info including the total credit needed for that group
Group_Electives = []  # same structure, see key/value in load_electives()


# [Group][Class ID, Class Name, Credit, PRE, CO, S/U, Semester_no]
# In the file to load, the first line first item is omitted
# second item = group name
# third = total credit of this group
# for the rest see the first line (header) in the file
def load_required():  # load information of required courses
    print('\tLoading required groups')
    for Group in Required_Files:
        with open(Group, 'r', encoding='utf8') as file:
            print('\t\tLoading ' + Group)
            csv_reader = csv.reader(file, delimiter=',')
            data = []
            row = next(csv_reader)  # read the first line (line zero)
            data.append({'Group Name': row[1], 'Total': row[2],
                         'Obtained': 0}, )  # skip the first item to avoid encoding prefix
            for row in csv_reader:  # read from the section line (line 1)
                Sem_No = ((int(row[6]) - 1) * 3 + int(row[7]))  # Semester in the study plan
                data.append({'ID': padzero(row[0]), 'Name': row[1], 'Credit': int(row[2]),
                             'Pre': row[3], 'Co': row[4], 'SU': row[5], 'Sem': Sem_No, 'Pass': 'No', 'Credited': 'No'})
                check_dup(padzero(row[0]), Group)
            Group_Required.append(data)


def print_required():  # print up to this semester for prof. job evaluation report
    C = Tran_Master[-1]  # find last semester from transcript, this should be the current sem
    sem = C['Sem']
    Early_Courses = []  # for keeping courses passed earlier then the study plan
    print('\nLast registered semester = ' + str(sem))
    print('\n\tPrinting missing required courses upto (including) semester ' + str(sem) + ' in the study plan\n')
    for GR in Group_Required:
        for line in GR[1:]:
            if line['Pass'] == 'Yes':
                if line['Sem'] > int(sem):
                    Early_Courses.append([line['ID'], line['Name']])
            elif line['Sem'] <= int(sem):  # for course still not pass at current semester
                print(line['ID'] + ' ' + line['Name'])
    print('\n\tPrinting required courses passed earlier than the study plan\n')
    for C in Early_Courses:
        print(C[0] + ' ' + C[1])
    print('\n')

    ''' print all for debugging only
    print('\tPrinting Required')
    for GR in Group_Required:
        for line in GR:
            print(line)
    '''


def load_electives():  # load information of elective groups and courses in the groups
    print('\tLoading electives groups')
    for Group in Elective_Files:
        with open(Group, 'r', encoding='utf8') as file:
            print('\t\tLoading ' + Group)
            csv_reader = csv.reader(file, delimiter=',')
            data = []
            row = next(csv_reader)  # read the first line
            # add only if it is not also in Group_Required
            data.append(
                {'Group Name': row[1], 'Total': row[2], 'Obtained': 0})  # skip the first item to avoid encoding prefix
            for row in csv_reader:
                used = 0  # to detect duplicated course (may be redundant now with function check_dup)
                for GR in Group_Required:
                    m = [x for x in GR[1:] if x['ID'] == padzero(row[0])]
                    if m != []:  # no matched
                        used = 1
                        print('Elective cannot be same as Required...Omitting...' + padzero(row[0]))
                        input('Press Enter to continue')
                        break
                if used == 0:
                    data.append({'ID': padzero(row[0]), 'Name': row[1], 'Credit': int(row[2]),
                                 'Pre': row[3], 'Co': row[4], 'SU': row[5], 'Pass': 'No', 'Credited': 'No'})
                    check_dup(padzero(row[0]), Group)
            Group_Electives.append(data)


def print_electives():
    print('\tPrinting Electives')
    register_only = 'Yes'
    for GR in Group_Electives:
        print(GR[0])
        for line in GR[1:]:
            if register_only != 'Yes':
                print(line)
            else:
                if line['Pass'] == 'Yes':
                    print(line)


def passgrade(x):  # Grade received with A-D
    if x == 'A' or x == 'B+' or x == 'B' or x == 'C+' or x == 'C' or x == 'D+' or x == 'D':
        return 'Yes'
    else:
        return 'No'


def gradded(x):  # get A-F or S or U
    if x == 'A' or x == 'B+' or x == 'B' or x == 'C+' or x == 'C' or x == 'D+' or x == 'D' \
            or x == 'F' or x == 'S' or x == 'U':
        return 'Yes'
    else:
        return 'No'


def fill_required():  # fill the required course info
    print('\tFilling required course')
    GR = Group_Required  # just so it is shorter, same list
    for i in range(len(GR)):  # for each group
        tot_credit = 0
        for j in range(1, len(GR[i])):  # skip first line but keep the index, which is for summary not courses
            k = [k for k in range(len(Tran)) if Tran[k]['ID'] == GR[i][j]['ID']]  # get index for matched line in Tran
            for ind in k:  # k is a list, k may be empty,
                # Tran <- all Matched ID must be set marked in key 'Counted'
                # Tran[]['Counted'] can be Yes (required or elective), Free (free elec), or No (unassigned)
                # Group_Required <- mark as pass or not, and counted in this group or not
                if GR[i][j]['SU'].lower() == 'YES'.lower():  # S/U
                    if Tran[ind]['Grade'] == 'S':
                        GR[i][j]['Pass'] = 'Yes'
                        if Tran[ind]['Counted'] == 'Free':  # can be counded only once
                            GR[i][j]['Credited'] = 'Yes'
                            Tran[ind]['Counted'] = 'Yes'  # marked as counted
                            tot_credit += GR[i][j]['Credit']
                elif passgrade(Tran[ind]['Grade']) == 'Yes':  # Letter Grade
                    GR[i][j]['Pass'] = 'Yes'
                    if Tran[ind]['Counted'] == 'Free':  # can be counded only once
                        GR[i][j]['Credited'] = 'Yes'
                        Tran[ind]['Counted'] = 'Yes'
                        tot_credit += GR[i][j]['Credit']
            # Course and GR is not the real list, we need to replace Groupe_Required with the new data
            # print(GR[i][j]) # for debugging only
        GR[i][0]['Obtained'] = tot_credit  # put in total credit


def fill_electives():
    print('\tFilling electives')
    GE = Group_Electives  # just so it is shorter, same list
    for i in range(len(GE)):
        tot_credit = 0
        for j in range(1, len(GE[i])):  # skip first line but keep the index, which is for summary not courses
            k = [k for k in range(len(Tran)) if Tran[k]['ID'] == GE[i][j]['ID']]  # get index for matched line in Tran
            for ind in k:  # k is a list, k may be empty
                # Tran <- all Matched ID must be marked in 'Counted'
                # Group_Required <- mark as pass or not, and counted in this group or not
                if GE[i][j]['SU'].lower() == 'YES'.lower():  # S/U
                    if Tran[ind]['Grade'] == 'S' or passgrade(Tran[ind]['Grade']) == 'Yes':
                        # some Gen-Ed class with S/U can be taken for grade
                        GE[i][j]['Pass'] = 'Yes'
                        if Tran[ind]['Counted'] == 'Free':  # can be counded only once
                            GE[i][j]['Credited'] = 'Yes'
                            Tran[ind]['Counted'] = 'Yes'
                            tot_credit += GE[i][j]['Credit']
                            GE[i][j]['Sem-Reg'] = Tran[ind]['Sem']
                elif passgrade(Tran[ind]['Grade']) == 'Yes':  # Letter Grade
                    GE[i][j]['Pass'] = 'Yes'
                    if Tran[ind]['Counted'] == 'Free':  # can be counded only once
                        GE[i][j]['Credited'] = 'Yes'
                        Tran[ind]['Counted'] = 'Yes'
                        tot_credit += GE[i][j]['Credit']
                        GE[i][j]['Sem-Reg'] = Tran[ind]['Sem']
            # Course and GR is not the real list, we need to replace Groupe_Required with the new data
            # print(GR[i][j]) # for debugging only
        GE[i][0]['Obtained'] = tot_credit  # put in total credit
    # need to add short key so editing is easier


''' 
#not used anymore, just collect in showdata()
Free_List=[] #unassigned course used for free electives
def make_freelist(): # collect un-assigned courses
    print('\tCollecting remaining courses as free electives')
    Free_List.append({'Group Name':'Free Electives', 'Total':Free_Credits, 'Obtained':0}) #make first row
    total_credit = 0
    for i in range(len(Tran)):
        if Tran[i]['Counted']=='No':
            tmp=Tran[i]
            tmp['Counted']='Yes'
            Free_List.append(tmp)
            Tran[i]['Counted']=='Yes'
            total_credit += Tran[i]['Credit']
    Free_List[0]['Obtained']=total_credit

def print_free():
    print('Printing Free Electives')
    print(Free_List[0])
    for row in Free_List[1:]:
        print(row)
'''


def checkpre(cmd_str, ID):  # should be ok if the course is registed with grade
    # not fully test for S/U
    # find registed semester
    C_in_T = [x for x in Tran if x['ID'] == ID]
    if C_in_T == []:
        result = 'NO '
    else:
        C_in_T = C_in_T[0]
        sem = C_in_T['Sem']
        cmd_str = cmd_str.lower()
        vprint('\nFor %s, Pass-Sem = %s \n\tPre-Req = %s' % (C_in_T['ID'], sem, cmd_str))
        result = '- '
        new_str = ''
        # cmd_str = command string, sem = class semester with this pre-requirement
        p = re.compile('[\d]{7}')  # set up re search with this 7 digit number
        i = 0  # string index
        m = [x for x in p.finditer(cmd_str)]
        if m != []:
            for m in p.finditer(cmd_str):  # find one by one
                # print(m)
                # m[].start(), m[].end(), m[].group()
                new_str += cmd_str[i:m.start()]
                i = m.end()
                pre = m.group()  # id of pre-requisite
                C = [x for x in Tran if x['ID'] == pre]
                if C == []:  # did not registered or no pass grade
                    new_str += 'False'
                else:
                    C = C[0]  # there should be only one or empty
                    # print(C)
                    if passgrade(C['Grade']) == 'Yes' and C['Sem'] < sem:
                        # print('True')
                        new_str += 'True'
                    else:
                        new_str += 'False'
            new_str += cmd_str[i:]
            vprint("\t" + new_str)
            x = eval(new_str)
            if x == True:
                result = 'ok '
            else:
                result = 'NO '
        else:
            result = '- '
    return result


def checkco(cmd_str, ID):
    # find registed semester
    C_in_T = [x for x in Tran if x['ID'] == ID]
    if C_in_T == []:
        result = 'NO '
    else:
        C_in_T = C_in_T[0]
        sem = C_in_T['Sem']
        cmd_str = cmd_str.lower()
        vprint('\tCo -Req = %s' % (cmd_str))
        result = '- '
        new_str = ''
        # cmd_str = command string, sem = class semester with this pre-requirement
        p = re.compile('[\d]{7}')  # set up re search with this 7 digit number
        i = 0  # string index
        m = [x for x in p.finditer(cmd_str)]
        if m != []:
            for m in p.finditer(cmd_str):  # find one by one
                # print(m)
                # m[].start(), m[].end(), m[].group()
                new_str += cmd_str[i:m.start()]
                i = m.end()
                pre = m.group()  # id of pre-requisite
                C = [x for x in Tran_AFSU if x['ID'] == pre]
                if C == []:  # did not register or not getting A-F
                    new_str += 'False'
                else:
                    C = C[0]  # there should be only one
                    # print(C)
                    if C != [] and gradded(C['Grade']) == 'Yes' and C['Sem'] <= sem:
                        # print('True')
                        new_str += 'True'
                    else:
                        new_str += 'False'
            new_str += cmd_str[i:]
            vprint("\t" + new_str)
            x = eval(new_str)
            if x == True:
                result = 'ok '
            else:
                result = 'NO '
        else:
            result = '- '
    return result


E_Avail_Tog = []  # for keeping track of possible toggle command,
# ex [{'No':0, 'Group':0, 'Row':0, 'ID':2103212},{}]
F_Avail_Tog = []


def show_data():  # and write to file too
    # show student info
    myprint('=' * 60)
    myprint('\t Report for ' + Student_ID + '\t\tProgram = ' + Program)
    myprint('=' * 60)

    # show required
    myprint('   Required Group\n')
    GR = Group_Required  # assigne a nickname
    for i in range(len(GR)):
        myprint('\tGroup = ' + left(GR[i][0]['Group Name'], 25) + '\tCredit Needed = ' + str(GR[i][0]['Total']) +
                '\tCredit Obtained = ' + str(GR[i][0]['Obtained']) + '\n')
        for j in range(1, len(GR[i])):
            C = GR[i][j]
            # required group should not be changed at all
            Mark = '   '
            if C['Pass'] == 'Yes':
                # Check if Pass with S
                # show S if grade is S in Tran
                x = [x for x in Tran if x['ID'] == C['ID']]  # should not be empty
                x = x[0]
                # print(x)
                if x['Grade'] == 'S':
                    passed = 'S'
                else:
                    passed = 'Pass'
                # check pre
                cmd_str = C['Pre']
                pre = checkpre(cmd_str, C['ID'])
                # check co
                cmd_str = C['Co']
                co = checkco(cmd_str, C['ID'])
            else:
                passed = 'No  '
                pre = '- '
                co = '- '

            myprint('\t' + C['ID'] + ' ' + "{:<22}".format(C['Name']) + '' + str(C['Credit']) +
                    '\t' + passed + '\t' + Mark + '\t' + "cur-sem = {:>2}".format(str(C['Sem'])) +
                    '\tpre=' + pre + '\tco=' + co)
        myprint('')

    # show electives
    count = 0  # for toggle command
    myprint('   Elective Group\n')
    ER = Group_Electives  # assigne a nickname
    for i in range(len(ER)):
        myprint('\tGroup = ' + left(ER[i][0]['Group Name'], 20) + '\t\tCredit Needed = ' + str(ER[i][0]['Total']) +
                '\tCredit Obtained = ' + str(ER[i][0]['Obtained']) + '\n')
        for j in range(1, len(ER[i])):
            C = ER[i][j]
            Mark = '[ ]'
            if C['Credited'] == 'Yes':
                Mark = '[x]'
            passed = 'No  '
            if C['Pass'] == 'Yes':
                x = [x for x in Tran if x['ID'] == C['ID']]  # should not be empty
                x = x[0]
                # print(x)
                if x['Grade'] == 'S':
                    passed = 'S'
                else:
                    passed = 'Pass'
                if not ('Sem-Reg' in C):
                    print(C['ID'] + 'error')
                    print('Missing Key, there might be duplicate entry in electives groups')
                else:
                    myprint(
                        'e' + str(count) + '\t' + C['ID'] + ' ' + "{:<22}".format(C['Name']) + '' + str(C['Credit']) +
                        '\t' + passed + '\t\tPas-sem = ' + left(str(C['Sem-Reg']), 5) + Mark)
                    E_Avail_Tog.append({'No': count, 'Group': i, 'Row': j, 'ID': C['ID']})
                    count += 1
        myprint('')

    # show free
    # count credit
    # clear Toggle
    F_Avail_Tog.clear()
    Free = [x for x in Tran if x['Counted'] == 'Free']
    total_credit = 0
    for C in Free:  # count free credit
        if passgrade(C['Grade']) == 'Yes':
            total_credit += C['Credit']
    myprint('  Free Electives (only A-D is credited) \tCredit Needed = ' + str(Free_Credits) + '\tCredit Obtained = ' +
            str(total_credit) + '\n')
    global Free_and_Unassigned
    Free_and_Unassigned = [x for x in Tran if x['Counted'] != 'Yes']
    FU = Free_and_Unassigned  # set a nick name
    for i in range(len(FU)):  # print both free [x] and unassigned [] here
        mark = '[x]'
        if FU[i]['Counted'] == 'No':
            mark = '[ ]'
        passed = 'No  '
        if passgrade(FU[i]['Grade']) == 'Yes':
            passed = 'Pass'
        elif FU[i]['Grade'] == 'S':
            passed = 'S   '
        myprint('f' + str(i) + '\t' + FU[i]['ID'] + ' ' + "{:<22}".format(FU[i]['Name']) + '' + str(FU[i]['Credit']) +
                '\t' + passed + ' \t\tPas-sem = ' + left(str(FU[i]['Sem']), 5) + mark)
        F_Avail_Tog.append({'No': i, 'ID': FU[i]['ID']})
    myprint('')

    # show extra
    myprint('   Unassigned\n')
    Unassigned = [x for x in Tran if x['Counted'] == 'No']
    for C in Unassigned:
        if passgrade(C['Grade']) == 'Yes':
            passed = 'Pass'
        elif C['Grade'] == 'S':
            passed = 'S   '
        myprint(' ' + '\t' + C['ID'] + ' ' + "{:<22}".format(C['Name']) + '' + str(C['Credit']) +
                '\t' + passed)
    myprint('')


def ind_in_Tran(ID):  # find index of class with ID in Tran
    for ind in range(len(Tran)):
        if Tran[ind]['ID'] == ID:
            return ind
    return []  # should not be executed


# loading data
load_transcript()
# print_transcript()
# print_fulltranscript() #for debugging
load_required()
# print_required() #for debugging
load_electives()
# print_electives() #for debugging

# checking
fill_required()
fill_electives()
# make_freelist() # no longer needed
show_data()
# print_transcript()
# print_fulltranscript()
# print_required()
# print_electives()
# print_free()

# main loop
while True:
    value = input("Command (q = quit, t = origial transcript, ti = transcript by ID, " +
                  "tn = transcript by NAME " + "\n\ttx = marked stripped transcript"
                  "\n\ts = show report, " + "p = print report, " +
                  "v = toggle show pre/co (now =" + str(Verbose) + ")" +
                  "\n\tx = print missing required course upto last registed semester and earlier ones" +
                  "\n\tto toggle selection type e<line no.> or f<line no.> example e0, f1, etc):")
    if value == 'q':
        break
    elif value == '':
        print('invalid selection')
    elif value == 'v':
        Verbose = not Verbose
        show_data()
    elif value == 'x':
        print_required()
    elif value == 't':
        print_fulltranscript(0)
    elif value == 'ti':
        print_fulltranscript(1)
    elif value == 'tn':
        print_fulltranscript(2)
    elif value == 'tx':
        print_TRAN()
    elif value == 's':
        show_data()
    elif value == 'p':
        # global fout
        fout = open(T_path + 'Report_' + Student_ID + '.txt', 'w', encoding='utf8')
        print_to_file = 'Yes'
        show_data()
        print_fulltranscript(0)
        print_to_file = 'No'
        fout.close()
    elif value[0] == 'e':  # toggle elective group
        # Elective [x] deselect -> put in Free group
        # Elective [ ] select -> put in Elective
        # Free [x] deselect -> put in unassigned group
        # Free [ ] select -> put in Free
        # Change in Tran ['Counted']
        # Change total credit count in Group_Required, and Group_Elective
        number = value[1:]
        if number.isnumeric():
            line_selected = int(number)
            x = [x for x in E_Avail_Tog if x['No'] == line_selected]
            if x == []:  # invalid selection
                print('invalid selection')
            else:
                x = x[0]  # convert list of one dictionary to dictionary
                Group_in_GE = x['Group']
                Row_in_GE = x['Row']
                ID = Group_Electives[Group_in_GE][Row_in_GE]['ID']
                # class in Group_Elective = Group_Electives[x['Group']][x['Row']]
                # print(Group_Electives[Group_in_GE][Row_in_GE])
                # find class in Tran
                Row_in_Tran = ind_in_Tran(ID)
                # print(Tran[Row_in_Tran])
                if Group_Electives[Group_in_GE][Row_in_GE]['Credited'] == 'Yes':  # counted [x]
                    # change to no count [ ] and move to Free by change 'Counted' in Tran to 'Free'
                    Group_Electives[Group_in_GE][Row_in_GE]['Credited'] = 'No'
                    Tran[Row_in_Tran]['Counted'] = 'Free'
                    Group_Electives[Group_in_GE][0]['Obtained'] -= int(
                        Group_Electives[Group_in_GE][Row_in_GE]['Credit'])
                else:  # not currently counted, this class could be in Free or Unassigned('No')
                    Group_Electives[Group_in_GE][Row_in_GE]['Credited'] = 'Yes'
                    Tran[Row_in_Tran]['Counted'] = 'Yes'
                    Group_Electives[Group_in_GE][0]['Obtained'] += int(
                        Group_Electives[Group_in_GE][Row_in_GE]['Credit'])
                show_data()
        else:
            print('invalid selection')
    elif value[0] == 'f':  # toggle free group
        number = value[1:]
        if number.isnumeric():
            line_selected = int(number)
            # x = [x for x in F_Avail_Tog if x['No']==line_selected] #I think F_Avail_Tog is not needed
            if line_selected >= len(Free_and_Unassigned):  # invalid selection
                print('invalid selection')
            else:
                ID = Free_and_Unassigned[line_selected]['ID']
                # find class in Tran
                Row_in_Tran = ind_in_Tran(ID)
                print(Tran[Row_in_Tran])
                if Tran[Row_in_Tran]['Counted'] == 'Free':
                    Tran[Row_in_Tran]['Counted'] = 'No'
                    print(Tran[Row_in_Tran])
                else:  # if it is 'No'
                    Tran[Row_in_Tran]['Counted'] = 'Free'
                    print(Tran[Row_in_Tran])
                show_data()
    else:
        pass
# print('Commnad = %s' % value)

# print transcript sort by sem, id, name
