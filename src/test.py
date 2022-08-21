# import matplotlib.pyplot as plt
# import numpy as np

# from sklearn import datasets
# from sklearn.linear_model import Lasso
# from sklearn.model_selection import GridSearchCV

# X, y = datasets.load_diabetes(return_X_y=True)
# X = X[:150]
# y = y[:150]

# lasso = Lasso(random_state=0, max_iter=10000)
# alphas = np.logspace(-4, -0.5, 30)

# tuned_parameters = {"alpha": alphas}
# n_folds = 5

# clf = GridSearchCV(lasso, tuned_parameters, cv=n_folds, refit=False, scoring="r2", verbose=1)
# clf.fit(X, y)
# #print(clf.cv_results_)
# print("Best score: %0.3f" % clf.best_score_)
# print("Best parameters set:")
# best_parameters = clf.get_params()
# print(best_parameters)
# scores = clf.cv_results_["mean_test_score"]
# scores_std = clf.cv_results_["std_test_score"]

# plt.figure().set_size_inches(8, 6)
# plt.semilogx(alphas, scores)

# std_error = scores_std / np.sqrt(n_folds)

# plt.semilogx(alphas, scores + std_error, "b--")
# plt.semilogx(alphas, scores - std_error, "b--")

# # alpha=0.2 controls the translucency of the fill color
# plt.fill_between(alphas, scores + std_error, scores - std_error, alpha=0.2)

# plt.ylabel("CV score +/- std error")
# plt.xlabel("alpha")
# plt.axhline(np.max(scores), linestyle="--", color=".5")
# plt.xlim([alphas[0], alphas[-1]])
# plt.show()
import os
print(os.environ.get("SLURM_CPUS_PER_TASK"))