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
    maternalFam=getMaternalFamily(id)
    paternalFam=getPaternalFamily(id)
    gfmaternal=(list(maternalFam.select()))
   ## gmmaternal=getPaternalFamily(id)
    # print(maternalFam)
    # if((maternalFam==None) or (paternalFam==None)):
    #     print ("the passed individual does not have any grand parents")
    # else:
    print(gfmaternal)
    # print(getIndividual(maternalFam.maternal).firstName)
    # print(getIndividual(paternalFam.maternal).firstName)
    # print(getIndividual(paternalFam.maternal).firstName)
def firstDegree():
    parents()
    sibling()
    children()

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
def uncles():
    pass
def maternalUncles():
    pass
def paternalUncles():
    pass
def maternalAunts():
    pass
def paternalAunts():
    pass

  

##helper(auxiliary) functions
def getIndividualInfo(id):
        # try:
            ind=Individual.get_by_id(id)
            return [ind,Family.get_by_id(ind.familyId)]
        # except:
        #     print("Unexpected error:", sys.exc_info())
        #     return [ind,None]


def getIndividual(id):
    return Individual.get_by_id(id)

def getFamiliesForIndividual(id):
    return Family.select().where((Family.paternal==id) | (Family.maternal==id))

def getMaternalFamily(id):
    fam=getIndividualInfo(id)[1]

    if (fam!=None):
        return fam.maternalInFamilies 

    return None

def getPaternalFamily(id):
    fam=getIndividualInfo(id)[1]
    print()
    if (fam!=None):
        return fam.paternalInFamilies 
    
    return None
  


def compare(resources):
# algorithm used for compare function
# -fetch all relevent policies based on the queried resources
    policies=findReleventPolcies(Resource)
# -inlcude all people in shares rules
    peopleShare=useShareRules(policies)
# -use never to discover conflicts
    conflicts=userNeverRules(policies)
# -show the results with any conflicts that exists
    