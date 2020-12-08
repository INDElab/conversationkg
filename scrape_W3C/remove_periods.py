
#%%

import json
from collections import Counter



from conversationkg import load_example_data_as_raw_JSON

ml = "public-credentials"

d_raw = load_example_data_as_raw_JSON(ml)



#%%


convos = [(subj_str, mail_ls) for period, subj_d in d_raw.items() for subj_str, mail_ls in subj_d.items()]


with open(f"{ml}/all.json", "w") as handle:
    json.dump(convos, handle)