import re, csv, os
from django.core.management.base import LabelCommand
from ballot.models import Ballot
from issues.models import Electorate

gsc_districts = {
    #'H&S': 'gsc-hs',
    'Medicine': 'gsc-med',
    'Engineer': 'gsc-eng',
    'EarthSci': 'gsc-earthsci',
    'Law': 'gsc-law',
    'Education': 'gsc-edu',
    'GSB': 'gsc-gsb',
}
assu_pops = {
    '1- Undergraduate Student': ['undergrad'],
    '2 - Coterm': ['undergrad','graduate'],
    '3 - Graduate Student': ['graduate'],
}
class_years = {
    '5 - Fifth year or more Senior': 'undergrad-5plus',
    '4 - Senior Class Affiliation': 'undergrad-5plus',
    '3 - Junior Class Affiliation': 'undergrad-4',
    '2 - Sophomore Class Affiliation': 'undergrad-3',
    '1 - Freshman Class Affiliation': 'undergrad-2',
}

def get_ballot(sunetid):
    b, created = Ballot.get_or_create_by_sunetid(sunetid)
    return b

def elec(slug):
    if slug is None: return None
    return Electorate.objects.get(slug=slug)

class Command(LabelCommand):
    def handle_label(self, label, **options):
        output = []
        
        students_path = os.path.join(label, 'students.csv')
        students = csv.DictReader(open(students_path,'rU'))
    
        for row in students:
            sunetid = row['SUNetID']
            b = get_ballot(sunetid)
            groups = map(str.strip, row['Class Level'].split(','))
            for g in groups:
                if g in assu_pops:
                    b.assu_populations = map(elec, assu_pops[g])
                if g in class_years:
                    b.undergrad_class_year = elec(class_years[g])
            print "%s\t%s" % (sunetid, b)
            b.save()
