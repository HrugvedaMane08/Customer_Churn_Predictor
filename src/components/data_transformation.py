import os
import sys
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.base import BaseEstimator, TransformerMixin
from dataclasses import dataclass

from src.logger import logging
from src.exception import CustomException
from src.utils import save_object

class FeatureEngineeringTransformer(BaseEstimator, TransformerMixin):
    """
    Custom transformer class to engineer features inside the Scikit-learn pipeline.
    Inheriting from BaseEstimator and TransformerMixin makes it compatible with Pipeline.
    """
    def __init__(self):
        logging.info("Initialized FeatureEngineeringTransformer")

    def fit(self, X, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Creates new features:
        1. ChargesRatio: TotalCharges / (tenure + 1)
        2. TenureGroup: Binned tenure groups (New, Medium, Long, Loyal)
        """
        try:
            X_copy = X.copy()
            logging.info("Engineering feature: ChargesRatio")
            # Calculate average charges per month of tenure; add 1 to tenure to prevent division by zero
            X_copy['ChargesRatio'] = X_copy['TotalCharges'] / (X_copy['tenure'] + 1)

            logging.info("Engineering feature: TenureGroup")
            # Bin tenure into qualitative groups
            def get_tenure_group(t):
                if t <= 12:
                    return 'New'
                elif t <= 36:
                    return 'Medium'
                elif t <= 60:
                    return 'Long'
                else:
                    return 'Loyal'
            X_copy['TenureGroup'] = X_copy['tenure'].apply(get_tenure_group)
            
            return X_copy
        except Exception as e:
            raise CustomException(e, sys)

@dataclass
class DataTransformationConfig:
    preprocessor_obj_file_path: str = os.path.join("artifacts", "preprocessor.pkl")

class DataTransformation:
    def __init__(self):
        self.data_transformation_config = DataTransformationConfig()

    def get_data_transformer_object(self) -> Pipeline:
        """
        Creates and returns the complete preprocessing pipeline including
        custom feature engineering, scaling, imputation, and encoding.
        """
        try:
            # 1. Feature Columns definition
            # Numerical columns include the engineered column 'ChargesRatio'
            numerical_columns = ["tenure", "MonthlyCharges", "TotalCharges", "ChargesRatio"]
            # Categorical columns include the engineered column 'TenureGroup'
            categorical_columns = ["gender", "Contract", "TenureGroup"]

            # 2. Pipeline for numerical features
            num_pipeline = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler())
                ]
            )

            # 3. Pipeline for categorical features
            cat_pipeline = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("one_hot_encoder", OneHotEncoder(handle_unknown="ignore")),
                    ("scaler", StandardScaler(with_mean=False))
                ]
            )

            logging.info(f"Pre-engineered & standard categorical columns: {categorical_columns}")
            logging.info(f"Pre-engineered & standard numerical columns: {numerical_columns}")

            # 4. Combine numerical and categorical pipelines using ColumnTransformer
            preprocessor = ColumnTransformer(
                transformers=[
                    ("num_pipeline", num_pipeline, numerical_columns),
                    ("cat_pipeline", cat_pipeline, categorical_columns)
                ]
            )

            # 5. Full sequential pipeline containing Feature Engineering first, then preprocessing
            full_pipeline = Pipeline(
                steps=[
                    ("feature_engineering", FeatureEngineeringTransformer()),
                    ("preprocessing", preprocessor)
                ]
            )

            return full_pipeline
        except Exception as e:
            raise CustomException(e, sys)

    def initiate_data_transformation(self, train_path: str, test_path: str) -> tuple:
        """
        Loads train and test splits, cleans columns, applies the preprocessing pipeline,
        and saves the preprocessor object.
        """
        try:
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)

            logging.info("Successfully loaded train and test datasets for transformation")

            # Clean and prepare initial dataframes
            logging.info("Converting TotalCharges to float and mapping Churn label to binary integers")
            for df in [train_df, test_df]:
                df['TotalCharges'] = pd.to_numeric(df['TotalCharges'].astype(str).str.strip(), errors='coerce')
                df['TotalCharges'] = df['TotalCharges'].fillna(0.0)
                df['Churn'] = df['Churn'].map({'Yes': 1, 'No': 0})

            logging.info("Obtaining full preprocessing pipeline object")
            preprocessing_pipeline = self.get_data_transformer_object()

            target_column_name = "Churn"

            # Separate features and target label
            input_feature_train_df = train_df.drop(columns=[target_column_name], axis=1)
            target_feature_train_df = train_df[target_column_name]

            input_feature_test_df = test_df.drop(columns=[target_column_name], axis=1)
            target_feature_test_df = test_df[target_column_name]

            logging.info("Applying full pipeline (Feature Engineering + Scaling + Encoding) on train and test features")
            input_feature_train_arr = preprocessing_pipeline.fit_transform(input_feature_train_df)
            input_feature_test_arr = preprocessing_pipeline.transform(input_feature_test_df)

            # Combine transformed features with targets back into numpy arrays for training
            train_arr = np.c_[input_feature_train_arr, np.array(target_feature_train_df)]
            test_arr = np.c_[input_feature_test_arr, np.array(target_feature_test_df)]

            logging.info("Serializing and saving preprocessor pipeline object")
            save_object(
                file_path=self.data_transformation_config.preprocessor_obj_file_path,
                obj=preprocessing_pipeline
            )

            return (
                train_arr,
                test_arr,
                self.data_transformation_config.preprocessor_obj_file_path
            )
        except Exception as e:
            raise CustomException(e, sys)
