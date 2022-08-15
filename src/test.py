from pathlib import Path
from time_utils import get_date_from_string

import pandas as pd
import plotly.express as px
# # Import Data
# df = pd.read_csv('https://raw.githubusercontent.com/selva86/datasets/master/mnist_012.csv')
#
# # Prepare X and Y
# Y = df.loc[:, '0']
# X = df.drop(['0'], axis=1)
#
# print(df.shape)
# print(df.head())
#
# # PCA
# pca = PCA()
# df_pca = pca.fit_transform(X=X)
#
# # Store as dataframe and print
# df_pca = pd.DataFrame(df_pca)
# print(df_pca.shape)  #> (3147, 784)
# print(df_pca.round(2).head())
#
# df_pca_loadings = pd.DataFrame(pca.components_)
# print(df_pca_loadings.head())
#
#
# X_mean = X - X.mean()
# print(X_mean.head())

path_str = "/Users/igor/Documents/Masterarbeit/logfile_analysis/resources/export/db/trainingdata_2022-08-15.db"
path = Path(path_str)
print(get_date_from_string(path.stem))
