import pandas as pd
import dill as pickle
import numpy as np
import sys


def pred_file_to_df(file_name):
    header = ['RecordID', 'Age',
              'GCS_Max', 'GCS_Mean', 'GCS_LastDataPoint',
              'HCO3_Min', 'HCO3_Max', 'HCO3_Mean', 'HCO3_LastDataPoint',
              'Urine_Sum',
              'BUN_Min', 'BUN_Max', 'BUN_Mean', 'BUN_LastDataPoint',
              'SysABP_Min', 'SysABP_Mean', 'SysABP_LastDataPoint',
              'NISysABP_Min',
              'FiO2_PaO2_Ratio',
              'WBC_Mean', 'WBC_LastDataPoint',
              'Temp_Mean', 'Temp_LastDataPoint',
              'Glucose_Max',
              'Na_Mean', 'Na_Max',
              'Lactate_LastDataPoint']

    data_list = preprocess_file(file_name)

    assert len(header) == len(data_list)

    df = pd.DataFrame(columns=header)
    df.loc[0] = data_list
    df = df.drop('RecordID', axis=1)

    return df



def preprocess_file(file_name):
    best_vars_values = {'GCS': 15, 'HCO3': 26.5, 'Urine': 2800, 'BUN': 15,
                        'FiO2': 0.21, 'PaO2': 80, 'WBC': 7.75, 'Temp': 37,
                        'Glucose': 95, 'Na': 140, 'NISysABP': 115, 'SysABP': 115,
                        'Lactate': 0.75}  # best predictor variables with their normal values

    df = pd.read_csv(file_name)
    RecordID_DF = df[df['Parameter'] == 'RecordID']
    Age_DF = df[df['Parameter'] == 'Age']

    var_df_list = clean_extract(df, best_vars_values)
    var_df_list.append(RecordID_DF)
    var_df_list.append(Age_DF)  # appended to the end as better time comp than prepend

    to_be_aggregated_df = pd.concat(var_df_list)
    aggregated_data = aggregate(to_be_aggregated_df)

    return aggregated_data


def aggregate(df):
    # Patient Info
    RecordID = str(int(df.loc[df['Parameter'] == 'RecordID', 'Value']))  # this is just for identification
    Age = int(df.loc[df['Parameter'] == 'Age', 'Value'])  # this is used for prediction

    # Predictor Variables Aggregated
    GCS = get_variable_row_values(df, 'GCS')
    GCS_Max = GCS.max()
    GCS_Mean = GCS.mean()
    GCS_LastDataPoint = get_last_data_point(GCS)
    # GCS_Slope = slope(df)

    HCO3 = get_variable_row_values(df, 'HCO3')
    HCO3_Min = HCO3.min()
    HCO3_Max = HCO3.max()
    HCO3_Mean = HCO3.mean()
    HCO3_LastDataPoint = get_last_data_point(HCO3)

    Urine_Sum = get_variable_row_values(df, 'Urine').sum()

    BUN = get_variable_row_values(df, 'BUN')
    BUN_Min = BUN.min()
    BUN_Max = BUN.max()
    BUN_Mean = BUN.mean()
    BUN_LastDataPoint = get_last_data_point(BUN)

    SysABP = get_variable_row_values(df, 'SysABP')
    SysABP_Min = SysABP.min()
    SysABP_Mean = SysABP.mean()
    SysABP_LastDataPoint = get_last_data_point(SysABP)

    NISysABP_Min = get_variable_row_values(df, 'NISysABP').min()

    WBC = get_variable_row_values(df, 'WBC')
    WBC_Mean = WBC.mean()
    WBC_LastDataPoint = get_last_data_point(WBC)

    Temp = get_variable_row_values(df, 'Temp')
    Temp_Mean = Temp.mean()
    Temp_LastDataPoint = get_last_data_point(Temp)

    Glucose_Max = get_variable_row_values(df, 'Glucose').max()

    Na = get_variable_row_values(df, 'Na')
    Na_Mean = Na.mean()
    Na_Max = Na.max()

    Lactate_LastDataPoint = get_last_data_point(get_variable_row_values(df, 'Lactate'))

    FiO2 = get_variable_row_values(df, 'FiO2')
    FiO2_Mean = FiO2.mean()

    PaO2 = get_variable_row_values(df, 'PaO2')
    PaO2_Mean = PaO2.mean()

    FiO2_PaO2_ratio = FiO2_Mean / PaO2_Mean

    data = [RecordID, Age,
            GCS_Max, GCS_Mean, GCS_LastDataPoint,
            HCO3_Min, HCO3_Max, HCO3_Mean, HCO3_LastDataPoint,
            Urine_Sum,
            BUN_Min, BUN_Max, BUN_Mean, BUN_LastDataPoint,
            SysABP_Min, SysABP_Mean, SysABP_LastDataPoint,
            NISysABP_Min,
            FiO2_PaO2_ratio,
            WBC_Mean, WBC_LastDataPoint,
            Temp_Mean, Temp_LastDataPoint,
            Glucose_Max,
            Na_Mean, Na_Max,
            Lactate_LastDataPoint]

    return data


def clean_extract(df, best_vars_values):
    best_vars = best_vars_values.keys()  # best predictor variables
    # df = pd.read_csv(file_name)

    # extract
    var_df_list = []  # dictionary of predictor variable dataframes
    for var in best_vars:
        var_df = df[df['Parameter'] == var]  # this may add empty df if empty
        var_df_list.append(var_df)  # add variable dataframe to dictionary

    # clean
    i = 0
    for var in best_vars:
        var_df = var_df_list[i]
        if var_df.empty:
            row = [['00:00', var, best_vars_values[var]]]
            temp_df = pd.DataFrame(row, columns=['Time', 'Parameter', 'Value'])
            var_df_list[i] = (temp_df)
        i += 1

    return var_df_list


def get_last_data_point(df):
    return df.iloc[-1]


def get_variable_row_values(df, variable_name):
    return df.loc[df['Parameter'] == variable_name, 'Value']


if __name__ == "__main__":
    print(sys.argv[1])
    file_path = sys.argv[1]
    pred_df = pred_file_to_df(file_path)
    pred_df_values_np_array = np.array(pred_df.values)
    print(pred_df_values_np_array)
    print(pred_df.values)

    model = pickle.load(open('ml_models/randomForestModel.sav', 'rb'))

    print("Prediction:", model.predict(pred_df))
    print("Prediction Prop. Score:", model.predict_proba(pred_df))

    predict_fn = lambda x: model.predict_proba(x).astype(float)
    explainer = pickle.load(open('ml_models/limeExplainerModel.sav', 'rb'))
    explanation = explainer.explain_instance(pred_df.values[-1], predict_fn, num_features=10)
    explanation.save_to_file('views/explanation.html')