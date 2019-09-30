from peewee import *
from playhouse.migrate import *



db=SqliteDatabase('database.db')

##ORM used is peewee .. Simple orm with sqlite database   
##checkout http://docs.peewee-orm.com/en/latest/ for the docs


class BaseModel(Model):
    class Meta:
        database=db


class Family(BaseModel):
     id=AutoField()
     maternalFamily=ForeignKeyField('self',null=True,backref="maternalFam")
     paternalFamily=ForeignKeyField('self',null=True,backref="paternalFam")
     root=BooleanField()
     paternal=DeferredForeignKey('Individual',null=True,backref="paternalInFamilies")
     maternal=DeferredForeignKey('Individual',null=True,backref="maternalInFamilies")

class Individual(BaseModel):
     id = AutoField()
     firstName = CharField()
     lastName = CharField()
     dob = DateField(null=False)
     dod = DateField(null=True)
     gender = CharField()
     familyId = ForeignKeyField(Family, backref='children')



class Relationship(BaseModel):
      id=AutoField()
      ind1=ForeignKeyField(Individual,backref="current")# relation from 
      ind2=ForeignKeyField(Individual, backref="relatives") # relation to
      tag=TextField()

class Policy(BaseModel):
      id=AutoField()
      author=ForeignKeyField(Individual,backref="policies")
      resources=TextField()#json

class Resource(BaseModel):
      id=AutoField()
      name=CharField()



class Relation(BaseModel):
       id=AutoField()
       name=TextField()



class Rule(BaseModel):
      id=AutoField()
      type=CharField()
      anon=BooleanField(null=True)
      instead=TextField()#json
      condition=TextField() #json
      relation=TextField() #json
      policyId=ForeignKeyField(Policy,backref="rules")


def performMigration():
       field = ForeignKeyField(Individual, field=Individual.id, null=True)
       paternal=ForeignKeyField(Individual,null=True,backref="paternalInFamilies")
       maternal=ForeignKeyField(Individual,null=True,backref="maternalInFamilies")

       relation=TextField()

       migrator=SqliteMigrator(db)
       migrate(
              migrator.drop_column('rule',"relation_id"),
              migrator.add_column('rule',"relation",relation)
       )





# class SharedPeople():
#     def __init__(self,individual,anon):
#         self.individual=individual
#         self.anon=anon


## instance of this below class represent 
class ShareComponents:
    def printAll(listOfResult):
           for i in listOfResult:
              for n in i.ppl:
                     print(n)
    def __init__(self,ppl,conditions):
        self.ppl=ppl
        self.conditions=conditions

class RuleResults():
       def __init__(self,policy,share,never):
              self.policy=policy
              self.share=share
              self.never=never
       def printInstance(self):
              print(self.policy.id,self.share,self.never)

       def getAuthor(self):
              return self.policy


class Conflict():
       def __init__(self,p1,p2,inds):
              self.p1=p1
              self.p2=p2
              self.inds=inds

       def getIndividialNames(self):
              ret=set()
              for i in self.inds:
                     ret.add(i.firstName)
              return str(ret)
       def printInstance(self):
              return "Between "+self.p1.author.firstName+" and "+self.p2.author.firstName+" regarding "+self.getIndividialNames()+"  (check policies "+str(self.p1.id)+" and "+str(self.p2.id)+" to find out why)"
class AnalyseResults():
       def __init__(self):
              self.ppl=set()
              self.conflicts=[]
       
       def addPpl(self,ppl):
              self.ppl=self.ppl.union(ppl)

       def addConflict(self,p1,p2,ind):
              self.conflicts.append(Conflict(p1,p2,ind))
       
       def printInstance(self):
              ret="Share with the following:"
              
              for p in self.ppl:
                     ret+="\n"+p.firstName

              ret+=("\nConflicts found:"+str(len(self.conflicts)))
              
              for c in self.conflicts:
                     ret+="\n"+c.printInstance()
              return ret



##used to access DB to create tables
class Access:
       def connect():
              db.connect()
              print ("open")

       def close():
              db.close()

       def createTables():
              try:
                     Access.connect()
                     db.create_tables([Rule])
                     db.close()
                     print ("close1")
              except:
                     print("Unexpected error:", sys.exc_info())
                     db.close()
                     print ("close2")

      



        
