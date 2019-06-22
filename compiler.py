# Vasileiou Ioannis - AM 2647 - cse42647
# Petros Savvopoulos - AM 2530 - cse32530
# Project : Starlet Language - Compiler

import sys
import os

# Lists of the symbols and keywords supported by Starlet #
keywords = {
				'program' : 'programtk',
				'endprogram' :  'endprogramtk',
				'declare' : 'declaretk',
				'if' : 'iftk',
				'then' : 'thentk',
				'else' : 'elsetk',
				'endif' : 'endiftk',
				'while' : 'whiletk',
				'endwhile' : 'endwhiletk',
				'dowhile' : 'dowhiletk',
				'enddowhile' : 'enddowhiletk',
				'loop' : 'looptk',
				'endloop' : 'endlooptk',
				'exit' : 'exittk',
				'forcase' : 'forcasetk',
				'endforcase' : 'endforcasetk',
				'incase' : 'incasetk',
				'endincase' : 'endincasetk',
				'when' : 'whentk',
				'default' : 'defaulttk',
				'enddefault' : 'enddefaulttk',
				'function': 'functiontk',
				'endfunction' : 'endfunctiontk',
				'return' : 'returntk',
				'in' : 'intk',
				'inout' : 'inouttk',
				'inandout' : 'inandouttk',
				'and' : 'andtk',
				'or' : 'ortk',
				'not' : 'nottk',
				'input' : 'inputtk',
				'print' : 'printtk'				}

symbols = ['+', '-', '*', '/', '<', '>', '=', '<=', '>=', '<>', ':=' , ';', ',', ':', '(', ')', '[', ']' , '/*', '*/', '//' ]

beginBlockCounter = 0
calledFrameLength = 0
# Endiamesos Kwdikas
temp_counter = -1 	# counter of T_
quads_line = -1		# counter of line 4adas
var_list = []		# list to store the temp variables ( T_ )
quads = {}			# "line : 4ada"

# Pinakas Sumvolwn
mainFrameLength=0
recordScopeList = {} # "scopeNestingLevel : entitites"
recordEntityList = []
recordArgumentsList = []
offsetTable = [] # Store all offsets for each nestingLevel	(Scopes)
offsetTable.append(12) # first offset of main
nestingLevel = 0

# Usefull Functions For Final Code
def gnlvcode(v):
	x,y = searchvar(v)

	marsfile.write("\tlw $t0 , -4($sp)\n")
	if( (x+1)<nestingLevel ):
		while(x>0):
			marsfile.write("\tlw $t0, -4($t0)\n")
			x-=1
	offset = str(recordScopeList[x][y][-1])
	marsfile.write("\tadd $t0 , $t0 , -" + offset + "\n")

def searchvar(var):
	global recordScopeList,nestingLevel
	# it will find which scope the "var" is in
    # i --> NestingLevel (#scope)
	for i in range(len(recordScopeList)-1,-1,-1):
		# j --> 4 * j
		for j in range(len(recordScopeList[i])):
			# return the first one it will be found
			if (var == recordScopeList[i][j][0]):
				return i,j
	return -1,-1

def loadvr(v, r):
	global nestingLevel,recordScopeList
	x,y = searchvar(v)

	if(y==-1 and x==-1):
		# Const
		if(v.isdigit() or v.lstrip("-").isdigit()):
			marsfile.write("\tli $t"+str(r)+", "+str(v)+"\n")


	# Global (it is in main scope)
	elif(x==0):
		offset = str(recordScopeList[x][y][len(recordScopeList[x][y])-1])
		marsfile.write("\tlw $t"+str(r)+", -"+offset+"($s0)\n")

	# BΦ = Current
	elif(x==nestingLevel):
		# Local var or Parameter via value or Temporary
		if(recordScopeList[x][y][1]=='in'):
			offset = str(recordScopeList[x][y][len(recordScopeList[x][y])-1])
			marsfile.write("\tlw $t"+str(r)+", -"+offset+"($sp)\n")

		# Parameter by Reference
		elif(recordScopeList[x][y][1]=='inout'):
			offset = str(recordScopeList[x][y][len(recordScopeList[x][y])-1])
			marsfile.write("\tlw $t0, -"+offset+"($sp)\n")
			marsfile.write("\tlw $t"+str(r)+", ($t0)\n")

		# Parameter via Copy
		elif(recordScopeList[x][y][1]=='inandout'):
			offset = str(recordScopeList[x][y][len(recordScopeList[x][y])-1])
			marsfile.write("\tlw $t"+str(r)+", -"+offset+"($sp)\n")
			marsfile.write("\tlw $t"+str(r)+", ($t0)\n")

	# ΒΦ < Current
	elif(x<nestingLevel):
		# Local var or Parameter via value or Temporary
		if(recordScopeList[x][y][1]=='in'):
			gnlvcode(recordScopeList[x][y][0])
			marsfile.write("\tlw $t"+str(r)+", ($t0)\n")

		# Parameter by Reference
		elif(recordScopeList[x][y][1]=='inout'):
			gnlvcode(recordScopeList[x][y][0])
			marsfile.write("\tlw $t0, ($t0)\n")
			marsfile.write("\tlw $t"+str(r)+", ($t0)\n")

		# Parameter via Copy
		elif(recordScopeList[x][y][1]=='inandout'):
			gnlvcode(recordScopeList[x][y][0])
			marsfile.write("\tlw $t"+str(r)+", ($t0)\n")
			marsfile.write("\tlw $t0, ($t0)\n")
			marsfile.write("\tlw $t"+str(r)+", ($t0)\n")

