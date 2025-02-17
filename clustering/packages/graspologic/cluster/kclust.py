# Copyright (c) Microsoft Corporation and contributors.
# Licensed under the MIT License.

from typing import Optional, Union

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score

from ..types import List

from .base import BaseCluster


class KMeansCluster(BaseCluster):
    ari_: Optional[List[float]]

    """
    KMeans Cluster.

    It computes all possible models from one component to ``max_clusters``.
    When the true labels are known, the best model is given by the model with highest
    adjusted Rand index (ARI).
    Otherwise, the best model is given by the model with highest silhouette score.

    Parameters
    ----------
    max_clusters : int, default=2.
        The maximum number of clusters to consider. Must be ``>=2``.

    random_state : int, RandomState instance or None, optional (default=None)
        If int, ``random_state`` is the seed used by the random number generator;
        If RandomState instance, ``random_state`` is the random number generator;
        If None, the random number generator is the RandomState instance used
        by ``np.random``.

    Attributes
    ----------
    n_clusters_ : int
        Optimal number of clusters. If y is given, it is based on largest
        ARI. Otherwise, it is based on highest silhouette score.

    model_ : KMeans object
        Fitted KMeans object fitted with ``n_clusters_``.

    silhouette_ : list
        List of silhouette scores computed for all possible number
        of clusters given by ``range(2, max_clusters)``.

    ari_ : list
        Only computed when y is given. List of ARI values computed for
        all possible number of clusters given by ``range(2, max_clusters)``.
    """

    def __init__(
        self,
        max_clusters: int = 2,
        random_state: Optional[Union[int, np.random.RandomState]] = None,
    ):
        if isinstance(max_clusters, int):
            if max_clusters <= 1:
                msg = "n_components must be >= 2 or None."
                raise ValueError(msg)
            else:
                self.max_clusters = max_clusters
        else:
            msg = "max_clusters must be an integer, not {}.".format(type(max_clusters))
            raise TypeError(msg)
        self.random_state = random_state

    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> "KMeansCluster":
        """
        Fits kmeans model to the data.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            List of n_features-dimensional data points. Each row
            corresponds to a single data point.

        y : array-like, shape (n_samples,), optional (default=None)
            List of labels for `X` if available. Used to compute ARI scores.

        Returns
        -------
        self
        """
        # Deal with number of clusters
        if self.max_clusters > X.shape[0]:
            msg = "n_components must be >= n_samples, but got \
                n_components = {}, n_samples = {}".format(self.max_clusters, X.shape[0])
            raise ValueError(msg)
        else:
            max_clusters = self.max_clusters

        # Get parameters
        random_state = self.random_state

        # Compute all models
        models = []
        silhouettes = []
        aris = []
        for n in range(2, max_clusters + 1):
            model = KMeans(n_clusters=n, random_state=random_state)

            # Fit and compute values
            predictions = model.fit_predict(X)
            models.append(model)
            silhouettes.append(silhouette_score(X, predictions))
            if y is not None:
                aris.append(adjusted_rand_score(y, predictions))

        if y is not None:
            self.ari_ = aris
            self.silhouette_ = silhouettes
            self.n_clusters_ = np.argmax(aris) + 1
            self.model_ = models[np.argmax(aris)]
        else:
            self.ari_ = None
            self.silhouette_ = silhouettes
            self.n_clusters_ = np.argmax(silhouettes) + 1
            self.model_ = models[np.argmax(silhouettes)]

        return self
