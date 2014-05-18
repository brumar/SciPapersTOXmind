from mekk.xmind import XMindDocument
import re
import chardet
import codecs



def setStyleAndMarker(topic,idTopic):
    if(idTopic=="text"):
        topic.add_marker(information)
        topic.set_style(style_text)
    if(idTopic=="ref"):
        topic.add_marker(ref)
        topic.set_style(style_ref)

def setStyleAndMarker_map(topic):
    topics=topic.get_subtopics()
    for subtopic in topics:
        setStyleAndMarker(subtopic,subtopic.get_embedded_id())
        setStyleAndMarker_map(subtopic)

def openText(filename):
    lines=""
    det=(chardet.detect(open(filename).read()))
    text = " ".join([ line for line in codecs.open(filename,"r",det["encoding"])])
    text=text.replace("-\r\n ","")
    text=text.replace("-\r\n","")
    text=text.replace("\r\n","")
    text=text.replace("\n","")
    text=text.replace("(e.g., ","(")
    text=text.replace("(e.g. ","(")
    return text

def reduceTitle(title,topic_type):
    ratio=int(len(title)/maxLength)
    absoluteVariation=0
    for i in range(1,ratio):
        index=maxLength*i+absoluteVariation
        while(title[index]!=" "):
            absoluteVariation+=1
            index+=1
        title=title[0:index]+"\n"+title[index+1:]
    return title

def niceAddTopic(topic_father,topic_title,topic_type):
    title=reduceTitle(topic_title,topic_type)
    topic_father.add_subtopic(title,topic_type)

def createMapFromLines(listOflines,listOfSublines,xmind):
    r=xmind.get_first_sheet().get_root_topic()
    r.set_style(style_root)
    r.add_subtopic("plan","planId").set_style(style_plan)
    subs=r.get_subtopics()
    plan=subs.next()
    for l,line in enumerate(listOflines):
        niceAddTopic(plan,line,"text")             
    subs=plan.get_subtopics()
    for s,sub in enumerate(subs):
        if (listOfSublines[s]!=""):
             for ref in listOfSublines[s]:
                niceAddTopic(sub,ref,"ref")
    return xmind
                
def breakTextInLines(text):
    text=text.replace("  "," ")
    textSequencing=[]
    breakLinesUnsures=[m.end(0) for m in re.finditer("\. ", text)] #First condition : presence of '.'
    start=0
    for breakLinesUnsure in breakLinesUnsures:
        if((breakLinesUnsure<len(text))and(text[breakLinesUnsure].isupper())): #Second condition : presence of capital letter just after
            textSequencing.append(text[start:breakLinesUnsure])
            start=breakLinesUnsure
    textSequencing.append(text[start:])  
    return(textSequencing)

def breakTextInLines_second(textSequencing):
    textSequencing2=[]
    for line in textSequencing:
        start=0
        nb_par=len(p.findall(line))
        if nb_par>1:
            breakLines=[m.end(0) for m in p.finditer(line)]
            for breakLine in breakLines:
                textSequencing2.append(line[start:breakLine])
                start=breakLine
            textSequencing2.append(line[start:])
        else :
            textSequencing2.append(line[start:])
    return textSequencing2
            
def repairPunctuation(lines):
    ##step 1 detect punctuation in line beginning and send them back at the end of the previous line.
    lines2=[]
    oldline=lines.pop(0)
    lines2.append(oldline)
    for l,line in enumerate(lines):
        lines2.append(line)
        if (line[0]=="." or line[0]==","):
            lines2[l]=lines2[l]+line[0]
        oldline=line
    ##step 2 delete white space and punctuation at the beginning of each line.
    lines3=[]
    for line in lines2:
        while((line!="")and(line[0]=="." or line[0]=="," or line[0]==" ")):
            line=line[1:]
        lines3.append(line)
    return lines3
            

def createLinesAndSublines(textSequencing):
    listOfSublines=[""]*len(textSequencing)
    listOflines=[]
    for l,line in enumerate(textSequencing):
        sublineStart=0
        sublineEnd=0
        sublines=[]
        breakLines=[[m.start(0),m.end(0)] for m in p.finditer(line)]
        for breakLine in breakLines:
            replace=""
            if(len(line)-m.end(0)>2):
                replace=" (ref) "
            listOfSublines[l]=line[breakLine[0]+1:breakLine[1]-1].split("; ")
            line=line.replace(line[breakLine[0]:breakLine[1]],replace)             
        listOflines.append(line)
    return listOflines,listOfSublines


#options -start
maxLength=80
xmind = XMindDocument.create("sheet1","article")
information="52r5pnqlh67gsj8d1v0469s1fm"
ref="1t2ehckaq1o9cnnnb0ru8k5a53"
xmind.embed_markers("PackageCompiler.xmp")
style_plan=XMindDocument.create_topic_style(xmind,'#80FF80',"org.xmind.topicShape.rectangle","#CACACA",line_width = "2pt")
style_text=XMindDocument.create_topic_style(xmind,'#CEFFCE',"org.xmind.topicShape.rectangle","#CACACA",line_width = "1pt")
style_ref=XMindDocument.create_topic_style(xmind,'#E5E5E5',"org.xmind.topicShape.roundedRect","#CACACA",line_width = "1pt")
style_root=XMindDocument.create_topic_style(xmind,'#37D02B',"org.xmind.topicShape.roundedRect","#CACACA",line_width = "3pt")
p = re.compile('('
               +'\('
               +'[^\d)]'
               +'[^\)]*?'
               +'\d\d\d\d'
               +'.*?'
               +'\)'
               +')')

#options -end
filename=raw_input("give the name of the text file in this directory you want to map : ")
output=raw_input("give the name of the xmind file that will be generated : ")
text=openText(filename)
textSequencing=breakTextInLines(text)##break the text in lines (each sentence=>a line)
textSequencing=breakTextInLines_second(textSequencing)## continue to break but when references are detected
listOflines,listOfSublines=createLinesAndSublines(textSequencing) #seperate lines and sublines
listOflines=repairPunctuation(listOflines)
xmind=createMapFromLines(listOflines,listOfSublines,xmind)
setStyleAndMarker_map(xmind.get_first_sheet().get_root_topic())
xmind.save(output)
print("done")
   

## numberLines=len(line)/carlim
##    for i,car in enumerate(line):
##        if (car=="("):
##            print("open at "+str(i))
##        if (car==")"):
##            print("close at "+str(i))
