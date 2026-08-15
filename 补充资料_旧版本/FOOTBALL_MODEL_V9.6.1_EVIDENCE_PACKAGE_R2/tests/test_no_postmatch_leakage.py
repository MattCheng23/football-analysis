def test_prematch_columns():
    with open('D:/Cola/FOOTBALL_MODEL_V9.6.1_EVIDENCE_PACKAGE_R2/data/ARCHIVED_PREMATCH_PREDICTIONS_LAST50.csv', encoding='utf-8') as f:
        cols = f.readline().strip().split(',')
        assert 'result_1x2' not in cols and 'home_goals' not in cols
