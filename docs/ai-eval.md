| case | source | model | checks passed | rejection reason | clarity 1-5 |
| --- | --- | --- | --- | --- | --- |
| increase | gemini | gemini-3.6-flash | yes | - | |
| increase_pettitt2014 | gemini | gemini-3.6-flash | yes | - | |
| decrease | gemini | gemini-3.6-flash | yes | - | |
| decrease_pettitt2014 | gemini | gemini-3.6-flash | yes | - | |
| no_trend | gemini | gemini-3.6-flash | yes | - | |
| no_trend_pettitt2014 | gemini | gemini-3.6-flash | yes | - | |

### increase (gemini)

**what_it_means:** We applied the Mann-Kendall test to 25 annual totals. The test returned p = 0.008, which is below the 0.05 threshold, showing that the upward trend is unlikely to come from random year-to-year variation alone. The size of this rise is about 8.4% per decade, compared with a mean annual total of 3724 mm.

**what_it_does_not_mean:** This result says nothing about why rainfall behaves this way, as the statistical tests describe a pattern in the numbers rather than its cause. It says nothing about future years because it covers 2001-2025 only. A result without statistical significance is not evidence that rainfall remained uniform, as a brief record can miss a real but small change. The value is a satellite estimate averaged over a box of about 33 km around Douala, not a reading at one point in the city.

**limitations:**
- The satellites providing the data changed in 2014 (TRMM to GPM), and NASA warns that such a change can create artifacts that look like a trend in multi-year studies.
- NASA reports lower IMERG accuracy near coasts, and Douala sits on the Wouri estuary.
- With only 25 annual values, the tests have low statistical power, so a real but small change can go undetected.
- The figures are satellite estimates averaged over a box of about 33 km around Douala, not a reading at one point.

### increase_pettitt2014 (gemini)

**what_it_means:** We tested 25 annual totals using the Mann-Kendall test. The resulting p = 0.008 is below the 0.05 cutoff, meaning the upward trend is unlikely to be pure random chance. The rise is about 8.4% per decade compared with an average annual total of 3724 mm. In addition, the Pettitt test found a sudden step jump starting in 2014. However, this jump matches the 2014 satellite transition from TRMM to GPM, so it may be a data artifact rather than a real shift.

**what_it_does_not_mean:** This result does not explain why rainfall behaves this way, as the statistical tests show a pattern in numbers without giving a cause. It says nothing about future years because it covers 2001-2025 only. A non-significant result is not proof that rainfall stayed constant, because a short record can miss a small real shift. The value is a satellite average for a box of about 33 km around Douala, not a reading at one point in the city.

**limitations:**
- The underlying satellites changed in 2014 from TRMM to GPM, and NASA warns that this switch can produce artifacts that resemble a trend over many years.
- NASA reports lower IMERG accuracy near coastal areas, and Douala sits on the Wouri estuary.
- Because there are only 25 annual values, the statistical tests have low power, so a small real shift could go undetected.
- The numbers are satellite estimates averaged across a box of about 33 km around Douala rather than a reading at one point.

### decrease (gemini)

**what_it_means:** We ran the Mann-Kendall test on 25 annual totals. The result gave p = 0.012, which is below the 0.05 threshold, showing that the downward tendency is unlikely to be just year-to-year chance. The size of the fall is around 7.4% per decade, relative to an average annual total of 3724 mm.

**what_it_does_not_mean:** This result says nothing about why rainfall behaves this way, because the tests describe a pattern in numbers, not its cause. It says nothing about future years, as it covers 2001-2025 only. A result that lacks statistical significance is not evidence that rainfall stayed the same, because a short record can miss a real but small change. The value is a satellite estimate averaged over a box of about 33 km around Douala, not a reading at one point in the city.

**limitations:**
- The satellites behind the data changed in 2014 (TRMM to GPM), and NASA warns that such a change can create artifacts that look like a trend in multi-year studies.
- NASA reports lower IMERG accuracy near coastlines, and Douala sits on the Wouri estuary.
- With only 25 annual values, the statistical tests have low power, so a real but small change can go undetected.
- The numbers are satellite estimates averaged over a box of about 33 km around Douala, rather than readings at a single point.