def storerv(r, v):
	global nestingLevel,recordScopeList
	x,y = searchvar(v)

	if(x==-1 and y==-1):
		printError("Not recognized: This variable is not declared in line : ",line)

	# Global (it is in main scope)
	elif(x==0):
		offset = str(recordScopeList[x][y][len(recordScopeList[x][y])-1])
		marsfile.write("\tsw $t"+str(r)+", -"+offset+"($s0)\n")

	# BΦ = Current
	elif(x==nestingLevel):
		# Local var or Parameter via value or Temporary
		if(recordScopeList[x][y][1]=='in'):
			offset = str(recordScopeList[x][y][len(recordScopeList[x][y])-1])
			marsfile.write("\tsw $t"+str(r)+", -"+offset+"($sp)\n")

		# Parameter by Reference
		elif(recordScopeList[x][y][1]=='inout'):
			offset = str(recordScopeList[x][y][len(recordScopeList[x][y])-1])
			marsfile.write("\tlw $t0, -"+offset+"($sp)\n")
			marsfile.write("\tsw $t"+str(r)+", ($t0)\n")

		# Parameter via Copy
		elif(recordScopeList[x][y][1]=='inandout'):
			offset = str(recordScopeList[x][y][len(recordScopeList[x][y])-1])
			marsfile.write("\tsw $t"+str(r)+", -"+offset+"($sp)\n")
			# we pass it as CV
			marsfile.write("\tsw $t"+str(r)+", -"+offset+"($sp)\n")
			marsfile.write("\tsw $t"+str(r)+", ($t0)\n")

	# ΒΦ < Current
	elif(x<nestingLevel):
		# Local var or Parameter via value or Temporary
		if(recordScopeList[x][y][1]=='in'):
			gnlvcode(recordScopeList[x][y][0])
			marsfile.write("\tsw $t"+str(r)+", ($t0)\n")

		# Parameter by Reference
		elif(recordScopeList[x][y][1]=='inout'):
			gnlvcode(recordScopeList[x][y][0])
			marsfile.write("\tlw $t0, ($t0)\n")
			marsfile.write("\tsw $t"+str(r)+", ($t0)\n")

		# Parameter via Copy
		elif(recordScopeList[x][y][1]=='inandout'):
			gnlvcode(recordScopeList[x][y][0])
			marsfile.write("\tlw $t0, ($t0)\n")
			marsfile.write("\tsw $t"+str(r)+", ($v1)\n")

def checkParameters(counterOfPar, numberOfQuad):
	global recordScopeList,offsetTable,nestingLevel,calledFrameLength

	if(counterOfPar == 0):
		while(True):
			if (quads[numberOfQuad][0] == 'par'):
				numberOfQuad+=1
			elif(quads[numberOfQuad][0] == 'call'):
				x,y = searchvar(quads[numberOfQuad][1])
				break

		if(not(str(recordScopeList[x][y][-1]).isdigit())):
			marsfile.write("\taddi $fp , $sp , "+ str(offsetTable[nestingLevel]) +"\n")
			calledFrameLength = offsetTable[nestingLevel]
		else:
			marsfile.write("\taddi $fp , $sp , "+ str(recordScopeList[x][y][-1]) +"\n")
			calledFrameLength = recordScopeList[x][y][-1]

