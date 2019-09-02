from classes import *
from peewee  import *



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

def siblings(id):
    ind=Individual.get_by_id(id)
    fam=Family.get_by_id(ind.familyId)
    for i in fam.children:
        if(i.id!=id):
            print (i.firstName)


def parents(id):
    fam=getIndividualInfo(id)[1]
    mam=Individual.get_by_id(fam.maternal)
    dad=Individual.get_by_id(fam.paternal)
    print(mam.firstName+"----> MAM")
    print(dad.firstName+"----> DAD")

def  children(id):
     info=getIndividualInfo(id)
     fam=info[1]
     ind=info[0]
     families=[]
     for f in getFamiliesForIndividual(ind.id):
        for i in f.children:
                print (i.firstName)

def partners(id):
    ##updatee family schema to make maternal & paternal as foreign keys
    families=getFamiliesForIndividual(id)
    ind=getIndividual(id)
    for f in families:
        partner=None
        if(ind.gender=="M"):
            partner=getIndividual(f.maternal)
        else:
            partner=getIndividual(f.paternal)

        print(partner.firstName)


    
def grandParents(id):
    info=fam=getIndividualInfo(id)
    maternalFam=getMaternalFamily(id,info[1]) #Mom Family 
    paternalFam=getPaternalFamily(id,info[1]) #Dad Family


    print("maternal\n-------")
    print(getIndividual(maternalFam.maternal).firstName)
    print(getIndividual(maternalFam.paternal).firstName)
    print("paternal\n-------")
    print(getIndividual(paternalFam.maternal).firstName)
    print(getIndividual(paternalFam.paternal).firstName)
def firstDegree(id):
    parents(id)
    sibling(id)
    children(id)

def sisters():
    ind=Individual.get_by_id(id)
    fam=Family.get_by_id(ind.familyId)
    for i in fam.children:
        if(i.gender=="F"):
            print (i.firstName)
    
def brothers():
    ind=Individual.get_by_id(id)
    fam=Family.get_by_id(ind.familyId)
    for i in fam.children:
        if(i.gender=="M"):
            print (i.firstName)
def secondDegree():
    pass
def uncles(id):
    info=fam=getIndividualInfo(id)
    maternalFam=getMaternalFamily(id,info[1]) #Mom Family 
    paternalFam=getPaternalFamily(id,info[1]) #Dad Family

    dontPrint=info[0].familyId.paternal

    printOnlyGender(maternalFam.children,"M",dontPrint)
    printOnlyGender(paternalFam.children,"M",dontPrint)
def maternalUncles(id):
    info=fam=getIndividualInfo(id)
    maternalFam=getMaternalFamily(id,info[1]) #Mom Family 
    printOnlyGender(maternalFam.children,"M",None)

def paternalUncles(id):
    info=fam=getIndividualInfo(id)
    paternalFam=getPaternalFamily(id,info[1]) #DAD Family 
    dontPrint=info[0].familyId.paternal
    printOnlyGender(paternalFam.children,"M",dontPrint)

def aunts(id):
    info=fam=getIndividualInfo(id)
    maternalFam=getMaternalFamily(id,info[1]) #Mom Family 
    paternalFam=getPaternalFamily(id,info[1]) #Dad Family
    
    dontPrint=info[0].familyId.maternal

    printOnlyGender(maternalFam.children,"F",dontPrint)
    printOnlyGender(paternalFam.children,"F",dontPrint)
def maternalAunts(id):
    info=fam=getIndividualInfo(id)
    maternalFam=getMaternalFamily(id,info[1]) #Mom Family  

    dontPrint=info[0].familyId.maternal
    printOnlyGender(maternalFam.children,"F",dontPrint)
def paternalAunts(id):
    info=fam=getIndividualInfo(id)
    paternalFam=getPaternalFamily(id,info[1]) #Mom Family  
    printOnlyGender(paternalFam.children,"F",None)

  

##helper(auxiliary) functions
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
  

def printOnlyGender(list,g,dontPrint):  #list of individuals
    for c in list:
        if(c.gender==g and c!=dontPrint):##if see is NONE this would produce a bug
            print(c.firstName)

           
def compare(resources):
# algorithm used for compare function
# -fetch all relevent policies based on the queried resources
    policies=findReleventPolcies(Resource)
# -inlcude all people in shares rules
    peopleShare=useShareRules(policies)
# -use never to discover conflicts
    conflicts=userNeverRules(policies)
# -show the results with any conflicts that exists
    