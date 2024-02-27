## The Graham Number as the Foundation of a Profitable Investment Strategy

Defensive Investoren suchen nach Methoden, substanzstarke Unternehmen einfach, aber dennoch vielversprechend zu identifizieren, um langfristig positive Renditen zu erzielen. Die Graham-Zahl bietet in diesem Kontext eine Lösung, indem durch simple Berechnungen der wahre Wert eines Unternehmens ermittelt und mit dem Marktpreis abgeglichen wird. Eine Investition wird getätigt, wenn die Graham-Zahl mit ausreichendem Abstand über dem aktuellen Kurs liegt.
Das Ziel ist es, die Effektivität der Graham-Zahl im US-amerikanischen Aktienmarkt (2000-2023) zu überprüfen. Dazu wird die Forschungshypothese aufgestellt, dass die Auswahl unterbewerteter Unternehmen nach der Graham-Zahl im Vergleich zu einer breiten Investition im S\&P 500 Index über einen Zeitraum von drei Jahren zu höheren Renditen führt. Zur Überprüfung der Hypothese wurde eine Backtesting-Methode angewandt, bei der mit historischen Graham-Zahlen investiert wird und die erstellten Portfolios jeweils über drei Jahren evaluiert werden.
Die Evaluationsergebnisse verdeutlichen, dass die Graham-Zahl als alleiniges Bewertungskriterium und isolierte Entscheidungsgrundlage aufgrund niedriger, gegen Null tendierender, Renditen vermieden werden sollte. Lediglich eine geringe Anzahl von Unternehmen den anspruchsvollen Kriterien von Graham genügt, was zu einer stark begrenzten Diversifikation der Portfolios führt. Des Weiteren zeigt sich eine ausgeprägte Sensibilität der Portfolios gegenüber Marktereignissen, was zu erheblichen Renditeschwankungen führt.
Die Erkenntnis, dass die Simplizität der Graham-Zahl als isolierte Bewertungsmethode den Herausforderungen des Aktienmarktes nicht in vollem Umfang gerecht wird, legt nahe, dass künftige Forschungsbemühungen darauf ausgerichtet sein sollten, die Formel zu optimieren und sie mit zusätzlichen Kriterien zu kombinieren.


Schlagwörter/Schlüsselwörter: Graham-Number, Value-Investing, Backtesting

Defensive investors are looking for methods to identify companies with strong substance in a simple yet promising way in order to achieve positive long-term returns. The Graham number offers a solution in this context by using simple calculations to determine the true value of a company and comparing it with the market price. An investment is made when the Graham number is sufficiently above the current share price.
The aim is to test the effectiveness of the Graham number in the US stock market (2000-2023). The research hypothesis is that the selection of undervalued companies according to the Graham number leads to higher returns over a three-year period compared to a broad investment in the S\&P 500 Index. To test the hypothesis, a backtesting method was used in which investments are made using historical Graham numbers and the portfolios created are evaluated over three years.
The evaluation results make it clear that the Graham number should be avoided as the sole valuation criterion and isolated basis for decision-making due to low returns tending towards zero. Only a small number of companies meet Graham's demanding criteria, which leads to a very limited diversification of the portfolios. Furthermore, the portfolios are highly sensitive to market events, which leads to considerable fluctuations in returns.
The finding that the simplicity of the Graham number as an isolated valuation method does not fully meet the challenges of the stock market suggests that future research efforts should focus on optimizing the formula and combining it with additional criteria.

Keywords: Graham Number, Value Investing, Backtesting

### Usage:
**Creating Portfolios:**
* Navigate to the "portfolio_pipeline" folder.
* Run the "run.py" script. (This script executes "main.py," which utilizes the "create_portfolio" function defined in "util.py")
* Portfolios are generated using key metrics from FMP, closing prices from Alpha Vantage, and the S&P list from the GitHub repository (https://github.com/fja05680/sp500/tree/master).

**Performance Evaluation:**
*Execute the evaluation using "sliding_window_evaluation.py."
*Results for each quarter are saved separately (e.g., "final_results_2000-03-31.json"), containing portfolio returns for 1 quarter, 2 quarters, etc., up to 6 years.
*Merge these files (sample code is also in "sliding_window_evaluation.py").

**Visualization and Benchmark Comparison:**
*Use "benchmark_visualization.ipynb" to visualize the results and compare them with the benchmark.

### Main Results:
*portfolios_final.json (in directory portfolio_pipeline): contains portfolios for all quarters (tickers and margin of safety)
*final_returns.json (in evaluation folder): contains performance results
*evaluation_visualizations