def create_FinalCode(counterOfQuads):
	global quads,programName,mainFrameLength,beginBlockCounter,calledFrameLength
	counterOfPar = 0

	# Convert code to assembly each function
	for i in range(beginBlockCounter,counterOfQuads):
		currentQuad = quads[i]
		# begin_block, blockName, _ , _
		if(currentQuad[0] == "begin_block"):
			# if it is the Main (==programName)
			if(currentQuad[1] == programName):
				marsfile.write("Lmain:\n\taddi $sp, $sp, " + str(mainFrameLength) + "\n")
				marsfile.write("\tmove $s0, $sp\n")
			else:
				marsfile.write("L_"+ currentQuad[1] + ":\n")
				marsfile.write("L_"+ str(i) + ":\n")
				marsfile.write("\tsw $ra, ($sp)\n")

		#end_block, x , _ , _
		elif(currentQuad[0] == "end_block"):
			if(currentQuad[1] != programName):
				marsfile.write("L_" + str(i) + ":\n")
				marsfile.write("\tlw, $ra, ($sp)\n")
				marsfile.write("\tjr $ra\n")

		# := , x , _ , z
		elif(currentQuad[0] == ":="):
			marsfile.write("L_" + str(i) + ":\n")
			loadvr(currentQuad[1], 1)
			storerv(1, currentQuad[3])

		# op, x, y, z
		elif(currentQuad[0]=="+" or currentQuad[0]=="-"	or currentQuad[0]=="*" or currentQuad[0]=="/"):
			marsfile.write("L_" + str(i) + ":\n")
			loadvr(currentQuad[1], 1)
			loadvr(currentQuad[2], 2)
			if(currentQuad[0]=="+"):
				marsfile.write("\tadd $t1, $t1, $t2\n")
			elif(currentQuad[0]=="-"):
				marsfile.write("\tsub $t1, $t1, $t2\n")
			elif(currentQuad[0]=="*"):
				marsfile.write("\tmul $t1, $t1, $t2\n")
			elif(currentQuad[0]=="/"):
				marsfile.write("\tdiv $t1, $t1, $t2\n")
			storerv(1, currentQuad[3])

		# inp , x , _ , _
		elif(currentQuad[0]=="inp"):
			marsfile.write("L_" + str(i) + ":\n")
			marsfile.write("\tli $v0, 5\n")
			marsfile.write("\tsyscall\n")

		# out , x , _ , _
		elif(currentQuad[0]=="out"):
			marsfile.write("L_" + str(i) + ":\n")
			marsfile.write("\tli $v0, 1\n")
			marsfile.write("\tli $a0, $t1\n")
			marsfile.write("\tsyscall\n")

		# retv, x, _ , _
		elif(currentQuad[0]=="retv"):
			marsfile.write("L_" + str(i) + ":\n")
			loadvr(currentQuad[1],1)
			marsfile.write("\tlw $t0, -8($sp)\n")
			marsfile.write("\tsw $t1, ($t0)\n")

		# jump , _ , _ , label
		elif(currentQuad[0]=="jump"):
			marsfile.write("L_" + str(i) + ":\n")
			marsfile.write("\tj L_"+str(currentQuad[3])+"\n")

		# relop, x, y, z
		elif(currentQuad[0]=="<" or currentQuad[0]==">" or currentQuad[0]=="<>" or currentQuad[0]=="<=" or currentQuad[0]==">=" or currentQuad[0]=="="):
			marsfile.write("L_" + str(i) + ":\n")
			loadvr(currentQuad[1],1)
			loadvr(currentQuad[2],2)
			if(currentQuad[0]=="="):
				marsfile.write("\tbeq $t1, $t2, L_"+ str(currentQuad[3])+"\n")
			if(currentQuad[0]=="<"):
				marsfile.write("\tblt $t1, $t2, L_"+ str(currentQuad[3])+"\n")
			if(currentQuad[0]==">"):
				marsfile.write("\tbgt $t1, $t2, L_"+ str(currentQuad[3])+"\n")
			if(currentQuad[0]=="<>"):
				marsfile.write("\tbne $t1, $t2, L_"+ str(currentQuad[3])+"\n")
			if(currentQuad[0]=="<="):
				marsfile.write("\tble $t1, $t2, L_"+ str(currentQuad[3])+"\n")
			if(currentQuad[0]==">="):
				marsfile.write("\tbge $t1, $t2, L_"+ str(currentQuad[3])+"\n")

		# call , functionName, _ , _
		elif(currentQuad[0]=="call"):
			marsfile.write("L_"+str(i)+":\n")
			x,y = searchvar(currentQuad[1])
			# call a brother
			if(x == nestingLevel):
				marsfile.write("\tlw $t0 , -4($sp)\n")
				marsfile.write("\tsw $t0 , -4($fp)\n")
			else:
				marsfile.write("\tsw $sp , -4($fp)\n")
			marsfile.write("\tadd $sp, $sp, "+str(calledFrameLength)+"\n")
			marsfile.write("\tjal L_"+ currentQuad[1] +"\n")
			marsfile.write("\tadd $sp, $sp, -"+str(calledFrameLength)+"\n")
			# init the counter of par again
			counterOfPar = 0

		# par , x , CV , _
		elif(currentQuad[0]=="par" and currentQuad[2]=="CV"):
			marsfile.write("L_"+str(i)+":\n")
			checkParameters(counterOfPar, i)
			loadvr(currentQuad[1],0)
			marsfile.write("\tsw $t0, "+str(-(12+(4*counterOfPar)))+"($fp)\n")
			counterOfPar+=1

		# par , x , REF , _
		elif(currentQuad[0]=="par" and currentQuad[2]=="REF"):
			marsfile.write("L_"+str(i)+":\n")
			x,y=searchvar(currentQuad[1])
			checkParameters(counterOfPar,i)
			# X is Local
			if(x == nestingLevel):
				# variable as INOUT
				if(recordScopeList[x][y][1]=='inout'):
					marsfile.write("\tlw $t0 , -"+ str(recordScopeList[x][y][len(recordScopeList[x][y])-1]) + "($sp)\n")
					marsfile.write("\tsw $t0 , "+ str(-(12+(4*counterOfPar))) + "($fp)\n")
				# local variable, or variable that passed as IN
				else:
					marsfile.write("\tadd $t0 , $sp , -"+ str(recordScopeList[x][y][-1])+"\n")
					marsfile.write("\tsw $t0 , "+ str(-(12+(4*counterOfPar))) + "($fp)\n")
			# Not Local
			else:
				# variable via ref
				if(str(recordScopeList[x][y][-1])=='inout'):
					gnlvcode(recordScopeList[x][y][0])
					marsfile.write("\tlw $t0 , ($t0)\n")
					marsfile.write("\tsw $t0 , "+ str(-(12+(4*counterOfPar))) + "($fp)\n")
				# local variable or variable via value
				else:
					gnlvcode(recordScopeList[x][y][0])
					marsfile.write("\tsw $t0 , "+ str(-(12+(4*counterOfPar))) + "($fp)\n")
			counterOfPar+=1

		# par , x , CP , _
		elif(currentQuad[0]=="par" and currentQuad[2]=="CP"):
			marsfile.write("L_"+str(i)+":\n")
			x,y=searchvar(currentQuad[1])
			checkParameters(counterOfPar,i)
			# X is Local
			if(x == nestingLevel):
				marsfile.write("\tlw $t0 , -"+ str(recordScopeList[x][y][len(recordScopeList[x][y])-1]) + "($sp)\n")
				marsfile.write("\tsw $t0 , "+ str(-(12+(4*counterOfPar))) + "($fp)\n")
			# Not Local
			else:
				gnlvcode(recordScopeList[x][y][0])
				marsfile.write("\tlw $t0 , ($t0)\n")
				marsfile.write("\tsw $t0 , "+ str(-(12+(4*counterOfPar))) + "($fp)\n")

		# par , x , RET , _
		elif(currentQuad[0] == "par" and currentQuad[2] == "RET"):
			x,y = searchvar(currentQuad[1])
			marsfile.write("L_"+str(i)+":\n")
			marsfile.write("\tadd $t0 , $sp , -"+str(recordScopeList[x][y][len(recordScopeList[x][y])-1]) +"\n")
			marsfile.write("\tsw $t0 , -8($fp)\n")


