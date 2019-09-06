from classes import *
from peewee  import *
from types   import *
import json
import inspect
from datetime import date



#add person
def addIndividual(firstName,lastName,dob,dod,gender,familyID):
    individual=Individual(firstName=firstName,lastName=lastName,dob=dob,dod=dod,gender=gender,familyId=familyID)
    individual.save()
    return individual.id
#init a root family
def initFamily(paternal,maternal):
    family=Family(paternalFamily=paternal,maternalFamily=maternal,root=0)
    family.save()
    return family.id

def initRootFamily(paternal,maternal):
    family=Family(paternal=paternal,maternal=maternal,root=1)
    family.save()
    return family.id

#add child to family
def linkChild(familyId,IndividualId):
    child=Children(familyId=familyId,childId=IndividualId)
    child.save()



def addRelation(name):
    relation=Relation(name=name)
    relation.save()

def addCondition(name):
    condition=Condition(name=name)
    condition.save()

def addResource(name):
    condition=Resource(name=name)
    condition.save()



def addPolicy(resources,individual):
    policy=Policy(author=individual,resources=resources)
    policy.save()
    return policy.id


def addRule(type, anon,condition,relation,policy):
    rule=Rule(type=type,anon=anon,condition=condition,relation=relation,policyId=policy)
    rule.save()

##mainly for never when instead is needed
def addRuleWithInstead(type, anon,condition,relation,policy,instead):
    rule=Rule(type=type,anon=anon,condition=condition,relation=relation,policy=policy,instead=instead)
    rule.save()




#reterive relatives

def siblings(id):##id is and individual not just number... so adjust how all relation function is written to speed up the process
    siblings=set()
    ind=Individual.get_by_id(id)
    fam=Family.get_by_id(ind.familyId)
    for i in fam.children:
        if(i.id!=id):
            siblings.add(i)
    return siblings


def parents(id):
    fam=getIndividualInfo(id)[1]
    mam=Individual.get_by_id(fam.maternal)
    dad=Individual.get_by_id(fam.paternal)
    return {mam, dad}

def mam(id):
    fam=getIndividualInfo(id)[1]
    mam=Individual.get_by_id(fam.maternal)
    return {mam}
def dad(id):
    fam=getIndividualInfo(id)[1]
    dad=Individual.get_by_id(fam.paternal)
    return {dad}

def  children(id):
     children=set()
     info=getIndividualInfo(id)
     fam=info[1]
     ind=info[0]
     families=[]
     for f in getFamiliesForIndividual(ind.id):
        for i in f.children:
                children.add(i)
     return children

def partners(id):
    ##updatee family schema to make maternal & paternal as foreign keys
    partners=set()
    families=getFamiliesForIndividual(id)
    ind=getIndividual(id)
    for f in families:
        partners.add(getIndividual(f.maternal) if ind.gender=="M" else getIndividual(f.paternal))
    
    return partners
    
def grandParents(id):
    grandParents=set()
    info=fam=getIndividualInfo(id)
    maternalFam=getMaternalFamily(id,info[1]) #Mom Family 
    paternalFam=getPaternalFamily(id,info[1]) #Dad Family

    grandParents.add(getIndividual(maternalFam.maternal))
    grandParents.add(getIndividual(maternalFam.paternal))
    grandParents.add(getIndividual(paternalFam.maternal))
    grandParents.add(getIndividual(paternalFam.paternal))

    return grandParents
    

def grandChildren(id):
    grandChildren=set()
    for c in getFamiliesForIndividual(id):
        #for every child we need to print his children
        for c in c.children:
            for f in getFamiliesForIndividual(c):
                for gc in f.children:
                    grandChildren.add(gc)
    
    return grandChildren

def firstDegree(id):
    all=set()
    all.update(parents(id))
    all.update(siblings(id))
    all.update(children(id))

    return all

def sisters(id):
    sisters=set()
    ind=Individual.get_by_id(id)
    fam=Family.get_by_id(ind.familyId)
    for i in fam.children:
        if(i.gender=="F" and i.id!=id):
            sisters.add(i)

    return sisters
    
def brothers():
    brothers=set()
    ind=Individual.get_by_id(id)
    fam=Family.get_by_id(ind.familyId)
    for i in fam.children:
        if(i.gender=="M"):
            brothers.add(i)
    return brothers
def secondDegree(id):
    all=set()
    all.update(uncles(id))
    all.update(aunts(id))
    all.update(grandParents(id))
    all.update(grandChildren(id))
    return all
def uncles(id):
    uncles=set()
    info=fam=getIndividualInfo(id)
    maternalFam=getMaternalFamily(id,info[1]) #Mom Family 
    paternalFam=getPaternalFamily(id,info[1]) #Dad Family

    dontPrint=info[0].familyId.paternal

    uncles.update(returnOnlyGender(maternalFam.children,"M",dontPrint))
    uncles.update(returnOnlyGender(paternalFam.children,"M",dontPrint))
    return uncles
