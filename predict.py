import numpy as np
import pandas as pd
from pymatgen.core import Composition
from matminer.featurizers.composition import ElementProperty
from sklearn.ensemble import RandomForestRegressor

# ==========================================
# 메인 실행 구문 보호 (Multiprocessing 에러 방지)
# ==========================================
if __name__ == '__main__':

    # 1. 원소 데이터 세팅
    element_d_centers = {
        'Cu': -2.67, 'Ni': -1.29, 'Co': -1.17, 'Mn': -0.80,
        'Zn': -7.50, 'Sn': -5.00, 'Fe': -0.92, 'Cr': -0.45,
        'Ti': 0.10,  'V': -0.15,  'Zr': 0.50,  'Nb': 0.30,
        'Ta': 0.40,  'W': -0.20,  'Mo': -0.30, 'Ag': -4.30,
        'Au': -3.80, 'Pd': -1.83, 'Pt': -2.25
    }

    # 2. 학습 데이터셋 1000개 생성
    np.random.seed(42)
    train_formulas = []
    train_targets = []
    elements = list(element_d_centers.keys())

    for _ in range(1000):
        n_elems = np.random.randint(4, 7)
        selected_elems = np.random.choice(elements, size=n_elems, replace=False)
        weights = np.random.dirichlet(np.ones(n_elems))
        comp_dict = {elem: round(w, 3) for elem, w in zip(selected_elems, weights)}
        
        comp = Composition(comp_dict)
        target_d_center = sum(comp_dict[e] * element_d_centers[e] for e in comp_dict)
        
        train_formulas.append(comp)
        train_targets.append(target_d_center)

    df_train = pd.DataFrame({'composition': train_formulas, 'target_d_center': train_targets})

    # 3. Matminer Feature 추출
    print("Extracting Magpie features using Matminer...")
    featurizer = ElementProperty.from_preset("magpie")

    # ignore_errors=True 옵션을 주면 이상한 화학식 처리 시 진행 중단 방지
    df_feat = featurizer.featurize_dataframe(df_train, col_id='composition', ignore_errors=True)

    print(df_feat)
    
    # 4. Feature 및 Target 분리
    X_train = df_feat.drop(columns=['composition', 'target_d_center']).values
    y_train = df_feat['target_d_center'].values

    # 5. ML 모델 학습 및 예측
    print("Training RandomForestRegressor model...")
    my_trained_model = RandomForestRegressor(n_estimators=100, random_state=42)
    my_trained_model.fit(X_train, y_train)

    # 6. 테스트 대상 Ga-Free HEA 예측
    formulas = [
    'Cu40Ni20Co5Mn5Zn20Sn10',
    'Cu40Ni15Co10Mn5Zn20Sn10',
    'Cu40Ni10Co15Mn5Zn20Sn10',
    'Cu40Ni5Co20Mn5Zn20Sn10',
    'Cu40Ni15Co5Mn10Zn20Sn10',
    'Cu40Ni10Co10Mn10Zn20Sn10',
    'Cu40Ni5Co15Mn10Zn20Sn10',
    'Cu40Ni10Co5Mn15Zn20Sn10',
    'Cu40Ni5Co10Mn15Zn20Sn10',
    'Cu35Ni20Co15Zn20Sn10'
    ]
    for i in range(len(formulas)):
        target_composition_str = formulas[i]
        target_comp = Composition(target_composition_str)
        target_feature = featurizer.featurize(target_comp)

        predicted_d_center = my_trained_model.predict([target_feature])[0]

        print(f"\nTarget Composition : {target_composition_str}")
        print(f"Predicted d-band center : {predicted_d_center:.3f} eV")