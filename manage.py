from classes import *
from peewee  import *
from types   import *
from functools import singledispatch
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


'''
    specific relations


    children(name)
    children([name])
    siblings(name)
    siblings([name])
    uncle(name)
    uncles([name])  /same for paternal and maternals
'''
def siblings(*args):##id is and individual not just number... so adjust how all relation function is written to speed up the process
    id=args[0]
    ind=Individual.get_by_id(id)
    fam=Family.get_by_id(ind.familyId)

    prop=(lambda a:a.id!=id)

    siblings=iterator(fam.children,args,prop)
    for fd in getFamiliesForIndividual(fam.paternal):
        siblings.update(iterator(fd.children,args,prop))

    for md in getFamiliesForIndividual(fam.maternal):
        siblings.update(iterator(md.children,args,prop))
    

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

def  children(*args):
     children=set()
     id=args[0]
     info=getIndividualInfo(id)
     fam=info[1]
     ind=info[0]
     families=[]
     for f in getFamiliesForIndividual(ind.id):
        children.update(iterator(f.children, args, (lambda a: True)))
     return children
def sons(*args):
    children=set()
    id=args[0]
    info=getIndividualInfo(id)
    fam=info[1]
    ind=info[0]
    families=[]
    for f in getFamiliesForIndividual(ind.id):
        children.update(iterator(f.children, args, (lambda a: a.gender=="M")))
    return children
def daughters(*args):
     children=set()
     id=args[0]
     info=getIndividualInfo(id)
     fam=info[1]
     ind=info[0]
     families=[]
     for f in getFamiliesForIndividual(ind.id):
         children.update(iterator(f.children, args, (lambda a: a.gender=="F")))
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

    if(maternalFam!=None):
        grandParents.add(getIndividual(maternalFam.maternal))
        grandParents.add(getIndividual(maternalFam.paternal))
    if(paternalFam!=None):
        grandParents.add(getIndividual(paternalFam.maternal))
        grandParents.add(getIndividual(paternalFam.paternal))

    return grandParents
    

def grandChildren(*args):
    id=args[0]
    grandChildren=set()
    for c in getFamiliesForIndividual(id):
        #for every child we need to print his children
        for c in c.children:
            for f in getFamiliesForIndividual(c):
                grandChildren.update(iterator(f.children, args, (lambda a: True)))               
    return grandChildren

def firstDegree(id):
    all=set()  ##think about threading here  (wont work cause SQL is )
    all.update(parents(id))
    all.update(siblings(id))
    all.update(children(id))

    return all

def sisters(*args):
    id = args[0]

    sisters=set()
    ind=Individual.get_by_id(id)
    fam=Family.get_by_id(ind.familyId)
    
    ##property/conditions
    prop=(lambda a:a.id!=id and a.gender=="F")

    ##full siblings
    sisters=iterator(fam.children,args,prop)
    
    ##paternal siblings
    for fd in getFamiliesForIndividual(fam.paternal):
        sisters.update(iterator(fd.children,args,prop))

    ##maternal siblings
    for md in getFamiliesForIndividual(fam.maternal):
        sisters.update(iterator(md.children,args,prop))

    return sisters
    
def brothers(*args):
    id = args[0]
    brothers=set()
    ind=Individual.get_by_id(id)
    fam=Family.get_by_id(ind.familyId)
   ##property/conditions
    prop=(lambda a:a.id!=id and a.gender=="M")

    ##full siblings
    brothers=iterator(fam.children,args,prop)
    
    
    ##paternal siblings
    for fd in getFamiliesForIndividual(fam.paternal):
        brothers.update(iterator(fd.children,args,prop))

    ##maternal siblings
    for md in getFamiliesForIndividual(fam.maternal):
        brothers.update(iterator(md.children,args,prop))

    return brothers

def paternalSiblings(*args):
     id=args[0]
     pSiblings = set()
     ind=Individual.get_by_id(id)
     fam=Family.get_by_id(ind.familyId)

     prop=(lambda a:a.id!=id and a.familyId!=ind.familyId)

     for fd in getFamiliesForIndividual(fam.paternal):
            pSiblings.update(iterator(fd.children, args, prop))
     return pSiblings
def maternalSiblings(*args):
    id=args[0]
    mSiblings=set()
    ind=Individual.get_by_id(id)
    fam=Family.get_by_id(ind.familyId)
    prop=(lambda a:a.id!=id and a.familyId!=ind.familyId)

    ##maternal siblings
    for md in getFamiliesForIndividual(fam.maternal):
        mSiblings.update(iterator(md.children, args, prop))

    return mSiblings