# Usefull Functions For Symbols Array
def record_entity(charName, type, argList):
	global recordEntityList,offsetTable,nestingLevel,recordScopeList,recordArgumentsList

	# Declarations
	if type == 'idDeclaration':
		recordEntityList.append([charName, offsetTable[nestingLevel]])
		recordScopeList[nestingLevel] = recordEntityList
		offsetTable[nestingLevel] += 4
		#print("offset ###### temp ",offsetTable[0])
	# Temporary variables
	elif type == 'temp':
		recordEntityList.append([charName, offsetTable[nestingLevel]])
		offsetTable[nestingLevel] += 4
		#print("offset ###### temp ",offsetTable[0])
	elif type == "func":
		# Entity Of Functions to Parent
		# [ nameOfFunc , [argumentsList...] , typeOfFunc ]
		temp = []
		temp.append(charName) # Name - First Element
		for i in range(len(argList)): # ArgumLists - SecondElement
			temp.append(argList[i])
		temp.append(type) # Type - Last Element
		# Go to Parent & Add it
		# '-1' will be changed
		recordScopeList[nestingLevel-1].append(temp)
	elif type == 'otherEntityOfFunction':
		# Add arguments as entity
		for i in range(len(recordArgumentsList)):
			recordEntityList.append([recordArgumentsList[i][0],recordArgumentsList[i][1],offsetTable[nestingLevel]])
			offsetTable[nestingLevel] += 4
		recordScopeList[nestingLevel] = recordEntityList

def record_arguments(name, type):
	global recordArgumentsList
	recordArgumentsList.append([name, type])

# Useful Functions
def nextQuad():
    global quads_line
    return quads_line+1

def genQuad(op,x,y,z):
    global quads,quads_line
    quads_line = nextQuad()
    quads[quads_line] = [str(op),str(x),str(y),str(z)]
    print(quads[quads_line])

def newTemp():
	global temp_counter
	temp_counter += 1
	tempName = "T_"+str(temp_counter)
	record_entity(tempName, 'temp', '')
	var_list.append(tempName)
	return tempName

def emptyList():
    empty_list = []
    return empty_list

def makeList(x):
    make_list = []
    make_list.append(x)
    return make_list

def mergeList(listone,listtwo):
	listone.extend(listtwo)
	return listone

def backPatch(currentList, label):
    for i in currentList:
        quads[i][3] = label

# ---------------------------------------------------------------------------------

# Lektikos Analytis
def lex():
	global ch,line,token,change
	positionOfChar = 0
	state = 0
	next = True
	word=''

	while(ch.isspace()):
		if(ch == '\n'):
		    line += 1
		ch = f.read(1)
		positionOfChar = f.tell()

	while next:
		#print("The character is : " , ch)
		#print("state = " , state)

		if state == 0:
			if ch.isalpha():
				state = 1
				token ='idtk'
			elif ch.isdigit():
				state = 2
				token = 'constanttk'
			elif ch == '<':
				state = 3
				token = 'lessThantk'
			elif ch == '>':
				state = 4
				token ='greaterThantk'
			elif ch == ':':
				state = 5
				token = 'colontk'
			elif ch == "/":
				state = 6
				token = 'divtk'
			elif ch == "+":
				next = False
				token = 'plustk'
			elif ch == "-":
				next = False
				token = 'minustk'
			elif ch == "*":
				next = False
				token = 'multk'
			elif ch == '=':
				next = False
				token = 'equaltk'
			elif ch == ",":
				next = False
				token = 'commatk'
			elif ch == ";":
				next = False
				token = 'semicolontk'
			elif ch == ')':
				next = False
				token = 'rightPartk'
			elif ch == ']':
				next = False
				token = 'rightBrackettk'
			elif ch == '(':
				token = "leftPartk"
				next = False
				checkParOrBra('(',')')
			elif ch == '[':
				token = "leftBrackettk"
				next = False
				checkParOrBra('[',']')
			elif not ch:
				createInt_File()
				createC_File()
				printError("---------- End Of File ---------- lines : " , line)
			else:
				printError("SyntaxError : 'Unknown character' \nLine' :  ", line)
			word+=ch
		elif state == 1:
			if not ch:
			    next = False
			elif (not ch.isalpha() and not ch.isdigit() ):
				f.seek(positionOfChar-1)
				next = False
			else:
			    word+=ch
			    word = word[:30]
		elif state == 2:
			if not ch.isdigit():
				if ch == '.':
					printError("SyntaxError : 'Starlet supports only integer numbers'.\nLine : ", line )
				elif ch.isalpha():
					printError("SyntaxError : 'Variables names cannot be started with number'.\nLine : ", line )
				else:
				    next = False
				    f.seek(positionOfChar-1)
			else:
				word+=ch
				if(int(word) > 32767):
					printError("SyntaxError : Starlet does not support number bigger than 32767 and lower than -32767.\nLine", line)
		elif state == 3:
			if ch == "=":
				next = False
				token = "lessOrEqualtk"
				word+=ch
			elif ch == ">":
				next = False
				token = "differenttk"
				word+=ch
			elif (ch.isdigit() or ch.isalpha()):
				f.seek(positionOfChar-1)
				next = False
			else:
				printError("SyntaxError : Unknown character \nLine : ", line)
		elif state == 4:
			if ch == "=":
				next = False
				token = "greaterOrEqualtk"
				word+=ch
			elif (ch.isdigit() or ch.isalpha()):
				f.seek(positionOfChar-1)
				next = False
			else:
				printError("SyntaxError : Unknown character \nLine : ", line)
		elif state == 5:
			if ch == "=":
				next = False
				token = "assignmenttk"
				word+=ch
			elif (ch.isdigit() or ch.isalpha()):
				f.seek(positionOfChar-1)
				next = False
		elif state == 6:
			if (ch.isdigit() or ch.isalpha()):
				f.seek(positionOfChar-1)
				next = False
			elif ch == "/":
				token = "commentsLinetk"
				# Searching for "\n"
				countColumns=0
				char = ''
				char=f.read(1)

				while (('\n' not in char) and countColumns<=100):
					if(('//' in char) or ('/*' in char)):
						print ("Error : Open comments in line: ", line , " for 2nd time")
						exit(1)
					char+=f.read(1)
					countColumns += 1
				#EndWhile
				pos=f.tell()
				f.seek(pos-1)
				next = False
			elif ch == "*":
				token = "commentsBlocktk"
				print ("CommentBlock is about to start, in line: " , line)

				# Searching for "\n"
				countColumns=0
				countNewLines=0
				countTimes=0
				char=''
				char=f.read(1)
				while (('*/' not in char) and (countColumns<=100)):
					if(('//' in char) or ('/*' in char)):
						if('\n' in char):
							countNewLines = char.count('\n')
							line += countNewLines
						print ("Error : Open comments in line: ", line , " for 2nd time")
						exit(1)
					if(char.count('\n') > countTimes):
						countTimes+=1
						countColumns=0
					c  = f.read(1)
					if(c == ''):
						print ("The commentsBlock never be closed in line :", line)
						exit(1)
					char+=c
					countColumns += 1
				#EndWhile
				pos=f.tell()
				f.seek(pos)
				next = False
				if('\n' in char):
				    countNewLines = char.count('\n')
				    line += countNewLines
			else:
			    #print("ch = ", ch)
			    printError("SyntaxErroor : Unknown character \nLine : ", line)

		ch = f.read(1)
		positionOfChar =  f.tell()
	#EndWhile

	#print("The word is : ",word)
	if word in keywords:
		token = keywords.get(word)
	elif word in symbols:
		if(token == 'commentsBlocktk' or token == 'commentsLinetk'):
		    lex()
		#print("The token is 2: ", token)
	#elif token == "constanttk":
	#	print("The token is 3: ", token)

	#print("The token is 4: ",token)

	return token,word

