from clustering.ensembles.utils import get_ensemble_distance_matrix
from clustering.methods import DeltaSpectralClustering


def scc(
    ensemble,
    k: int,
    delta: float = 1.0,
    ensemble_is_coassoc_matrix: bool = False,
    **kwargs,
):
    """
    Performs consensus clustering using a spectral-based approach.

    This function uses :obj:`clustering.methods.DeltaSpectralClustering` to
    perform consensus clustering on the provided ensemble.

    Args:
        ensemble: array-like, shape (n_partitions, n_samples)
            It contains partitions generated by clustering algorithms. Each
            value indicates the cluster a sample belongs to.
        k: the number of clusters.
        delta: the width of the Gaussian kernel applied to the distance matrix
            derived from the ensemble (coassociation matrix).
        ensemble_is_coassoc_matrix: it indicates if the ``ensemble`` parameter
            represents the ensemble (n_partitions, n_samples) or the distance
            matrix derived from it (n_samples, n_samples).
        **kwargs: other arguments passed to
            :obj:`clustering.methods.DeltaSpectralClustering`

    Returns: array-like, shape (n_samples,)
        A partition of the samples in the ensemble using a spectral-based
        approach.
    """

    if ensemble_is_coassoc_matrix:
        data = ensemble
    else:
        data = get_ensemble_distance_matrix(ensemble)

    return DeltaSpectralClustering(
        n_clusters=k,
        delta=delta,
        **kwargs,
    ).fit_predict(data)
