from classes import *
from peewee  import *
from types   import *
from functools import singledispatch
import json
import inspect
from datetime import date


##in the files we find the implementation for the analyse and generate policies





#the below functions to insert family, indivudal, policy and resource
##but it worth to note those were not used over coding implementation and mostly
##the data was inserted manually into the database


##  you can find the data type of the atrributed in classes.py

def addIndividual(firstName,lastName,dob,dod,gender,familyID):
    individual=Individual(firstName=firstName,lastName=lastName,dob=dob,dod=dod,gender=gender,familyId=familyID)
    individual.save()
    return individual.id

def initFamily(paternal,maternal):
    family=Family(paternalFamily=paternal,maternalFamily=maternal,root=0)
    family.save()
    return family.id

def initRootFamily(paternal,maternal):
    family=Family(paternal=paternal,maternal=maternal,root=1)
    family.save()
    return family.id

def addResource(name):
    res=Resource(name=name)
    Resource.save()



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



'''
the following function are used to lookup the list of people with relative relation (function name)

functions who have *args, is length  eith have length 1 or 2
in case of 1  ->they  would include just [id] 
in case of 2  -> the  would inlcude the [id,name]  name is would be used when certain person  within relation (specific person) 

function with just id  -> id is used to find relatives in respect to the user with passed id
    usedthey dont offer the selecting certain person (those can be extended to allow selecting specific person)
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
    
    if(fam.paternal!=None):
        return {mam, dad}
    ##in case the individual doesn't have parents(root family)
    return {}

def mam(id):
    fam=getIndividualInfo(id)[1]
    mam=Individual.get_by_id(fam.maternal)
    if(fam.maternal!=None):
        return {mam}
    return {}#in case the individual doesn't have mam
def dad(id):
    fam=getIndividualInfo(id)[1]
    dad=Individual.get_by_id(fam.paternal)
    if(fam.paternal != None):
        return {dad}
    
    #in case the individual doesn't have dad(root family)
    return {}

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
    
    ##maternal niece  (extenstion)
    ##paternal niece  (extenstion)
    
    return nieces
def twins(id):
    pass



#    The following is mappiing of relation to functions

relInterface={
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


'''
This function would returnt he list of people individals based on arguments passed

