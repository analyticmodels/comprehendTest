import pandas as pd
from pprint import pprint
from comprehend_detect import ComprehendDetect
import boto3
from botocore.exceptions import ClientError

def detect_pi(df):
    df_pi = pd.DataFrame()
    n_rows = 0
    for row in df.itertuples(index=False, name="row_tuple"):
        n_rows += 1
        for col in df.columns:
            pii_list = comp_detect.detect_pii(getattr(row, col), 'en')
            for j in range(len(pii_list)):
                pii_list[j]['field'] = col
                pii_list[j]['row'] = n_rows
            df_pi = pd.concat([df_pi,pd.DataFrame(pii_list)]) 
    df_pi.to_csv("data/detectedPI.csv",index=False)
    return df_pi

def detect_names(df):
    df_names = pd.DataFrame()
    n_rows = 0
    for row in df.itertuples(index=False):
        n_rows += 1
        for col in df.columns:
            name_list = comp_detect.detect_entities(getattr(row, col), 'en')
            for name in name_list:
                if name['Type'] == "PERSON":
                    name['Type'] = "NAME"
                    name['field'] = col
                    name['row'] = n_rows
                    df_names = pd.concat([df_names,pd.DataFrame([name])])
    df_names.to_csv("data/detectedNames.csv",index=False)
    return df_names

def redact_text(text, pi_dict):
    for pi in pi_dict:
        start = pi_dict['BeginOffset']
        end = pi_dict['EndOffset']
        entity_type = pi_dict['Type']
        len_redact = end-start
        
        # Replace with redaction marker
        replace_str = text[start:end]
        redaction_text = f"[{entity_type}]"
        try:
            redacted_str = text.replace(replace_str,redaction_text)
        except:
            pass
        #
        return redacted_str
    
def redact_df(df,df_redacts):
    df_redacted = df.copy()
    for _, redact in df_redacts.iterrows():
        df_redacted.loc[redact['row']-1,redact['field']] = redact_text(df[redact['field']][redact['row']-1],redact.to_dict())
    return df_redacted

# if __name__ == "__main__":
#     #data
#     df = pd.read_csv("data/pii_test_faker.csv",delimiter=",")
#     df.dropna()
#     #instantiate wrapper class
#     comp_detect = ComprehendDetect(boto3.client("comprehend","us-east-1"))

#     #return PII detections
#     df_pi = detect_pi(df)
#     #redact PII detections
#     df_redacted = redact_df(df,df_pi)

#     #rescan for excluded names
#     df_names = detect_names(df_redacted)
#     #redact names
#     df_redacted = redact_df(df_redacted,df_names)

#     df_redacted.to_csv("./data/fakerRedacted.csv",index=False)
#     # df_compare = pd.DataFrame()
#     # for j in range(len(df)):
#     #     df_compare = pd.concat([df_compare,df[j:j+1]])
#     #     df_compare = pd.concat([df_compare,df_redacted[j:j+1]])
#     # df_compare.to_csv("data/compare.csv")
#     # pprint(df_compare)