def halfSiblings(*args):
    hfSiblings=set()
    hfSiblings=paternalSiblings(args)
    hfSiblings.update(maternalSiblings(args))
    return hfSiblings

def fullSiblings(*args):
    id=args[0]
    fSiblings=set()
    ind=Individual.get_by_id(id)
    fam=Family.get_by_id(ind.familyId)
    prop=(lambda a:a.id!=id)

    ##full siblings
    fSiblings=iterator(fam.children,args,prop)
    return fSiblings

def secondDegree(id):
    all=set()
    all.update(uncles(id))
    all.update(aunts(id))
    all.update(grandParents(id))
    all.update(grandChildren(id))
    return all
def uncles(*args):
    id=args[0]
    uncles=set()
    info=fam=getIndividualInfo(id)
    maternalFam=getMaternalFamily(id,info[1]) #Mom Family 
    paternalFam=getPaternalFamily(id,info[1]) #Dad Family
    prop=lambda a:a.id!=info[1].paternal.id and a.gender=="M"

    uncles.update(iterator(paternalFam.children, args, prop))
    uncles.update(iterator(maternalFam.children,args,prop))
    return uncles
def maternalUncles(*args): 
    id=args[0]
    maternalUncles=set()
    info=fam=getIndividualInfo(id)
    maternalFam=getMaternalFamily(id,info[1]) #Mom Family 
    prop=lambda a:a.gender=="M"
    maternalUncles.update(iterator(maternalFam.children,args,prop))
    return maternalUncles

def paternalUncles(*args):
    id=args[0]
    paternalUncles=set()
    info=fam=getIndividualInfo(id)
    paternalFam=getPaternalFamily(id,info[1]) #Mom Family 
    prop=lambda a:a.id!=info[1].paternal.id and a.gender=="M"
    paternalUncles.update(iterator(paternalFam.children,args,prop))
    return paternalUncles

def aunts(*args):
    id=args[0]
    aunts=set()
    info=fam=getIndividualInfo(id)
    maternalFam=getMaternalFamily(id,info[1]) #Mom Family 
    paternalFam=getPaternalFamily(id,info[1]) #Dad Family
    prop=lambda a:a.id!=info[1].paternal.id and a.gender=="F"

    aunts.update(iterator(paternalFam.children, args, prop))
    aunts.update(iterator(maternalFam.children,args,prop))
    return aunts
def maternalAunts(*args):
    id=args[0]
    maternalAunts=set()
    info=fam=getIndividualInfo(id)
    maternalFam=getMaternalFamily(id,info[1]) #Mom Family 
    prop=lambda a:a.id!=info[1].maternal.id and a.gender=="F"

    maternalAunts.update(iterator(maternalFam.children,args,prop))
    return maternalAunts
def paternalAunts(*args):
    id=args[0]
    paternalAunts=set()
    info=fam=getIndividualInfo(id)
    paternalFam=getPaternalFamily(id,info[1]) #Mom Family 
    prop=lambda a:a.gender=="F"

    paternalAunts.update(iterator(paternalFam.children,args,prop))
    return paternalAunts


#will be implemented at later time
def nephews(*args):
    id= args[0]
    nephews=set()
    ind=Individual.get_by_id(id)
    fam=Family.get_by_id(ind.familyId)

    
    ##Full nephews
    for c in fam.children:
        if(c.id!=id):
            nephews.update(sons(c.id))

    ##maternal nephews  
    ##paternal newpews
    return nephews
def nieces(*args):
    id = args[0]
    nieces = set()
    ind = Individual.get_by_id(id)
    fam = Family.get_by_id(ind.familyId)

    ##Full niece
    for c in fam.children:
        if(c.id != id):
            nieces.update(daughters(c.id))
    ##maternal niece
    ##paternal niece
    
    return nieces
def twins(id):
    pass

interface={
        "siblings()":siblings,
        "maternalSiblings()":maternalSiblings,
        "paternalSiblings()":paternalSiblings,
        "parents()":parents,
        "mother()":mam,
        "father()":dad,
        "children()":children,
        "sons()":sons,
        "daughters()":daughters,
        "partners()":partners,
        "grandParents()":grandParents,
        "grandChildren()":grandChildren,
        "firstDegree()":firstDegree,
        "secondDegree()":secondDegree,
        "sisters()":sisters,
        "brothers()":brothers,
        "uncles()":uncles,
        "maternalUncles()":maternalUncles,
        "paternalUncles()":paternalUncles,
        "aunts()":aunts,
        "maternalAunts()":maternalAunts,
        "paternalAunts()":paternalAunts,
        "nephews()":nephews,
        "nieces()":nieces,
        "twins()":twins

    }    
