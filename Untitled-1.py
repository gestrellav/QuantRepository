"""
Ejemplo APT multifactor (estadístico via PCA) aplicado a acciones US + ETFs de bonos US.
Requisitos: pip install yfinance pandas numpy scipy statsmodels scikit-learn cvxpy
"""

import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.decomposition import PCA
import statsmodels.api as sm
import cvxpy as cp
from datetime import datetime

# -----------------------
# 1) Definiciones
# -----------------------
tickers_equity = ["AAPL", "MSFT", "GOOGL", "AMZN", "JPM"]   # ejemplo: acciones US
tickers_bonds = ["TLT", "IEF", "BND"]                     # ETFs proxy para bonos US
tickers = tickers_equity + tickers_bonds
factor_k = 3   # número de factores PCA (ajusta según prefieras)
start = "2019-01-01"
end = datetime.today().strftime("%Y-%m-%d")
freq = "1mo"   # usamos retornos mensuales en este ejemplo

# -----------------------
# 2) Descargar precios y calcular retornos
# -----------------------
data = yf.download(tickers, start=start, end=end, interval=freq, progress=False)["Adj Close"]
prices = data.dropna(axis=0, how="any")   # quitar filas con NA
rets = prices.pct_change().dropna()        # retornos simples
print(f"Shape retornos: {rets.shape}")

# -----------------------
# 3) Construir factores por PCA (serie de factores de mercado estadísticos)
#    Otra opción sería usar factores económicos (FF, yields, inflación...) si están disponibles.
# -----------------------
# Standardizar (mean=0) antes de PCA
X = (rets - rets.mean()) / rets.std(ddof=0)
pca = PCA(n_components=factor_k)
F_scores = pca.fit_transform(X)    # matríz (T x k) de factores
F = pd.DataFrame(F_scores, index=rets.index, columns=[f"F{i+1}" for i in range(factor_k)])

# convertemos factores a rendimientos mensuales (ya lo son por construcción)
# opcional: normalizar factores por su desviación (facilita interpretación)
F = (F - F.mean()) / F.std(ddof=0)

# -----------------------
# 4) Estimar betas APT (regresión de retornos de cada activo sobre los factores)
# -----------------------
betas = pd.DataFrame(index=tickers, columns=F.columns)
residuals = pd.DataFrame(index=rets.index, columns=tickers)

for asset in tickers:
    y = rets[asset] - 0.0  # si quieres usar exceso sobre RF, resta RF aquí
    X_reg = sm.add_constant(F)   # incluye intercept (alpha)
    model = sm.OLS(y, X_reg).fit(cov_type='HAC', cov_kwds={'maxlags':1})  # robust cov
    betas.loc[asset, :] = model.params[F.columns].values
    residuals[asset] = model.resid

betas = betas.astype(float)
print("\nBetas (primeras filas):")
print(betas.head())

# -----------------------
# 5) Estimar primas de factores (factor risk premia)
#    Simple: promedio histórico de retorno de cada factor (esto es una aproximación)
# -----------------------
factor_premia = F.mean().values  # vector k
print("\nFactor premia (est):", dict(zip(F.columns, factor_premia.round(6))))

# -----------------------
# 6) Construir retornos esperados por APT: E[R_i] = alpha_i + beta_i * E[F]
#    (en este ejemplo usamos solo beta*factor_premia y descartamos alpha como 0 o la intercept)
# -----------------------
# si prefieres incluir intercept (alpha), podrías usar model.params['const']
expected_returns = betas.values.dot(factor_premia)  # shape (n_assets,)
expected_returns = pd.Series(expected_returns, index=tickers)
print("\nExpected returns (APT est):")
print(expected_returns.sort_values(ascending=False).round(4))

# -----------------------
# 7) Estimación de covarianzas: descomposición en factor y residual
#    Sigma = B Var(F) B' + Var(eps) (diag)
# -----------------------
B = betas.values  # (n_assets x k)
CovF = np.cov(F.values.T, ddof=1)  # (k x k)
# residual variances:
resid_var = residuals.var(ddof=1).values
Sigma = B.dot(CovF).dot(B.T) + np.diag(resid_var)

Sigma = pd.DataFrame(Sigma, index=tickers, columns=tickers)

# -----------------------
# 8) Optimización de portafolio: Min Var para un objetivo de retorno (long-only)
# -----------------------
w = cp.Variable(len(tickers))
mu = expected_returns.values
Sigma_cvx = Sigma.values

ret_target = 0.005  # objetivo retorno mensual (ajusta según horizonte)
prob = cp.Problem(cp.Minimize(cp.quad_form(w, Sigma_cvx)),
                  [cp.sum(w) == 1,
                   mu @ w >= ret_target,
                   w >= 0])   # long-only

prob.solve(solver=cp.SCS, verbose=False)   # prueba otros solvers si prefieres
w_opt = pd.Series(np.array(w.value).flatten(), index=tickers)
print("\nPesos óptimos (Min-Var con objetivo de retorno):")
print(w_opt[w_opt>1e-4].sort_values(ascending=False).round(4))

# -----------------------
# 9) Risk decomposition por factores para el portafolio
#    Var_port = w' Sigma w
#    Var_from_factors = w' B CovF B' w
#    Var_idiosyncratic = w' Diag(resid_var) w
#    Contribucion por factor j: (w' B_j)^2 * Var(F_j) ? (ver nota abajo)
# -----------------------
wvec = w_opt.values.reshape(-1,1)
var_total = float(wvec.T.dot(Sigma.values).dot(wvec))
var_factors = float(wvec.T.dot(B.dot(CovF).dot(B.T)).dot(wvec))
var_idio = float(wvec.T.dot(np.diag(resid_var)).dot(wvec))
print(f"\nVar total del portafolio (mensual): {var_total:.6f}")
print(f"Var por factores: {var_factors:.6f}, Var idiosincrática: {var_idio:.6f}")

# Contribuciones por factor (aproximación lineal):
# contrib_j = (w' B_j)^2 * Var(F_j)  (no es la única fórmula, pero sirve como insight)
factor_contrib = {}
for j in range(B.shape[1]):
    bj = B[:, j].reshape(-1,1)
    contrib_j = float((wvec.T.dot(bj))**2 * CovF[j, j])
    factor_contrib[f"F{j+1}"] = contrib_j
print("\nContribución aproximada por factor (var units):")
for kf, v in factor_contrib.items():
    print(f" {kf}: {v:.6f}")

# -----------------------
# 10) Stress test: chocar factores +/- 2 sigma y ver impacto en portafolio returns
# -----------------------
F_std = F.std()
shock = 2.0  # sigma
shocks = {"up": (F_std * shock).values, "down": -(F_std * shock).values}

for name, svec in shocks.items():
    # impacto aproximado en retorno = w' B svec
    impact = float(wvec.T.dot(B.dot(svec.reshape(-1,1))))
    print(f"\nShock {name} (+/-{shock} sigma) impacto estimado en retorno (mensual): {impact:.4f}")

# -----------------------
# Opcional: mostrar tabla resumen
# -----------------------
summary = pd.DataFrame({
    "ExpectedReturn(APT)": expected_returns,
    "Weight_opt": w_opt,
    "ResVar": resid_var
}).sort_values("Weight_opt", ascending=False)

print("\nResumen (top activos):")
print(summary.head(10).round(5))

# Fin script