def maternalUncles(id):
    info=fam=getIndividualInfo(id)
    maternalFam=getMaternalFamily(id,info[1]) #Mom Family   
    return returnOnlyGender(maternalFam.children,"M",None)

def paternalUncles(id):
    info=fam=getIndividualInfo(id)
    paternalFam=getPaternalFamily(id,info[1]) #DAD Family 
    dontPrint=info[0].familyId.paternal
    
    return returnOnlyGender(paternalFam.children,"M",dontPrint)

def aunts(id):
    aunts=set()
    info=fam=getIndividualInfo(id)
    maternalFam=getMaternalFamily(id,info[1]) #Mom Family 
    paternalFam=getPaternalFamily(id,info[1]) #Dad Family
    
    dontPrint=info[0].familyId.maternal

    aunts.update(returnOnlyGender(maternalFam.children,"F",dontPrint))
    aunts.update(returnOnlyGender(paternalFam.children,"F",dontPrint))
    return aunts
def maternalAunts(id):
    info=fam=getIndividualInfo(id)
    maternalFam=getMaternalFamily(id,info[1]) #Mom Family  

    dontPrint=info[0].familyId.maternal
    return returnOnlyGender(maternalFam.children,"F",dontPrint)
def paternalAunts(id):
    info=fam=getIndividualInfo(id)
    paternalFam=getPaternalFamily(id,info[1]) #Mom Family  
    return returnOnlyGender(paternalFam.children,"F",None)




#will be implemented at later time
def nephew(id):
    pass
def niece(id):
    pass
def twins(id):
    pass
def maternalSiblings(id):
    pass
def paternalSiblings(id):
    pass

interface={
        "siblings()":siblings,
        "maternalSiblings()":maternalSiblings,
        "paternalSiblings()":paternalSiblings,
        "parents()":parents,
        "mother()":mam,
        "father()":dad,
        "children()":children,
        "partners()":partners,
        "grandParents()":grandParents,
        "grandChildren()":grandChildren,
        "fristDegree()":firstDegree,
        "secondDegree()":secondDegree,
        "sisters()":sisters,
        "brothers()":brothers,
        "uncles()":uncles,
        "maternalUncles()":maternalUncles,
        "paternalUncles()":paternalUncles,
        "aunts()":aunts,
        "maternalAunts()":maternalAunts,
        "paternalAunts()":paternalAunts,
        "nephew()":nephew,
        "niece()":niece,
        "twins()":twins

    }    
def relationInterface(relation,id):
    f=interface.get(relation)
    return f(id)

  

##helper(auxiliary) functions for fetching relations
def getIndividualInfo(id):
        # try:
            ind=Individual.get_by_id(id)
            return [ind,Family.get(Family.id==ind.familyId)]
        #) except:
        #     print("Unexpected error:", sys.exc_info())
        #     return [ind,None]


def getIndividual(id):
    return Individual.get_by_id(id)

def getFamiliesForIndividual(id):
    return Family.select().where((Family.paternal==id) | (Family.maternal==id))

    

def getMaternalFamily(id,fam):
    if (fam!=None):
        return Family.get(Family.id==fam.maternalFamily.id)

    return None

def getPaternalFamily(id,fam):
    if (fam!=None):
        return Family.get(Family.id==fam.paternalFamily.id)
    
    return None

def getChildren(f):
    pass

def returnOnlyGender(list,g,dontPrint):  #list of individuals
    s=set()
    for c in list:
        if(c.gender==g and c!=dontPrint):##if c is NONE this would produce a bug
            s.add(c)
    return s



#below function are concering comapre function



def findReleventPolicies(res):
    policies=[]
    for p in Policy.select():
        if(isResourceIncluded(p,res)):
            policies.append(p)

    return policies
        




##helper(auxiliary) functions for fetching compare
def isResourceIncluded(policy,res):#right now we're not considerring conjunction and disjunction of resource
    arrayRes=json.loads(policy.resources)
    for elem  in arrayRes:
        if isinstance(elem,list):
            pass
        elif isinstance(elem,int):#need to b change to in the future
            if(res==elem):
                return True #in which case the resource is is relevent to the policy
    return False

def useShareRules(policies):
    shareWith=[]
    ruleSharePpl=list()
    for p in policies:
        ruleSharePpl=[]
        for r in p.rules:
            if(r.type=="share"):
                ppl=relationInterface(r.relation,p.author.id) ##add people in respect to the relation
                conditions=json.loads(r.condition)
                ##filtered=checkConditions(ppl,conditions)
                ##print(ppl,filtered)
                rd=RuleResults(ppl,conditions)
                ruleSharePpl.append(rd) ##check conditions
        ##after going through all rules..check any overlaps
        #print(ruleSharePpl)
        shareWith.append(checkOverlapp(ruleSharePpl))
    '''
    tasks
        finish checkOverlapp
        test it
        add never rules
        work on detecting conflicts
        generate the file
        ---here you can meet with Age
        write more relation functions
        annonymous sharing
        speed up the perfomance

     '''
    return shareWith

