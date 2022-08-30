import pickle
import numpy as np
import pandas as pd

class HealthInsurance:

    def __init__(self):
        self.annual_premium_scaler = pickle.load(open('../features/annual_premium_scaler.pkl', 'rb'))
        self.age_scaler = pickle.load(open('../features/age_scaler.pkl', 'rb'))
        self.policy_sales_scaler = pickle.load(open('../features/fe_policy_sales_channel.pkl', 'rb'))
        self.target_encode_gender = pickle.load(open('../features/target_encode_gender.pkl', 'rb'))
        self.target_encode_region_code = pickle.load(open('../features/target_encode_region_code.pkl', 'rb'))
        self.vintage_scaler = pickle.load(open('../features/vintage_scaler.pkl', 'rb'))


    def data_cleaning(self, df1):
        # drop duplicates id columns
        df1 = df1.loc[:, ~df1.columns.duplicated()].copy()

        return df1


    def feature_engineering(self, df2):
        ## 2.3 Feature Engineering
        # adjust format into vehicle age
        df2['vehicle_age'] = df2['vehicle_age'].apply(lambda x: 'over_2_years' if x == '> 2 Years'
                                                                else 'between_1_2_year' if x == '1-2 Year'
                                                                else 'below_1_year')


        # Convert categorical into numeric
        df2['vehicle_damage'] = df2['vehicle_damage'].apply(lambda x: 1 if x=='Yes' else 0)

        return df2


    def data_filtering(self, df3):
        ## 3.1 Filtragem das linhas
        # select only annual_premium bellow 65.000
        df3 = df3[df3['annual_premium'] < 65000]

        ## 3.2 Seleção das colunas

        # Select only who has driving license
        df3 = df3[df3['driving_license'] == 1]

        # drop driving license column
        df3.drop(columns='driving_license', inplace=True)

        return df3


    def data_preparation(self, df5):
        ## 5.1 Standardization

        # annual_premium
        df5['annual_premium'] = self.annual_premium_scaler.transform(df5[['annual_premium']].values)

        ## 5.2 Rescaling

        # Age
        df5['age'] = self.age_scaler.transform(df5[['age']].values)

        # Vintage
        df5['vintage'] = self.vintage_scaler.transform(df5[['vintage']].values)

        ## 5.3 Transformação
        ### 5.3.1 Encoding

        # gender - Target Encoding
        df5.loc[:, 'gender'] = df5['gender'].map(self.target_encode_gender)

        # region_code - Target Encoding
        df5.loc[:, 'region_code'] = df5['region_code'].map(self.target_encode_region_code)

        # vehicle_age - One Hot Encoding
        df5 = pd.get_dummies(df5, prefix='vehicle_age', columns=['vehicle_age'])

        # policy_sales_channel - Frequency Encoding
        df5.loc[:, 'policy_sales_channel'] = df5['policy_sales_channel'].map(self.policy_sales_scaler)

        # fillna
        df5 = df5.fillna(0)

        # select features from Metrics
        cols_selected = ['vintage', 'annual_premium', 'age', 'region_code',
                        'vehicle_damage', 'policy_sales_channel', 'previously_insured']


        return df5[cols_selected]
    

    def get_prediction(self, model, original_data, test_data):
        # results of train dataset
        pred = model.predict_proba( test_data )

        # join prediction into original data
        original_data['score'] = pred[:, 1].tolist()

        return original_data.to_json(orient='records', date_format='iso')