# ----------------------------------------------------------------------------------

# Syntaktikos Analutis
def program():
	global token,word,programName
	token,word = lex()
	if (token == "programtk"):
		token,word = lex()
		if (token == "idtk"):
			programName = word
			token,word = lex()
			block(programName)
			if (token == "endprogramtk"):
				token,word = lex()
			else:
				printError("SyntaxError : Not found the word 'endprogram' was expected in line : " , line)
		else:
			printError("SyntaxError : Invalid name for the function in line : " , line)
	else:
		printErrort("SyntaxError : Not found the word 'program' was expected in line : " , line)

def block(blockName):
    global programName,mainFrameLength,nestingLevel,quads,beginBlockCounter
    declarations()
    subprograms()
    genQuad('begin_block',blockName,'_','_')
	# -1 because of "begin_block"
    beginBlockCounter = len(quads)-1
    statements()
    if(blockName == programName):
        print("Scope can see:")
        for i in range(len(recordEntityList)):
            print("	The entity has [name , type , offset ]: -->> " ,recordEntityList[i])

        mainFrameLength = offsetTable[nestingLevel]
        print(" Framelength : ", mainFrameLength)
        create_FinalCode(len(quads))
        recordScopeList.pop(nestingLevel)
        del offsetTable[nestingLevel]
        nestingLevel-=1
        marsfile.write("L_"+str(nextQuad())+":\n")
        genQuad('halt','_','_','_')
    genQuad('end_block',blockName,'_','_')

def declarations():
	global token,word
	while (token=="declaretk"):
		token,word = lex()
		varlist()
		if (token=="semicolontk"):
			token,word = lex()
		else:	printError("SyntaxError : Not found the symbol ';' was expected in line :" , line)

def varlist():
	global token,word
	while (token == "idtk"):
		var_list.append(word)
		# For Symbols Array
		record_entity(word,'idDeclaration','')
		token,word=lex()
		while (token == "commatk"):
			token,word=lex()
			if (token == "idtk"):
				var_list.append(word)
				# For Symbols Array
				record_entity(word,'idDeclaration','')
				token,word=lex()
			else:	printError("SyntaxError : Invalid name for the function in line : " , line)

def subprograms():
	global token,word
	while (token=="functiontk"):
		subprogram()
# ---------------- Gia ta functions min 3exasw teliko kwdika
def subprogram():
	global token,word,offsetTable,nestingLevel,recordEntityList,recordScopeList
	if (token == "functiontk"):
		token,word=lex()
		blockName = word
		if (token == "idtk"):
			# StartQuad - NEW Scope - FirstOffset = 12
			nestingLevel+=1
			offsetTable.append(12) # adding element & init to 12
			recordEntityList = []
			recordArgumentsList = [] # Triangles
			token,word=lex()
			funcbody(blockName)
			if (token == "endfunctiontk"):
				print("Scope can see : ")
				for i in range(len(recordEntityList)):
					print("	The entity has [name , type , offset ]: -->> " ,recordEntityList[i])
				create_FinalCode(len(quads))
				# End of Function
				recordScopeList[nestingLevel-1][-1].append(offsetTable[nestingLevel])
				recordScopeList.pop(nestingLevel)
				del offsetTable[nestingLevel]
				nestingLevel-=1
				recordEntityList = recordScopeList[nestingLevel]
				token,word=lex()
			else:
				printError("SyntaxError : Not found the word 'endfunction' was expected in line : ",line)
		else:
			printError("SyntaxError : Invalid name for the function in line : ",line)
	else:
		printError("SyntaxError : Not found the word 'function' was expected in line : " ,line)

def funcbody(blockName):
	global recordArgumentsList
	formalpars()
	record_entity('','otherEntityOfFunction',recordArgumentsList)
	record_entity(blockName , 'func', recordArgumentsList)
	block(blockName)

def formalpars():
	global token,word
	if (token == "leftPartk"):
		token,word=lex()
		formalparlist()
		if (token == "rightPartk"):
			token,word=lex()
		else:
			printError("SyntaxError : Not found the symbol ')' was expected in line : ", line)
	else:
		printError("SyntaxError : Not found the symbol '(' was expected in line : ", line)

def formalparlist():
	global token,word
	formalparitem()
	while (token == "commatk"):
		token,word=lex()
		formalparitem()

def formalparitem():
	global token,word
	if (token == "intk"	or token == "inouttk" or token == "inandouttk"):
		type = word
		token,word=lex()
		if (token == "idtk"):
			record_arguments(word, type)
			token,word=lex()
		else:
			printError("SyntaxError : Invalid name for the argument of the function in line : " , line)

def statements():
	global token,word
	statement()
	while (token == "semicolontk"):
		token,word=lex()
		statement()