### decrease_pettitt2014 (gemini)

**what_it_means:** We tested 25 annual totals using the Mann-Kendall test. The result gave p = 0.012, which is below the 0.05 threshold. This means the downward tendency is unlikely to come from random year-to-year chance. The total fall is about 7.4% per decade compared to the mean annual total of 3724 mm. The Pettitt test identified a sudden step change starting in 2014. This change matches the 2014 satellite transition from TRMM to GPM, so it might be a data artifact instead of a real shift.

**what_it_does_not_mean:** This result does not explain why rainfall behaves this way because the tests only describe numerical patterns, not causes. It says nothing about future years and covers 2001-2025 only. A result without statistical significance does not mean rainfall stayed constant, since a short record can miss a small real shift. This value is a satellite estimate averaged over a box of about 33 km around Douala, not a reading at one point in the city.

**limitations:**
- The satellite sensors changed in 2014 from TRMM to GPM, and NASA warns this switch can create artificial trends in long studies.
- NASA notes lower IMERG accuracy near coastlines, and Douala is located on the Wouri estuary.
- Because there are only 25 annual values, the statistical tests have low power and might miss a small real shift.
- These numbers represent satellite estimates averaged over a box of about 33 km around Douala, rather than a reading at one point.

### no_trend (gemini)

**what_it_means:** We tested 25 annual totals using the Mann-Kendall test. The result gave p = 0.168, which is not below the 0.05 threshold, so the record cannot separate a steady upward or downward pattern from ordinary year-to-year variation. The primary estimate is 3.9% per decade, relative to an average annual total of 3724 mm. The 95% confidence interval spans from a negative to a positive value, meaning the real change could go either way.

**what_it_does_not_mean:** This result says nothing about why rainfall behaves this way, because the statistical tests describe patterns in the numbers rather than their causes. It says nothing about future years, covering 2001-2025 only. A result that is not statistically significant is not evidence that rainfall stayed the same, because a short record can miss a small real change. The value is a satellite estimate averaged over a box of about 33 km around Douala, not a reading at one point in the city.

**limitations:**
- The satellites behind the data changed in 2014 from TRMM to GPM, and NASA warns that such a change can create artificial patterns that look like a trend in multi-year studies.
- NASA reports lower IMERG accuracy near coasts, and Douala sits on the Wouri estuary.
- With only 25 annual values, the tests have low statistical power, so a real but small change can go undetected.
- The numbers are satellite estimates averaged over a box of about 33 km around Douala, not a reading at one point.

### no_trend_pettitt2014 (gemini)

**what_it_means:** We applied the Mann-Kendall test to 25 annual rainfall totals. The test yielded p = 0.168, which is not below the 0.05 cutoff. This means the dataset cannot distinguish a real upward or downward tendency from typical year-to-year variation. The main estimate is 3.9% per decade relative to an average annual total of 3724 mm. The 95% interval ranges from a negative to a positive value, meaning the true shift could be positive or negative. A Pettitt test showed a sharp step starting in 2014. This shift matches the 2014 satellite transition (TRMM to GPM), so it might be a data artifact rather than a real shift.

**what_it_does_not_mean:** This finding says nothing about why rainfall behaves this way, as the statistical tests show numerical patterns rather than causes. It says nothing about future years because it covers 2001-2025 only. An outcome that lacks statistical significance is not evidence that rainfall remained constant, since a short dataset might overlook a real but small shift. Finally, the figure represents a satellite estimate averaged across a box of about 33 km around Douala, rather than a reading at one point in the city.

**limitations:**
- The satellite instruments behind the record shifted in 2014 (TRMM to GPM), and NASA cautions that this swap can produce false patterns that look like a long-term tendency.
- NASA indicates lower IMERG accuracy in coastal zones, and Douala lies along the Wouri estuary.
- Because there are only 25 annual values, the statistical tests have low detection power, which means a small actual pattern could be missed.
- These figures reflect satellite estimates averaged across a box of about 33 km around Douala, not a reading at one point.