relation-> relation name  
arguments -> the user id and in some case a name might be as well passed
'''
def relationInterface(relation,arguments):
    f=relInterface.get(relation)

    if(len(arguments)==1):
        return f(arguments[0])# f(id)
    elif(len(arguments)==2):
        return f(arguments[0],arguments[1])  #f(id,name)

  

#(auxiliary) functions  used in relation functions



##return list of two elements with individual instance and individual's Family instance 
## id -> the individual id
def getIndividualInfo(id):
        # try:
            ind=Individual.get_by_id(id)
            return [ind,Family.get(Family.id==ind.familyId)]
        #) except:
        #     print("Unexpected error:", sys.exc_info())
        #     return [ind,None]


#return individial instance based on the id passed
def getIndividual(id):
    return Individual.get_by_id(id)


#return family instances where an individual is a parent 
def getFamiliesForIndividual(id):
    return Family.select().where((Family.paternal==id) | (Family.maternal==id))



##return the family instance of individal's MAM
def getMaternalFamily(id,fam):
    if (fam.maternalFamily!=None):
        return Family.get(Family.id==fam.maternalFamily.id)

    return None
##return the Famil instanace of individal's DAD
def getPaternalFamily(id,fam):
    if (fam.paternalFamily!=None):
        return Family.get(Family.id==fam.paternalFamily.id)
    
    return None


# ##return the list 
# def returnOnlyGender(list,g,dontPrint):  #list of individuals
#     s=set()
#     for c in list:
#         if(c.gender==g and c!=dontPrint):##if c is NONE this would produce a bug
#             s.add(c)
#     return s


## return a set of people based on arguments passed  , the function is called most of the relatoin functions
## select-> type of peewee.select that can be iterted through
## args ->is the same args passed to relation functions, hence the lenth could be 1 0r 2
## f    -> contains the function the would in every individual with select.. It could be check on gender or id  (to get better idea ,look at iterator calls)
def iterator(select, args, f):
    
    returnSet = set()
    for i in select:
         if(len(args) == 2):
            if(i.firstName == args[1] and f(i)):   ## when looking for a specific person
                returnSet.add(i)
         elif(f(i)):
             returnSet.add(i)
    return returnSet



#below function are concering analyse function


#return the list of policies that are attached to resource id passed
#res-> resource id
def findReleventPolicies(res):
    policies=[]
    for p in Policy.select():
        if(isResourceIncluded(p,res)):
            policies.append(p)

    return policies
        




## this function would check if a resource is in a policy's resource
## policy -> its the policy that we are looking into its resources  (not Policy resource is in json and need to be converted to an python array)
## res ->  id of the resource where search if its exist in the policy resources  
def isResourceIncluded(policy,res):
    arrayRes=json.loads(policy.resources)
    for elem  in arrayRes:
        if isinstance(elem,list):
            pass
        elif isinstance(elem,int):
            if(res==elem):
                return True #in which case the resource is is relevent to the policy
    return False


##this function would take all share rules and evaluate then by return the a list of people
## author ->policy author's id 
## rules  -> the list of rules
def evaluateShareRules(author,rules):
    share=[]
    for r in rules:
        rd=evaluateRule(author,r,False)
        share.append(rd) ##check conditions
    ##after going through all rules..check any overlaps
    ret= checkOverlap(share)##pop an element which the first cause it the only one
    return ret

##this function would take all never rules and evaluate then by return the a list of people
## author ->policy author's id 
## rules  -> the list of rules
def evaluateNeverRules(author, rules):
    never=set()
    instead=set()
    for r in rules:
        filtered=evaluateRule(author,r,True)
        if(r.instead!=[]):
            insteadRules = convertJsonToRules(r.instead)
            for f in filtered:
                instead.update(evaluateShareRules(f.id, insteadRules))
            
        never.update(filtered)   
    return [never,instead]

##this function would evaluate people a single rules yeild considering the rules relation and conditoins
##return an instance
## author ->policy author's id 
## rule  -> rules to be evaluated
def evaluateRule(author,rule,filter):
     arguments = getRelationArgs(author, rule)  # [relation,args]
     return getPplRule(rule,arguments[0],arguments[1],filter)


## The following is an axuilariy function  for evaluate rule that call  relation function and then filter them based on conditions
def getPplRule(rule,relation,args,filter):
    ppl=relationInterface(relation,args) ##add people to respect to the relation
    conditions=json.loads(str(rule.condition))

    if(filter):
        return checkConditions(ppl,conditions)

    return ShareComponents(ppl, conditions)

##convert rules in json to rule instances  (used for instead part)
def convertJsonToRules(js):
    if(js==""):
        return ""
    rules=list()
    rulesConverted=json.loads(js)
    for r in rulesConverted:
        cond = r.get("conditions") if r.get("conditions")!=None else []
        rules.append(Rule(condition=cond, relation=r.get("relation"),type="share"))

    return rules

##this function used in evaluate rule that return list of two element the define a relation with arguments
## this return of this function would get passed to the relationinterface

def getRelationArgs(pAuthorId,rule):
    funArgs = [pAuthorId]
    relation=rule.relation
    bracketInd=rule.relation.index("(")
    args=rule.relation[bracketInd+1:-1]
    if(args!=""):##in case name is included , add the name to the args
        splitArgs=args.split(",")
        funArgs.extend(splitArgs)
        relation = rule.relation[:bracketInd]+"()"
    return [relation,funArgs]


##get all rules of certain typen (share/never)
##policy -> instance of the policy
##type   -> the type wanted
def getRules(policy,type):
    rules=set()
    for r in policy.rules:
        if(r.type==type):
            rules.add(r)
    return rules   

# def removeElementsFromList(ls,rls):
#     for r in rls:
#         for l in ls:
#             if(l.id==r.id):
#                 ls.remove(r)
#                 break


                    
##This function is used within evaluateShare rules, and its purpose is to make sure there is no overlap  between all share rules

def checkOverlap(results):
    allRemove=set()
    if(len(results)==0):
        return set()#empty set
    elif(len(results)==1):
        return results[0].ppl
    else:
        for i in range(1,len(results)):
            
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
        others=checkOverlap(results[1:])
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
        ## op (propertyvalue,comparedvalue)e
        ret=op(op1,op2)
       
        return ret
        
    return True



def evaluatePolicies(policies):
    results=[]
    share,never,instead,performNever=set(),set(),set(),[]
    for p in policies:
        share=evaluateShareRules(p.author.id,getRules(p,"share"))
        performNever = evaluateNeverRules(p.author.id, getRules(p, "never")) #[never,instead]
        never=performNever[0]
        instead=performNever[1]
        share.update(instead)

        results.append(RuleResults(p,share,never))
    return results
        



def detectConflict(results):
    res=AnalyseResults()
    for i in results:
         s=i.share
         shareWith=i.share
         for j in results:
             inters=s.intersection(j.never)
             if(not (inters==set())):     ##or i.getAuthor().id==j.getAuthor().id)):
                ##at least one conflict found
                 addConflictToResults(res,inters,i.policy,j.policy)
             shareWith = shareWith.difference(inters)
         res.addPpl(shareWith)##bit naive tho I think
    return res


    
def addConflictToResults(res,ppl,p1,p2):
         res.addConflict(p1,p2,ppl)

def analyse(resource):
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

def generateShareRules(rules):
    ret=""
    for r in rules:
        if(r.type=="share"):
            ret+="\t"+generateRule(r)+"\n"
    return ret

def generateNeverRules(rules):
    ret=""
    for r in rules:
        if(r.type=="never"):
            insteadRules=convertJsonToRules(r.instead)
            if(insteadRules==""):
                ret+="\t"+generateRule(r)+":\n"
            else:
                ret += "\t"+generateRule(r)+":["+generateInsteadRules(insteadRules)+"]\n"
    return ret

def generateInsteadRules(insteadRules):
    ret=""
    for r in insteadRules:
       cond=convertToExp(r.condition)
       return r.relation+":"+cond
    return ret
    

def generatePolicy(id):
    p=Policy.get_by_id(id)

    #construct share and never block
    rules="\nshare\n"+generateShareRules(p.rules)+"never\n"+generateNeverRules(p.rules)

    policy="author "+str(p.author.id)
    policy+="\nresources "+p.resources+"{"+rules+"}"
    return policy

def generatePolicies(ps):
    for p in ps:
        print(generatePolicy(p))


    




    