def statement():
	global token,word
	if(token == "idtk"):
		A1place = word
		token,word=lex()
		assignment_stat(A1place)
	elif(token == "iftk"):
		token,word=lex()
		if_stat()
	elif(token == "whiletk"):
		token,word=lex()
		while_stat()
	elif(token == "dowhiletk"):
		token,word=lex()
		do_while_stat()
	elif(token == "looptk"):
		token,word=lex()
		loop_stat()
	elif(token == "exittk"):
		token,word=lex()
		exit_stat()
	elif(token == "forcasetk"):
		token,word=lex()
		forcase_stat()
	elif(token == "incasetk"):
		token,word=lex()
		incase_stat()
	elif(token == "returntk"):
		token,word=lex()
		return_stat()
	elif(token == "inputtk"):
		token,word=lex()
		input_stat()
	elif(token == "printtk"):
		token,word=lex()
		print_stat()

def assignment_stat(A1place):
	#A1place is id
	global token,word
	if (token == "assignmenttk"):
		token,word=lex()
		A2place = expression()
		genQuad(':=',A2place,'_',A1place)
	else:
		printError("SyntaxError : Not found the symbol ':=' was expected in line : ", line)

def if_stat():
	global token,word
	if (token=="leftPartk"):
		token,word=lex()
		ifTrue, ifFalse = condition()
		if (token=="rightPartk"):
			token,word=lex()
			if (token=="thentk"):
				token,word=lex()
				# P1
				backPatch(ifTrue,nextQuad())
				statements()
				# P2
				ifList = makeList(nextQuad())
				genQuad('jump','_','_','_')
				backPatch(ifFalse,nextQuad())
				elsepart()
				# P3
				backPatch(ifList,nextQuad())
				if (token=="endiftk"):
					token,word=lex()
				else:
					printError("SyntaxError : Not found the word 'endif' was expected in line : ",line)
			else:
				printError("SyntaxError : Not found the word 'then' was expected in line : ",line)
		else:
			printError("SyntaxError : Not found the symbol ')' was expected in line : ",line)
	else:
		printError("SyntaxError : Not found the symbol '(' was expected in line : ",line)

def elsepart():
	global token,word
	if (token == "elsetk"):
		token,word=lex()
		statements()

def while_stat():
	global token,word
	if (token=="leftPartk"):
		token,word=lex()
		# P1
		whileQuad = nextQuad()
		# --
		whileTrue, whileFalse = condition()
		if (token=="rightPartk"):
			token,word=lex()
			# P2
			backPatch(whileTrue,nextQuad())
			# --
			statements()
			# P3
			genQuad('jump','_','_',whileQuad)
			backPatch(whileFalse,nextQuad())
			# --
			if (token=="endwhiletk"):
				token,word=lex()
			else:
				printError("SyntaxError : Not found the word 'endwhile' was expected in line : ",line)
		else:
			printError("SyntaxError : Not found the symbol ')' was expected in line : ",line)
	else:
		printError("SyntaxError : Not found the word '(' was expected in line : ",line)

def do_while_stat():
	global token,word
	# P1
	dowhileQuad = nextQuad()
	# --
	statements()
	if (token=="enddowhiletk"):
		token,word=lex()
		if (token=="leftPartk"):
			token,word=lex()
			dowhileTrue, dowhileFalse = condition()
			# P2
			backPatch(dowhileTrue, dowhileQuad)
			backPatch(dowhileFalse, nextQuad())
			# --
			if (token=="rightPartk"):
				token,word=lex()
			else:
				printError("SyntaxError : Not found the symbol ')' was expected in line : ",line)
		else:
			printError("SyntaxError : Not found the symbol '(' was expected in line : ",line)
	else:
		printError("SyntaxError : Not found the word 'enddowhile' was expected in line : ",line)

def loop_stat():
	global token,word,forLoopList
	# P0
	firstQuad=nextQuad()
	statements()
	# For exit
	backPatch(forLoopList,nextQuad()+1)
	# P1
	genQuad('jump','_','_',firstQuad)
	if (token == "endlooptk"):
		token,word=lex()
	else:
		printError("SyntaxError : Not found the word 'endloop' was expected in line : ",line)

def exit_stat():
	global token,word,forLoopList
	forLoopList = makeList(nextQuad())
	genQuad('jump','_','_','_')

def forcase_stat():
	global token,word
	# P0
	exitList = emptyList()
	forcaseCond=nextQuad()
	while (token == "whentk"):
		token,word=lex()
		if(token == "leftPartk"):
			token,word=lex()
			# P1
			condTrue, condFalse = condition()
			backPatch(condTrue, nextQuad())
			if(token == "rightPartk"):
				token,word=lex()
				if (token == "colontk"):
					token,word=lex()
					statements()
					# P2
					t = makeList(nextQuad())
					genQuad('jump','_','_','_')
					mergeList(exitList,t)
					backPatch(condFalse, nextQuad())
				else:
					printError("SyntaxError : Not found the symbol ':' was expected in line : ",line)
			else:
				printError("SyntaxError : Not found the symbol ')' was expected in line : ",line)
		else:
			printError("SyntaxError : Not found the symbol '(' was expected in line : ",line)

	if (token == "defaulttk"):
		token,word=lex()
		if (token == "colontk"):
			token,word=lex()
			statements()
			if (token == "enddefaulttk"):
				token,word=lex()
				# P3
				genQuad('jump','_','_',forcaseCond)
				backPatch(exitList,nextQuad())
				if (token == "endforcasetk"):
					token,word=lex()
				else:
					printError("SyntaxError : Not found the word 'endforcase' was expected in line : ",line)
			else:
				printError("SyntaxError : Not found the word 'enddefault' was expected in line : ",line)
		else:
			printError("SyntaxError : Not found the symbol ':' was expected in line : ",line)
	else:
		printError("SyntaxError : Not found the word 'default' was expected in line : ",line)

