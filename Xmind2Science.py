from mekk.xmind import XMindDocument
import re
import logging
logging.basicConfig()
##with open("test.txt") as f:
##    content = f.readlines()
##    print content

def dropDuplicate(l):
    seen = set()
    seen_add = seen.add
    return [ x for x in l if x not in seen and not seen_add(x)]

def getMarkers(topic):
    ms=topic.get_markers()
    return ms

def xmindWalk_getMarkers(topic,values=[]):
    topics=topic.get_subtopics()
    for subtopic in topics:
        markers=subtopic.get_markers()
        for marker in markers:
            values.append(marker)
        xmindWalk_getMarkers(subtopic,values)
    return values

def takeText(marker,m_title,m_text,m_ref,title):
    if((marker==m_title)or(marker==m_text)or(marker==m_ref)):
        title=title.replace("\r\n"," ")
        title=title.replace("  "," ")
        while(title[-1]==".")or(title[-1]==" "):
            title=title[:-1]
        while(title[0]==" "):
            title=title[1:]  
        return title,marker
    else:
        return "",""

def TextCompiler(title,fulltext,ref,texts):
    noParenthesis=False
    finaltext=""
##            if(title[0].isupper()):
##            title=". "+title
##          
    oldTtype=title
    for text in texts:
        Ttype=text[1]
        words=text[0]
        if(Ttype!=ref)and(oldTtype==ref):
            if(noParenthesis):
                finaltext=finaltext+"___ "#the upper bar is temporary
                noParenthesis=False
            else:
                finaltext=finaltext+")___ "#the upper bar is temporary
        if(Ttype==title):
            finaltext+="\n\n"+words+"\n\n"
        if(Ttype==fulltext):
            if(oldTtype!=title):
                if(words[0].isupper()):
                    finaltext+=". "+words
                else :
                    finaltext+=" "+words
            else:
                finaltext+=words
        if(Ttype==ref):
            if(oldTtype==ref):
                finaltext+="; "+words
            else:
                if(words[-1]==")"):
                    noParenthesis=True
                    finaltext+=" ___"+words#the upper bar is temporary
                else :
                    finaltext+=" ___("+words#the upper bar is temporary
        oldTtype=Ttype
    return finaltext
    
    

def xmindWalk_TextCompiler(topic,m_title,m_text,m_ref,texts):
    title=topic.get_title()
    markers=topic.get_markers()
    for marker in markers:
        [text,typeText]=takeText(marker,m_title,m_text,m_ref,title)
        texts.append([text,typeText])
    subtopics=topic.get_subtopics()
    for subtopic in subtopics:
        texts=xmindWalk_TextCompiler(subtopic,m_title,m_text,m_ref,texts)
    return texts


def replaceReferences(references,sources,text1):
    index=0
    parts=[]
    for reference in references:
        for source in sources:
            if(source[0]>reference[0]):
                parts.append(text1[index:reference[0]])
                parts.append(text1[source[0]:source[1]]+text1[reference[1]:source[0]])
                print(text1[source[0]:source[1]]+text1[reference[1]:source[0]])
                index=source[1]
                break
    parts.append(text1[index:])
    text="".join(parts)
    text=text.replace("___","")
    return text
    
##    texts=[]
##    topics=topic.get_subtopics()
##    refcounter=0
##    for subtopic in topics:
##        texts.append(xmindWalk_TextCompiler(subtopic,m_title,m_text,m_ref,text,i+1))
##        print("enter subtopic")
##        markers=subtopic.get_markers()
##        for marker in markers:
##            #print (marker,refcounter,m_title,m_text,m_ref,subtopic.get_title(),text)
##            
##            print(text)
##
##    text="".join(texts)
##    if(refcounter!=0):
##        text=text[0:-1]+")"
##    return text

Manual=True
if(Manual):
    Xmindfile=raw_input("name of your xmind file : ")
else :
    Xmindfile="article.xmind"

pref_target = re.compile('('
               +'\('
               +'ref'
               +'\)'
               +')')
pref_source = re.compile('('
               +'___'
               +'.*?'
               +'\)___)')
xmind = XMindDocument.open(Xmindfile)
first_sheet = xmind.get_first_sheet()
root_topic = first_sheet.get_root_topic()
#style=root_topic.get_style()
#print(style)
markers=(dropDuplicate(xmindWalk_getMarkers(root_topic)))
markers.append("none")
message="Your markers are : "
for i,marker in enumerate(markers):
    message+=marker+"("+str(i)+") ; "
print message[0:-2]
if(Manual):
    titleId=int(raw_input("choose the index of marker for title (choose none if none ) : "))
    textId=int(raw_input("choose the index of marker for full text (choose none if none ) : "))
    refsId=int(raw_input("choose the index of marker for references (choose none if none ) : "))
    output=raw_input("choose the name of the file that will be created : ")
else:
    titleId=0
    textId=1
    refsId=2
    texts=xmindWalk_TextCompiler(root_topic,markers[titleId],markers[textId],markers[refsId],[] )
    output="input4.txt"
texts=xmindWalk_TextCompiler(root_topic,markers[titleId],markers[textId],markers[refsId],[])
text1=TextCompiler(markers[titleId],markers[textId],markers[refsId],texts)
references=[[m.start(0),m.end(0)] for m in pref_target.finditer(text1)]
sources=[[m.start(0),m.end(0)] for m in pref_source.finditer(text1)]
print(references)
print(sources)
text1=replaceReferences(references,sources,text1)
text1=text1.encode('ascii', 'ignore')
output=output.replace(".txt","")+".txt"
with open(output, "w") as text_file:
    text_file.write(text1)
print("the result has been stored in "+output)

