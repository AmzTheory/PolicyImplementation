from peewee import *
import sys
from playhouse.migrate import *

#implementation needed
# add people
# add resources/conditions/relations
#Download dateset that would be usefull for testing
# add policies(which include rules)
#-> when policies created a policy language file need to be generated (used for reasoning later)
# evaluate policies for a list of resource (Compare function)


db=SqliteDatabase('database.db')

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




class Children(BaseModel):
     familyId=ForeignKeyField(Family,backref="Fam")
     childID=ForeignKeyField(Individual,backref="Children")


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



#surplus the need for now as resutl of introducing JSON
class Condition(BaseModel):
       id=AutoField()
       name=TextField()

class RelationToRule(BaseModel):
       ruleId=ForeignKeyField(Rule,backref="relations")
       relationId=ForeignKeyField(Relation,backref="rules")


class RuleDetails(BaseModel):
       ruleId = ForeignKeyField(Rule, backref="conditions")
       condition=TextField() #json

class Instead(BaseModel):
       ruleId=ForeignKeyField(Rule,backref="relations")
       relationId=ForeignKeyField(Relation,backref="rules")


class SharedPeople():
    def __init__(self,individual,anon):
        self.individual=individual
        self.anon=anon


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

      



        