def incase_stat():
	global token,word
	# P0
	flag = newTemp()
	firstQuad = nextQuad()
	genQuad(':=','0','_',flag)
	while (token=="whentk"):
		token,word=lex()
		if (token=="leftPartk"):
			token,word=lex()
			# P1
			condTrue, condFalse = condition()
			backPatch(condTrue, nextQuad())
			if (token=="rightPartk"):
				token,word=lex()
				if (token=="colontk"):
					token,word=lex()
					statements()
					# P2
					genQuad(':=','1','_',flag)
					backPatch(condFalse, nextQuad())
				else:
					printError("SyntaxError : Not found the symbol ':' was expected in line : ",line)
			else:
				printError("SyntaxError : Not found the symbol ')' was expected in line : ",line)
		else:
			printError("SyntaxError : Not found the symbol '(' was expected in line : ",line)

    # P3
	genQuad('=',flag,'1',firstQuad)
	if (token=="endincasetk"):
		token,word=lex()
	else:
		printError("SyntaxError : Not found the word 'endincase' was expected in line : ",line)

def return_stat():
	global token,word
	Eplace = expression()
	genQuad('retv',Eplace,'_','_')

def print_stat():
	global token,word
	Eplace = expression()
	genQuad('out',Eplace,'_','_')

def input_stat():
	global token,word
	if (token == "idtk"):
		Idplace = word
		genQuad('inp',Idplace,'_','_')
		token,word=lex()
	else:
		printError("SyntaxError : Invalid name as input in line : ",line)

def actualpars():
	global token,word
	if (token == "leftPartk"):
		token,word=lex()
		actualparlist()
		if (token == "rightPartk"):
			w = newTemp()
			genQuad('par',w,'RET','_')
			token,word=lex()
			return w
		else:
			printError("SyntaxError : Not found the symbol ')' was expected in line : ",line)
	else:
		printError("SyntaxError : Not found the symbol '(' was expected in line : ",line)

def actualparlist():
	global token,word
	actualparitem()
	while (token == "commatk"):
		token,word=lex()
		actualparitem()

def actualparitem():
	global token,word
	if (token == "intk"):
		token,word=lex()
		if (token == "idtk"):
			A1place = expression()
			genQuad('par',A1place,'CV','_')
		else:
			printError("SyntaxError : Invalid name as argument on the function in line : ",line)
	elif(token == "inouttk"):
		token,word=lex()
		if (token == "idtk"):
			A1place = word
			genQuad('par',A1place,'REF','_')
			token,word=lex()
		else:
			printError("SyntaxError : Invalid name as argument on the function in line : ",line)
	elif (token=="inandouttk"):
		token,word=lex()
		if (token == "idtk"):
			A1place = word
			genQuad('par',A1place,'CP','_')
			token,word=lex()
		else:
			printError("SyntaxError : Invalid name as argument on the function in line : ",line)
	else:
		printError("Starlet supports specific type [in , inout , inandout]\nSyntaxError : Invalid type in line : ",line)

def condition():
	global token,word
	Btrue1 , Bfalse1 = boolterm()
	while (token == "ortk"): # B - OR
		token,word=lex()
		backPatch(Bfalse1 , nextQuad())
		# -----
		Btrue2 , Bfalse2 = boolterm()
		# -----
		Btrue1 = mergeList(Btrue1 , Btrue2)
		Bfalse1 = Bfalse2
	return Btrue1 , Bfalse1

def boolterm():
	global token,word
	Qtrue1 , Qfalse1 = boolfactor()
	while (token == "andtk"): # Q - AND
		token,word=lex()
		backPatch(Qtrue1 , nextQuad())
		# -----
		Qtrue2 , Qfalse2 = boolfactor()
		# -----
		Qfalse1 = mergeList(Qfalse1 , Qfalse2)
		Qtrue1 = Qtrue2
	return Qtrue1 , Qfalse1

def boolfactor():
	global token,word,condR_TrueList,condR_FalseList,isThereNot
	if (token == "nottk"):
		token,word=lex()
		if(token == "leftBrackettk"):
			token,word=lex()
			condition()
			isThereNot = True
			if(token == "rightBrackettk"):
				token,word=lex()
			else:
				printError("SyntaxError : Not found the symbol ']' was expected in line : ",line)
		else:
			printError("SyntaxError : Not found the symbol '[' was expected in line : ",line)
	elif (token == "leftBrackettk"):
		token,word=lex()
		condition()
		if (token == "rightBrackettk"):
			token,word=lex()
		else:
			printError("SyntaxError : Not found the symbol ']' was expected in line : ",line)
	else:
		E1place = expression() # Q || R
		relop = relational_oper()
		E2place = expression() # Q || R
		condR_TrueList = makeList(nextQuad())
		genQuad(relop , E1place , E2place, '_')
		condR_FalseList = makeList(nextQuad())
		genQuad('jump','_','_','_')
	if isThereNot:
		isThereNot = False
		return condR_FalseList,condR_TrueList
	else:
		return condR_TrueList,condR_FalseList

def expression():
	global token,word
	prosimo = optional_sign()
	T1place = prosimo + term()
	while (token == "plustk" or token == "minustk"):
		if(token == "plustk"):
			add_oper()
			T2place = term()
			w = newTemp()
			genQuad('+',T1place,T2place,w)
			T1place = w
		elif(token == "minustk"):
			add_oper()
			T2place = term()
			w = newTemp()
			genQuad('-',T1place,T2place,w)
			T1place = w
	Eplace = T1place
	return Eplace

def term():
	global token,word
	F1place = factor()
	while (token == "multk" or token == "divtk"):
		if(token == "multk"):
			mul_oper()
			F2place = factor()
			w = newTemp()
			genQuad('*',F1place,F2place,w)
			F1place = w
		elif(token == "divtk"):
			mul_oper()
			F2place = factor()
			w = newTemp()
			genQuad('/',F1place,F2place,w)
			F1place = w
	Tplace = F1place
	return Tplace

