import pandas as pd


data = {
    'Price Range': ['0-500', '501-1000', '1001-2000', '2001-5000', '5001-6000'],
    'Frequency (f)': [3, 12, 15, 15, 5],
    'xi': [250, 750, 1500, 3500, 5500],
    'xi*fi': [750, 9000, 22500, 52500, 27500],
    '(xi - x̄)': [-1995, -1495, -745, 1255, 3255],
    '(xi - x̄)^2': [3980025, 2235025, 555025, 1575025, 10595025],
    'fi*(xi - x̄)^2': [11940075, 26820300, 8325375, 23625375, 52975125]
}


df = pd.DataFrame(data)

total_frequency = 50
total_xi_fi = 112250
sample_mean = total_xi_fi / total_frequency


total_fi_xi_minus_mean_squared = df['fi*(xi - x̄)^2'].sum()
variance = total_fi_xi_minus_mean_squared / total_frequency
standard_deviation = variance ** 0.5

import scipy.stats as stats

z_score = stats.norm.ppf(0.975)  
margin_of_error = z_score * (standard_deviation / (total_frequency ** 0.5))
confidence_interval_lower = sample_mean - margin_of_error
confidence_interval_upper = sample_mean + margin_of_error

print("sample mean: ", sample_mean)
print("variance: ", variance)
print("standard deviation: ", standard_deviation)
print("confidence interval: ", (confidence_interval_lower, confidence_interval_upper))
