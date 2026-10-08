import numpy as np
import pandas as pd
from itertools import combinations, product

# 원소 확장
ELEMENTS = {
    'Cu': {'VEC': 11, 'r': 1.28, 'd_center': -2.67},
    'Ni': {'VEC': 10, 'r': 1.24, 'd_center': -1.29},
    'Co': {'VEC': 9,  'r': 1.25, 'd_center': -1.17},
    'Mn': {'VEC': 7,  'r': 1.27, 'd_center': -0.80},
    'Zn': {'VEC': 12, 'r': 1.34, 'd_center': -7.50},  #  (d-band center 하강 핵심)
    'Sn': {'VEC': 14, 'r': 1.45, 'd_center': -5.00}  
}

# Miedema Pairwise Enthalpy Matrix (kJ/mol) 
DH_MIX = {
    ('Cu','Ni'): 4,  ('Cu','Co'): 6,  ('Cu','Mn'): 4,  ('Cu','Zn'): 1,  ('Cu','Sn'): -7,
    ('Ni','Co'): 0,  ('Ni','Mn'): -8, ('Ni','Zn'): -2, ('Ni','Sn'): -4,
    ('Co','Mn'): -5, ('Co','Zn'): -5, ('Co','Sn'): -5,
    ('Mn','Zn'): -8, ('Mn','Sn'): -8,
    ('Zn','Sn'): 1
}

def get_dh_mix(e1, e2):
    if e1 == e2: return 0
    return DH_MIX.get((e1, e2)) or DH_MIX.get((e2, e1), 0)


def run_hea_screening_no_ga():
    all_elems = list(ELEMENTS.keys())
    results = []

    # 5원계 및 6원계 조합
    for n_elements in [5, 6]:
        for elem_sub in combinations(all_elems, n_elements):
            grid = np.linspace(0.05, 0.40, 8) 
            for p in product(grid, repeat=n_elements):
                if np.isclose(sum(p), 1.0):
                    comp = dict(zip(elem_sub, p))
                    #frules
                    # 1. Sn > 10%: 소결 시 저융점 상 형성 및 취성 유발 차단
                    # 2. Zn > 20%: 고온 소결 시 증기압(휘발성) 문제 억제
                    # 3. Cu < 20%: 자성 완전 차단 및 d-band center 기본 틀 유지
                    if comp.get('Sn', 0) > 0.10 or comp.get('Zn', 0) > 0.20:
                        continue
                    if comp.get('Cu', 0) < 0.20:
                        continue

                    # 물성 지표 계산
                    vec = sum(comp[e] * ELEMENTS[e]['VEC'] for e in elem_sub)
                    s_mix = -sum(comp[e] * np.log(comp[e]) for e in elem_sub)
                    r_avg = sum(comp[e] * ELEMENTS[e]['r'] for e in elem_sub)
                    delta = np.sqrt(sum(comp[e] * (1 - ELEMENTS[e]['r'] / r_avg)**2 for e in elem_sub)) * 100

                    dh_mix = sum(4 * get_dh_mix(elem_sub[i], elem_sub[j]) * comp[elem_sub[i]] * comp[elem_sub[j]]
                                 for i in range(n_elements) for j in range(i + 1, n_elements))

                    d_center = sum(comp[e] * ELEMENTS[e]['d_center'] for e in elem_sub)

                    # [진정 HEA 및 FCC 단상 필터]
                    if s_mix >= 1.5 and vec >= 8.5 and delta <= 6.6 and -15 <= dh_mix <= 5:
                        formula = " ".join([f"{k}{int(v*100)}" for k, v in comp.items()])
                        results.append({
                            'Formula': formula,
                            'Elements_N': n_elements,
                            'dS_mix/R': round(s_mix, 2),
                            'VEC': round(vec, 2),
                            'Delta_r (%)': round(delta, 2),
                            'dH_mix (kJ/mol)': round(dh_mix, 2),
                            'd_band_center (eV)': round(d_center, 3)
                        })

    df = pd.DataFrame(results)
    return df.sort_values(by='d_band_center (eV)', ascending=True).drop_duplicates(subset=['Formula'])

# 실행 및 결과 정렬
df_hea_no_ga = run_hea_screening_no_ga()
print("=== Top 10 HEA Candidate Compositions for YBCO Wire ===")
print(df_hea_no_ga.head(10).to_string(index=False))