def factor():
	global token,word
	if (token == "constanttk"):
		Fplace = word
		token,word=lex()
	elif (token == "leftPartk"):
		token,word=lex()
		Fplace = expression()
		if (token == "rightPartk"):
			token,word=lex()
		else:
			printError("SyntaxError : Not found the symbol ')' was expected in line : ",line)
	elif (token == "idtk"):
		Fplace = word
		token,word=lex()
		retValue = idtail()
		if(retValue != '-1'):
			genQuad('call',Fplace,'_','_')
			Fplace = retValue
	return Fplace

def idtail():
	global token,word
	if (token=="leftPartk"):
		retValue = actualpars()
		return retValue
	return '-1'

def relational_oper():
	global token,word
	if (token == "equaltk") :		  # =
		relop = word
		token,word=lex()
	elif (token == "lessThantk"): 	  # <
		relop = word
		token,word=lex()
	elif (token == "lessOrEqualtk"):  # <=
		relop = word
		token,word=lex()
	elif (token == "differenttk"):	  # <>
		relop = word
		token,word=lex()
	elif (token == "greaterThantk"):  # >
		relop = word
		token,word=lex()
	elif (token == "greaterOrEqualtk"): # >=
		relop = word
		token,word=lex()
	return relop

def add_oper():
	global token,word
	token,word=lex()

def mul_oper():
	global token,word
	token,word=lex()

def optional_sign():
	global token
	if(token == "plustk"):
		add_oper()
		return '+'
	elif (token == "minustk"):
		add_oper()
		return '-'
	return ''

# ----------------------------------------------------------------------------------
def createInt_File():
	global quads
	for k,v in quads.items():
		intfile.write( str(k) + ' : ' + str(v)+'\n')

def createC_File():
	global quads,var_list
	cfile.write('#include <stdio.h> \n\nint main()\n{\n  int ')
	i=0
	for i in range(len(var_list)-1):
		cfile.write(var_list[i]+',')
	cfile.write(var_list[i+1]+ ';\n')

	i=0
	for i in range(len(quads)):
		if (quads[i][0]==':='):
			cfile.write('  L_'+str(i)+': '+quads[i][3]+'='+quads[i][1]+';\n')
		elif(quads[i][0]=='+' or quads[i][0]=='-' or quads[i][0]=='*' or quads[i][0]=="/"):
			cfile.write('  L_'+str(i)+': '+quads[i][3] + '=' + quads[i][1] + quads[i][0]+quads[i][2]+';\n')
		elif(quads[i][0] == 'jump'):
			cfile.write('  L_'+str(i)+': '+'goto '+'L_'+str(quads[i][3])+';\n')
		elif(quads[i][0] == '=' or quads[i][0] == '<>' or quads[i][0]== '>=' or quads[i][0] == '<' or quads[i][0] == '>' or quads[i][0] == '<='):
			if(quads[i][0]== '='):
				cfile.write('  L_'+str(i)+': '+str('if')+'('+str(quads[i][1])+'=='+str(quads[i][2])+')' +' goto L_'+str(quads[i][3])+';\n')
			elif(quads[i][0]== '<>'):
				cfile.write('  L_'+str(i)+': '+str('if')+'('+str(quads[i][1])+'!='+str(quads[i][2])+')' +' goto L_'+str(quads[i][3])+';\n')
			else:
				cfile.write('  L_'+str(i)+': '+str('if')+'('+str(quads[i][1])+str(quads[i][0])+str(quads[i][2])+')' +' goto L_'+str(quads[i][3])+';\n')

		elif(quads[i][0]=='halt'):
			cfile.write('  L_'+str(i)+':  {}\n')
		elif(quads[i][0] == 'beginBlock' or quads[i][0] == 'endBlock'):
			continue
		elif(quads[i][0] == 'out'):
			cfile.write('  L_'+str(i)+': printf("%d""\\n",' +str(quads[i][1])+');\n')

	cfile.write('}\n')

def printError(msg, numLine):
    print(msg , numLine)
    exit(1)

def checkParOrBra(symbol1,symbol2):
    global lineOfPar,change
    currentLine = line
    countColumns=0
    start=f.tell()
    char=f.read(1)
    if(currentLine > lineOfPar):
        change = True
    if(change == True):
        lineOfPar = line
        change = False
        while ('\n' not in char):
            if(countColumns>=100):
                printError("SyntaxError : The left parenthesis/bracket never be closed in line :", line )
            char+=f.read(1)
            countColumns += 1
        counterOfLeft = char.count(symbol1) + 1
        counterOfRight = char.count(symbol2)
        if(counterOfLeft > counterOfRight):
            printError("SyntaxError : There are more left parenthesis/brackets than right ones in line :", line)
        elif(counterOfLeft < counterOfRight):
            printError("SyntaxError : There are more right parenthesis/brackets than left ones in line :", line)
	# Start reading the file from the right byte
    f.seek(start)
# ----------------------------------------------------------------------------------
token = ""
word = ""
programName = ""
forLoopList=[]
isThereNot = False
condR_TrueList = emptyList()
condR_FalseList = emptyList()

global change
if (len(sys.argv)>2 or len(sys.argv)<2):
    sys.exit('Give 2 arguments')
else:
	infile = sys.argv[1]

if not os.path.exists(infile[:-4]):
	os.makedirs(infile[:-4])

path = infile[:-4]+'/'+infile[:-3]+'int'
intfile = open(path,"w")
path = infile[:-4]+'/'+infile[:-3]+'c'
cfile = open(path,"w")
path = infile[:-4]+'/'+infile[:-3]+'asm'
marsfile = open(path,"w")
marsfile.write("#MARS File created by Starlet\n\n.data\n.asciiz\n.text\n\n")
marsfile.write("\tj Lmain\n")

with open(infile,'r') as f:
    global ch,line,lineOfPar
    lineOfPar = -1
    line = 1
    ch = f.read(1)
    if not ch:
    	sys.exit("Empty File")
    program()

infile.close()
marsfile.close()
intfile.close()
cfile.close()
sys.exit()
