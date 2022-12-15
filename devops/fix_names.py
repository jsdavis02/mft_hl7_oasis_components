import sys
sys.path.append('..')
from devops import util_functions

paths = ['/regulatory_prd/PACLetters', '/regulatory_prd/ReferralLetters',  '/regulatory_prd/BHLetters', '/regulatory_prd/AMBCC', '/fs_groups/Grants/Programs/Well Woman HealthCheck Program/Billing/ADHS BILLING BUNDLE/TO_ADHS']
for p in paths:
    util_functions.clean_file_names(p)
