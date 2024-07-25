import streamlit as st
import numpy as np
import scipy.stats as stats
import altair as alt
import pandas as pd


def calculate_sample_size(baseline_conv, mde, alpha, power):
  effect_size = abs(baseline_conv - (baseline_conv * (1 + mde)))
  required_n = np.ceil(
      (2 * (stats.norm.ppf(1 - alpha / 2) + stats.norm.ppf(power))**2 *
       baseline_conv * (1 - baseline_conv)) / (effect_size**2))
  return int(required_n)


def analyze_results(conversions_a, samples_a, conversions_b, samples_b):
  conv_rate_a = conversions_a / samples_a
  conv_rate_b = conversions_b / samples_b

  se_pooled = np.sqrt(conv_rate_a * (1 - conv_rate_a) / samples_a +
                      conv_rate_b * (1 - conv_rate_b) / samples_b)

  z_score = (conv_rate_b - conv_rate_a) / se_pooled
  p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))

  ci_factor = stats.norm.ppf(0.975)  # For 95% CI

  ci_a_lower = conv_rate_a - ci_factor * np.sqrt(conv_rate_a *
                                                 (1 - conv_rate_a) / samples_a)
  ci_a_upper = conv_rate_a + ci_factor * np.sqrt(conv_rate_a *
                                                 (1 - conv_rate_a) / samples_a)
  ci_b_lower = conv_rate_b - ci_factor * np.sqrt(conv_rate_b *
                                                 (1 - conv_rate_b) / samples_b)
  ci_b_upper = conv_rate_b + ci_factor * np.sqrt(conv_rate_b *
                                                 (1 - conv_rate_b) / samples_b)

  return conv_rate_a, conv_rate_b, p_value, ci_a_lower, ci_a_upper, ci_b_lower, ci_b_upper


st.set_page_config(page_title="AB Testing Tools",
                   page_icon="assets/microscope.png",
                   layout="centered",
                   initial_sidebar_state="auto",
                   menu_items=None)

st.title("🧪 AB Testing Tools")

tab1, tab2 = st.tabs(["Sample Size Calculator", "Results Analyzer"])

with tab1:
  st.header("Sample Size Calculator")
  baseline_conv = st.number_input("Baseline conversion rate",
                                  0.01,
                                  0.99,
                                  0.1,
                                  0.01,
                                  key="ssc_baseline")
  mde = st.number_input("Minimum Detectable Effect (relative)",
                        0.01,
                        1.0,
                        0.2,
                        0.01,
                        key="ssc_mde")
  alpha = st.number_input("Significance level (alpha)",
                          0.01,
                          0.1,
                          0.05,
                          0.01,
                          key="ssc_alpha")
  power = st.number_input("Statistical power",
                          0.7,
                          0.99,
                          0.8,
                          0.05,
                          key="ssc_power")

  if st.button("Calculate Sample Size"):
    sample_size = calculate_sample_size(baseline_conv, mde, alpha, power)
    st.success(f"Required sample size per group: **{sample_size}**")

with tab2:
  st.header("Results Analyzer")
  col1, col2 = st.columns(2)
  with col1:
    conversions_a = st.number_input("Conversions (A)", 0, 1000000, 100)
    samples_a = st.number_input("Total samples (A)", 1, 1000000, 1000)
  with col2:
    conversions_b = st.number_input("Conversions (B)", 0, 1000000, 120)
    samples_b = st.number_input("Total samples (B)", 1, 1000000, 1000)

  if st.button("Analyze Results"):
    conv_rate_a, conv_rate_b, p_value, ci_a_lower, ci_a_upper, ci_b_lower, ci_b_upper = analyze_results(
        conversions_a, samples_a, conversions_b, samples_b)

    st.write(f"P-value: **{p_value:.4f}**")

    results = pd.DataFrame(
        data={
            "Metric": ["Conversion Rate (A)", "Conversion Rate (B)"],
            "Value": [conv_rate_a, conv_rate_b],
            "95% Confidence Interval": [[ci_a_lower, ci_a_upper],
                                        [ci_b_lower, ci_b_upper]]
        })

    st.dataframe(
        results,
        hide_index=True,
    )

    data = pd.DataFrame({
        'Group': ['A', 'B'],
        'Conversion Rate': [conv_rate_a, conv_rate_b],
        'CI Lower': [ci_a_lower, ci_b_lower],
        'CI Upper': [ci_a_upper, ci_b_upper]
    })

    chart = alt.Chart(data).mark_bar().encode(x=alt.X(
        'Group', axis=alt.Axis(labelAngle=0)),
                                              y='Conversion Rate',
                                              color='Group')

    error_bars = alt.Chart(data).mark_errorbar(extent='ci').encode(
        x='Group', y='CI Lower', y2='CI Upper')

    final_chart = (chart + error_bars).properties(
        width=400,
        height=300,
        title='Conversion Rates Comparison with 95% Confidence Intervals')

    st.altair_chart(final_chart, use_container_width=True)
