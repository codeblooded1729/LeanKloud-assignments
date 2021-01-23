import pandas as pd
import argparse

def find_topper(subject):
    column=df[subject]
    Id=column.idxmax()
    return df['Name'][Id]

def top3():
    df['Total']=sum(df[sub] for sub in df.columns if sub!='Name')
    topper_list=[]
    for i in range(3):
        currmax=0
        for j in range(len(df)):
            if j in topper_list:
                continue
            if df['Total'][j]>df['Total'][currmax]:
                currmax=j
        topper_list+=[currmax]
    return [df['Name'][ind] for ind in topper_list]

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--csv',help='name of csv file')
    args=parser.parse_args()
    if not args.csv:
        parser.error('Provide name of csv file')
    file_name=args.csv


    df=pd.read_csv(file_name)
    for subject in df.columns:
        if subject=='Name':
            continue
        print(f'Topper in {subject} is',find_topper(subject))

    t3=top3()
    print('Best students in the class are',' '.join(t3))