def relationInterface(relation,arguments):
    f=interface.get(relation)

    if(len(arguments)==1):
        return f(arguments[0])# f(id)
    elif(len(arguments)==2):
        return f(arguments[0],arguments[1])  #f(id,name)

  

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
    if (fam.maternalFamily!=None):
        return Family.get(Family.id==fam.maternalFamily.id)

    return None

def getPaternalFamily(id,fam):
    if (fam.paternalFamily!=None):
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


def iterator(select, args, f):
    returnSet = set()
    for i in select:
         if(len(args) == 2):
            if(i.firstName == args[1] and f(i)):
                returnSet.add(i)  # what about if the author included his name
         elif(f(i)):
             returnSet.add(i)
    return returnSet



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

def useShareRules(policy):
    share=[]
    for r in policy.rules:
        if(r.type=="share"):
            #relation
            funArgs=[policy.author.id]
            relation=r.relation
            bracketInd=r.relation.index("(")
            args=r.relation[bracketInd+1:-1]
            if(args!=""):
                splitArgs=args.split(",")
                funArgs.extend(splitArgs)
                relation=r.relation[:bracketInd]+"()"
                print(relation,args,splitArgs)
            ppl=relationInterface(relation,funArgs) ##add people in respect to the relation
            conditions=json.loads(r.condition)
            ##filtered=checkConditions(ppl,conditions)
            ##print(ppl,filtered)
            rd=ShareComponents(ppl,conditions)
            share.append(rd) ##check conditions
    ##after going through all rules..check any overlaps
    ret= checkOverlapp(share)##pop an element which the first cause it the only one
    return ret

def userNeverRules(policy):
    never=set()
    for r in policy.rules:
        if(r.type=="never"):
            ppl=relationInterface(r.relation,[policy.author.id]) ##add people in respect to the relation
            conditions=json.loads(r.condition)
            filtered=checkConditions(ppl,conditions)
            never=never.union(filtered)   
    return never
                
def removeElementsFromList(ls,rls):
    for r in rls:
        for l in ls:
            if(l.id==r.id):
                ls.remove(r)
                break


                    

def checkOverlapp(results):
    allRemove=set()
    if(len(results)==0):
        return set()#empty set
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
     if(theSet==set()):
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


def evaluatePolicies(policies):
    results=[]
    for p in policies:
        share=useShareRules(p)
        never=userNeverRules(p)
        results.append(RuleResults(p,share,never))
    return results
        



def detectConflict(results):
    res=CompareResults()
    
    for i in results:
         agg=set()
         s=i.share
         for j in results:
             inters=s.intersection(j.never)
             if(not (inters==set() or i.getAuthor().id==j.getAuthor().id)):
                ##at least one conflict found
                 addConflictToResults(res,inters,i.policy,j.policy)
             s=dif=s.difference(j.never)
         res.addPpl(s)##bit naive tho I think
    return res


    
def addConflictToResults(res,ppl,p1,p2):
    
    for p in ppl:
         res.addConflict(p1,p2,p)

def compare(resource):
# algorithm used for compare function
# -fetch all relevent policies based on the queried resource
    policies=findReleventPolicies(resource)
## get share and nevers for every policy
    resultsBeforeConflicts=evaluatePolicies(policies)
## detect conflict and form the fnal output  
    resultsFinal=detectConflict(resultsBeforeConflicts)

##print output
    print(resultsFinal.printInstance())


##this block would include function used for generating policy files

def convertToExp(conditions):
    if(conditions==[]):
        return ""
    elif(isinstance(conditions,int)):
        return str(conditions)
    elif(isinstance(conditions,str)):
        if(conditions.startswith(".")):
            return conditions[1:]
        else:
            return conditions         
    elif conditions!=[]:
        return convertToExp(conditions[1])+" "+conditions[0]+" "+convertToExp(conditions[2])



def generateRule(r):
    cond=convertToExp(json.loads(r.condition))
    return r.relation+":"+cond

def generateRules(p,typeRule):
    ret=""
    
    for r in p.rules:
        if r.type==typeRule: 
            ret+="\t"+generateRule(r)+"\n"
    return ret
    

def generatePolicy(id):
    p=Policy.get_by_id(id)

    #construct share and never block
    rules="\nshare\n"+generateRules(p,"share")+"never\n"+generateRules(p,"never")

    policy="author "+str(p.id)
    policy+="\nresources "+p.resources+"{"+rules+"}"
    return policy

def generatePolicies(ps):
    for p in ps:
        print(generatePolicy(p))


    




    