'''
{a,b,c,d,e,f}
{b,c,z}
(e,f,z)
{g,h} cond()  {g}

assume all common willf fail to pass

checkOverlapp -1
    {a,d}
    {z}
    {z}
    {g,h}
checkOverlapp -2
    {}
    {}
    {g,h}
checkOverlapp -3
   {}
   {}
   {g,h}

results={a,d,g,h}
'''


        

def checkOverlapp(results):
    allRemove=set()
    if(len(results)==0):
        return {}#empty set
    elif(len(results)==1):
        return results[0].ppl
    else:
        for i in range(1,len(results)):
            # print(results[0].ppl,results[i].ppl)
            #print("compare",results[0].ppl,results[i].ppl)
            common=(results[0].ppl).intersection(results[i].ppl)
        
            # for c in common:
            
            conditions=["and",results[0].conditions,results[i].conditions]
            union=results[0].ppl.union(results[i].ppl)
            filtered=checkConditions(union,conditions)


            removed=common.difference(filtered)## the ones are common and failed to be in filtered
            allRemove=allRemove.union(removed)
            removeInAll(results[1:],removed)
            #print("removed",removed,"result",results[i].ppl)
            


        results[0].ppl=results[0].ppl.difference(allRemove)
        others=checkOverlapp(results[1:])
        ret=(results[0].ppl).union(others)
        
        return ret

def removeInAll(results,rem):
    for r in results:
        r.ppl=r.ppl.difference(rem)


operators={##we might need consider operators with single operand
    "==":lambda a,b: a==b,
    ">" :lambda a,b: a>b,
    ">=":lambda a,b: a>=b,
    "<" :lambda a,b: a<b,
    "<=":lambda a,b: a<=b,
    "and":lambda a,b: a and b,
    "or":lambda a,b: a or b,
    "not":lambda a,b: not a
}

def propertyInterface(i,property):
    f=properties.get(property)
    return f(i)
    
def getGender(i):
    return i.gender
def getAge(i):
    return calculateAge(i.dob)

def calculateAge(birthDate): 
    today = date.today() 
    age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day)) 
    return age


properties={
    "gender":getGender,
    "age":getAge
}

def checkConditions(theSet,conditions):
     temp=set()
     if(conditions==[] or theSet==set()):
        return theSet
     for i in theSet:
         if not evaluateConditions(i,conditions):
             temp.add(i)  ##it doesnt pass the conditions
     
     
     return theSet.difference(temp)##remove the ones in both sets (the ones that have'nt passed) 
def evaluateConditions(i,conditions):
    if(isinstance(conditions,int)):
        return conditions
    elif(isinstance(conditions,str)):
        if(conditions.startswith(".")):
            return propertyInterface(i,conditions[1:])
        else:
            return conditions         
    elif conditions!=[]:
        op=operators.get(conditions[0])

        op1=evaluateConditions(i,conditions[1])
        op2=evaluateConditions(i,conditions[2])
        ## op (propertyvalue,comparedvalue)
        ret=op(op1,op2)
       
        return ret
        
    return True
'''
we got rules
    what we do when have and overlapp of individuals among bunch of relations. which one should we have higer presendence?
    note: that every rules has it own conditoins

    one approach could think of rules as gates for people to get in the shared people basket
    however the other approach might make sure when sharing with x, that x wouldn't violate any of the rest rules.

    the former is easy and quite straight forward to implement, however the latter would increase the complexity of the reading/parsing 
    the rules but it seem to be more natual approach or at least what would you expect.  


    other conflict that might occur is if individual x was allowed to get in by rules r1 and r2. Hoever r1 and r2 have different level of
    identity exposure. r1 is + and r2 is -, in this case (-) would have higher precendence. In other words rule setting anonymoised shared 
    would override an not anonmised rule... the implementation of would't be the much difficult 


algorithm (to get the people to share with)




-make list of people for all rules    xs   
    go through every rule in the policy
        call the relationInterface to get R
        go through R to check conditions
            if pass
                add to the rule list
            else
                nothing 
            

-check if intersection between each two lists
if x ^ y is non empty set
    then  if rule x conditions is r1, and rule y conditions  is r2
        therefore every element in  (x ^y) need to pass r1 and r2
        otherwise remove the element from list of shared people


flatten the list of people

[a,b,c] [c,d,b] [b,e]
[a,b][c,d][b,e]
[a][c,d][e]=[a,c,d,e]


'''



def compare(resource):
# algorithm used for compare function
# -fetch all relevent policies based on the queried resource
    policies=findReleventPolicies(resource)
# -inlcude all people in shares rules
    peopleShare=useShareRules(policies)
    print(peopleShare)
# -use never to discover conflicts
    ##conflicts=userNeverRules(policies)
# -show the results with any conflicts that exists

    




    



