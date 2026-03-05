from scipy.stats import ks_2samp

def detect_drift(reference_data, live_data, threshold=0.05):
    statistic, p_value = ks_2samp(reference_data, live_data)
    return p_value < threshold
